"""Standardized, high-aesthetic Plotly charts for retail analytics."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.core.config import COLORS, PALETTE, COLORSCALE_MONEY, COLORSCALE_PROFIT
from src.core.theme import apply_theme


def plot_revenue_trend(df: pd.DataFrame, freq: str = "D", by_branch: bool = False) -> go.Figure:
    """Generate modern sales trend line chart."""
    freq_code = "D" if freq == "Daily" else "W"
    
    if by_branch:
        grouped = (
            df.groupby([pd.Grouper(key="Date", freq=freq_code), "Branch"])["Sales"]
            .sum()
            .reset_index()
        )
        fig = px.line(
            grouped,
            x="Date",
            y="Sales",
            color="Branch",
            title="Tendencia de Ventas por Sucursal",
            markers=True,
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(
            line=dict(width=2.5),
            marker=dict(size=5),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Venta: $%{y:,.2f}<extra></extra>",
        )
    else:
        grouped = (
            df.groupby(pd.Grouper(key="Date", freq=freq_code))["Sales"]
            .sum()
            .reset_index()
        )
        fig = px.area(
            grouped,
            x="Date",
            y="Sales",
            title="Evolución Temporal de Ingresos",
            markers=True,
        )
        fig.update_traces(
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=5, color=COLORS["primary_light"]),
            fillcolor="rgba(99, 102, 241, 0.12)",
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Ingresos: $%{y:,.2f}<extra></extra>",
        )

    return apply_theme(fig)


def plot_category_margin_bar(df: pd.DataFrame) -> go.Figure:
    """Create stacked or grouped category sales and profit comparison."""
    summary = (
        df.groupby("Product line")
        .agg(Ventas=("Sales", "sum"), Margen=("gross income", "sum"))
        .reset_index()
        .sort_values("Ventas", ascending=True)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=summary["Product line"],
            x=summary["Ventas"],
            name="Ventas Totales",
            orientation="h",
            marker=dict(
                color=COLORS["primary"],
                line=dict(color="rgba(255,255,255,0.1)", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Ventas: $%{x:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=summary["Product line"],
            x=summary["Margen"],
            name="Ganancia Bruta",
            orientation="h",
            marker=dict(
                color=COLORS["emerald"],
                line=dict(color="rgba(255,255,255,0.1)", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Ganancia: $%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        title=dict(text="Desempeño por Categoría: Ventas vs Margen Bruto"),
        xaxis_title="Monto ($)",
        yaxis_title="",
    )
    return apply_theme(fig)


def plot_customer_distribution_donuts(df: pd.DataFrame):
    """Return two donut charts: Customer Type and Payment Method."""
    # 1. Customer Type
    ctype = df.groupby("Customer type")["Sales"].sum().reset_index()
    fig_cust = px.pie(
        ctype,
        names="Customer type",
        values="Sales",
        hole=0.6,
        title="Participación: Miembro vs Normal",
        color_discrete_sequence=[COLORS["primary"], COLORS["emerald"]],
    )
    fig_cust.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#0B0F19", width=2)),
        hovertemplate="<b>%{label}</b>: $%{value:,.2f} (%{percent})<extra></extra>",
    )
    apply_theme(fig_cust)

    # 2. Payment Method
    payment = df.groupby("Payment")["Sales"].sum().reset_index()
    fig_pay = px.pie(
        payment,
        names="Payment",
        values="Sales",
        hole=0.6,
        title="Canales de Pago",
        color_discrete_sequence=[COLORS["primary_light"], COLORS["cyan"], COLORS["amber"]],
    )
    fig_pay.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#0B0F19", width=2)),
        hovertemplate="<b>%{label}</b>: $%{value:,.2f} (%{percent})<extra></extra>",
    )
    apply_theme(fig_pay)

    return fig_cust, fig_pay


def plot_sales_heatmap(df: pd.DataFrame, metric: str = "Total") -> go.Figure:
    """Create Day-of-Week x Hour sales intensity heatmap."""
    agg_func = "sum" if metric == "Total" else "mean"
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    pivot = (
        df.groupby(["DayName", "Hour"])["Sales"]
        .agg(agg_func)
        .reset_index()
    )
    pivot["DayName"] = pd.Categorical(pivot["DayName"], categories=days_order, ordered=True)
    pivot_table = pivot.pivot(index="DayName", columns="Hour", values="Sales").fillna(0)

    fig = px.imshow(
        pivot_table,
        labels=dict(x="Hora del Día", y="Día de la Semana", color=f"Ventas {metric} ($)"),
        aspect="auto",
        color_continuous_scale="Viridis",
        text_auto=".0f",
        title=f"Mapa de Calor de Intensidad Comercial ({metric})",
    )
    fig.update_xaxes(side="top")
    return apply_theme(fig)
