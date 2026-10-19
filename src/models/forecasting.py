"""Time-series Demand Forecasting and Inventory Safety Stock models."""
import math
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.core.config import COLORS
from src.core.theme import apply_theme

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


def generate_demand_forecast(
    df: pd.DataFrame,
    horizon_days: int = 30,
    confidence_level: float = 0.95,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Forecast future daily sales using Exponential Smoothing with fallback to trend projection."""
    # Daily aggregation
    daily = df.groupby(pd.Grouper(key="Date", freq="D"))["Sales"].sum().reset_index()
    daily = daily.set_index("Date").asfreq("D", fill_value=0.0)

    if len(daily) < 10:
        return pd.DataFrame(), {"error": "Insuficientes datos temporales para pronóstico."}

    y = daily["Sales"]
    forecast_dates = pd.date_range(start=daily.index[-1] + pd.Timedelta(days=1), periods=horizon_days, freq="D")

    forecast_values = []
    lower_bound = []
    upper_bound = []

    model_used = "Linear Trend + 7-Day Seasonality"

    if STATSMODELS_AVAILABLE and len(daily) >= 14:
        try:
            # Fit Holt-Winters with additive trend and additive 7-day weekly seasonality
            hw_model = ExponentialSmoothing(
                y,
                trend="add",
                seasonal="add",
                seasonal_periods=7,
                initialization_method="estimated",
            ).fit()
            pred = hw_model.forecast(horizon_days)
            forecast_values = pred.values
            residuals = y - hw_model.fittedvalues
            std_res = np.std(residuals)
            model_used = "Holt-Winters Exponential Smoothing (Trend + Seasonality)"
        except Exception:
            # Fallback
            forecast_values = None
    else:
        forecast_values = None

    if forecast_values is None:
        # Robust statistical baseline: 7-day rolling mean + linear drift
        rolling_7 = y.rolling(7, min_periods=1).mean()
        trend_slope = (rolling_7.iloc[-1] - rolling_7.iloc[0]) / len(rolling_7)
        base_level = rolling_7.iloc[-1]
        
        # Day of week seasonality factors
        dow_factor = y.groupby(y.index.dayofweek).mean()
        overall_mean = y.mean() or 1.0
        dow_multipliers = (dow_factor / overall_mean).to_dict()

        preds = []
        for i, dt in enumerate(forecast_dates):
            dow = dt.dayofweek
            val = (base_level + trend_slope * (i + 1)) * dow_multipliers.get(dow, 1.0)
            preds.append(max(0.0, float(val)))
        forecast_values = np.array(preds)
        std_res = float(np.std(y))

    # Compute confidence intervals (Z-score 1.96 for 95%)
    z_score = 1.96 if confidence_level >= 0.95 else 1.64
    for i, val in enumerate(forecast_values):
        # Uncertainty expands slightly with forecast horizon
        uncertainty = z_score * std_res * math.sqrt(1 + 0.05 * i)
        lower_bound.append(max(0.0, val - uncertainty))
        upper_bound.append(val + uncertainty)

    forecast_df = pd.DataFrame({
        "Date": forecast_dates,
        "Forecast": forecast_values,
        "Lower_Bound": lower_bound,
        "Upper_Bound": upper_bound,
    })

    # Summary metrics
    expected_total_revenue = float(forecast_values.sum())
    daily_avg_expected = float(forecast_values.mean())
    growth_vs_history = ((daily_avg_expected - y.mean()) / (y.mean() or 1.0)) * 100

    metrics = {
        "model_used": model_used,
        "horizon_days": horizon_days,
        "expected_revenue": expected_total_revenue,
        "daily_avg_expected": daily_avg_expected,
        "growth_pct": growth_vs_history,
        "historical_volatility": float(std_res),
    }

    return forecast_df, metrics


def calculate_safety_stock_matrix(df: pd.DataFrame, lead_time_days: int = 7) -> pd.DataFrame:
    """Calculate Safety Stock, Reorder Point (ROP), and Stockout Risk by Product Line."""
    results = []

    daily_prod = (
        df.groupby(["Product line", pd.Grouper(key="Date", freq="D")])["Quantity"]
        .sum()
        .reset_index()
    )

    for prod_line, group in daily_prod.groupby("Product line"):
        mean_daily_demand = group["Quantity"].mean()
        std_daily_demand = group["Quantity"].std()
        if pd.isna(std_daily_demand):
            std_daily_demand = mean_daily_demand * 0.25

        # Service Level 95% -> Z = 1.65
        z = 1.65
        safety_stock = z * std_daily_demand * math.sqrt(lead_time_days)
        lead_time_demand = mean_daily_demand * lead_time_days
        reorder_point = lead_time_demand + safety_stock

        # Volatility coefficient of variation (CV)
        cv = (std_daily_demand / mean_daily_demand) if mean_daily_demand > 0 else 0
        risk_level = "Alto" if cv > 0.8 else ("Medio" if cv > 0.4 else "Bajo")

        results.append({
            "Línea de Producto": prod_line,
            "Demanda Diaria Promedio": round(mean_daily_demand, 1),
            "Desviación Estándar": round(std_daily_demand, 1),
            "Demanda Lead Time (7d)": round(lead_time_demand, 0),
            "Stock de Seguridad (SS)": math.ceil(safety_stock),
            "Punto de Reorden (ROP)": math.ceil(reorder_point),
            "Riesgo de Quiebre": risk_level,
        })

    return pd.DataFrame(results).sort_values("Punto de Reorden (ROP)", ascending=False)


def plot_forecast_chart(daily_history: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Plot historical sales combined with forecast and confidence bands."""
    fig = go.Figure()

    # History (last 45 days for clarity)
    hist_tail = daily_history.tail(45)
    fig.add_trace(
        go.Scatter(
            x=hist_tail["Date"],
            y=hist_tail["Sales"],
            name="Ventas Históricas",
            mode="lines+markers",
            line=dict(color=COLORS["text_secondary"], width=2),
            marker=dict(size=4),
        )
    )

    # Upper and Lower confidence bounds
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Upper_Bound"],
            name="Límite Superior (95%)",
            mode="lines",
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Lower_Bound"],
            name="Intervalo de Confianza (95%)",
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(99, 102, 241, 0.15)",
        )
    )

    # Forecast
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Forecast"],
            name="Pronóstico IA",
            mode="lines+markers",
            line=dict(color=COLORS["emerald"], width=3, dash="solid"),
            marker=dict(size=5, color=COLORS["emerald_light"]),
        )
    )

    fig.update_layout(
        title="Proyección de Demanda e Intervalos de Confianza (Próximos Días)",
        xaxis_title="Fecha",
        yaxis_title="Ventas Estimadas ($)",
    )
    return apply_theme(fig)
