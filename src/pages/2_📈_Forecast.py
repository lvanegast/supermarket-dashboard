"""Demand Forecasting and Inventory Risk Analytics Page."""
import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.theme import load_css
from src.data.db import load_data
from src.components.filters import render_sidebar_filters
from src.components.kpi_card import render_kpi_card, render_insight_callout
from src.models.forecasting import (
    generate_demand_forecast,
    calculate_safety_stock_matrix,
    plot_forecast_chart,
)


def render_forecast_page():
    load_css()
    df_raw = load_data()

    if df_raw.empty:
        st.error("No se encontraron datos disponibles.")
        return

    df, filters = render_sidebar_filters(df_raw)

    st.markdown(
        """
        <div class="executive-header">
            <div class="executive-header-left">
                <h1>Pronóstico Predictivo de Demanda & Control de Stock</h1>
                <p>Modelado de series temporales, descomposición de estacionalidad y puntos de reorden de inventario</p>
            </div>
            <div>
                <span class="badge-status">Modelo ML Activo</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Control Bar
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            horizon = st.slider("Horizonte de pronóstico (días)", min_value=14, max_value=60, value=30, step=7)
        with col2:
            confidence_opt = st.segmented_control("Nivel de confianza", ["95%", "90%"], default="95%")
            confidence = 0.95 if confidence_opt == "95%" else 0.90
        with col3:
            lead_time = st.slider("Tiempo de reposición del proveedor (días)", 3, 14, 7)

    # Run Forecast Model
    daily_history = df.groupby(pd.Grouper(key="Date", freq="D"))["Sales"].sum().reset_index()
    forecast_df, metrics = generate_demand_forecast(df, horizon_days=horizon, confidence_level=confidence)

    if forecast_df.empty or "error" in metrics:
        st.warning(metrics.get("error", "No fue posible generar el pronóstico con los filtros actuales."))
        return

    # Forecast KPI cards
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card(
            f"Ventas proyectadas ({horizon}d)",
            f"${metrics['expected_revenue']:,.2f}",
            icon="🔮",
            delta_str=f"{metrics['growth_pct']:+.1f}% vs media histórica",
            delta_status="positive" if metrics['growth_pct'] >= 0 else "negative",
            theme_color="emerald",
        )
    with c2:
        render_kpi_card(
            "Venta diaria promedio proyectada",
            f"${metrics['daily_avg_expected']:,.2f}",
            icon="📅",
            theme_color="cyan",
        )
    with c3:
        render_kpi_card(
            "Algoritmo calibrado",
            metrics["model_used"].split("(")[0],
            icon="⚙️",
            subtitle="estacionalidad semanal activa",
            theme_color="primary",
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Main Forecast Plot
    with st.container(border=True):
        fig_f = plot_forecast_chart(daily_history, forecast_df)
        st.plotly_chart(fig_f, width="stretch", alt="Proyección de demanda futura")

    # Inventory Matrix
    with st.container(border=True):
        st.markdown("### 📦 Matriz de stock de seguridad y puntos de reorden (ROP)")
        st.caption("Cálculo estocástico basado en variabilidad de demanda por categoría y nivel de servicio del 95%.")

        safety_df = calculate_safety_stock_matrix(df, lead_time_days=lead_time)

        render_insight_callout(
            title="Recomendación de Compras y Suministro",
            message=(
                f"Para un tiempo de entrega de <b>{lead_time} días</b>, las líneas con mayor riesgo de quiebre "
                f"deben mantener un stock de seguridad mínimo de acuerdo al Punto de Reorden (ROP). "
                f"Cuando el inventario físico caiga por debajo del ROP, se debe emitir una orden de compra automática al proveedor."
            ),
            icon="🛡️",
        )

        st.dataframe(
            safety_df,
            width="stretch",
            alt="Matriz de stock de seguridad y reorden",
            column_config={
                "Línea de Producto": st.column_config.TextColumn("Categoría"),
                "Demanda Diaria Promedio": st.column_config.NumberColumn("Demanda Media/Día", format="%.1f uds"),
                "Stock de Seguridad (SS)": st.column_config.NumberColumn("Stock Seguridad (uds)", format="%d uds"),
                "Punto de Reorden (ROP)": st.column_config.ProgressColumn(
                    "Punto de Reorden (ROP)",
                    format="%d uds",
                    min_value=0,
                    max_value=int(safety_df["Punto de Reorden (ROP)"].max() * 1.15),
                ),
                "Riesgo de Quiebre": st.column_config.TextColumn("Nivel de Riesgo"),
            },
        )


if __name__ == "__main__" or "page" in __name__:
    render_forecast_page()
