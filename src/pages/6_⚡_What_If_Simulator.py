"""What-If Pricing, Discount, and Margin Simulation Page."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.theme import load_css, apply_theme
from src.core.config import COLORS
from src.data.db import load_data
from src.components.filters import render_sidebar_filters
from src.components.kpi_card import render_kpi_card, render_insight_callout


def render_what_if_page():
    load_css()
    df_raw = load_data()

    if df_raw.empty:
        st.error("No se encontraron datos.")
        return

    df, filters = render_sidebar_filters(df_raw)

    st.markdown(
        """
        <div class="executive-header">
            <div class="executive-header-left">
                <h1>Simulador de Escenarios Comerciales ("What-If")</h1>
                <p>Evalúa el impacto de descuentos, elasticidad de demanda y variaciones de costos antes de aplicarlos</p>
            </div>
            <div>
                <span class="badge-status">Simulador Financiero</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simulation Controls
    st.markdown("##### ⚙️ Parámetros de Simulación")
    c1, c2, c3 = st.columns(3)
    with c1:
        discount_pct = st.slider("Descuento Promocional Planeado (%)", min_value=0, max_value=30, value=10, step=1)
    with c2:
        elasticity = st.slider("Elasticidad Precio-Demanda (Volumen Adicional)", min_value=0.5, max_value=2.5, value=1.4, step=0.1)
    with c3:
        cogs_increase_pct = st.slider("Variación en Costo de Mercancía (COGS %)", min_value=-10, max_value=20, value=0, step=1)

    # Baseline calculations
    base_sales = float(df["Sales"].sum())
    base_cogs = float(df["cogs"].sum())
    base_profit = float(df["gross income"].sum())
    base_margin = float(df["gross margin percentage"].mean())

    # Simulation calculations
    # Price multiplier = 1 - discount
    # Volume multiplier = 1 + (discount * elasticity)
    price_factor = 1.0 - (discount_pct / 100.0)
    vol_factor = 1.0 + ((discount_pct / 100.0) * elasticity)
    cogs_factor = (1.0 + (cogs_increase_pct / 100.0)) * vol_factor

    sim_sales = base_sales * price_factor * vol_factor
    sim_cogs = base_cogs * cogs_factor
    sim_profit = sim_sales - sim_cogs
    sim_margin = (sim_profit / sim_sales * 100.0) if sim_sales > 0 else 0.0

    delta_profit = sim_profit - base_profit
    delta_sales = sim_sales - base_sales

    # KPI Comparison
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        render_kpi_card(
            "Ventas Proyectadas",
            f"${sim_sales:,.2f}",
            icon="💰",
            delta_str=f"{((sim_sales - base_sales)/base_sales)*100:+.1f}%",
            delta_status="positive" if delta_sales >= 0 else "negative",
            subtitle="vs ventas base",
            theme_color="primary",
        )
    with k2:
        render_kpi_card(
            "Ganancia Proyectada",
            f"${sim_profit:,.2f}",
            icon="📈",
            delta_str=f"${delta_profit:+,.2f}",
            delta_status="positive" if delta_profit >= 0 else "negative",
            subtitle="impacto en utilidad",
            theme_color="emerald" if delta_profit >= 0 else "rose",
        )
    with k3:
        render_kpi_card(
            "Margen Resultante",
            f"{sim_margin:.2f}%",
            icon="📊",
            delta_str=f"{sim_margin - base_margin:+.2f} pp",
            delta_status="positive" if (sim_margin - base_margin) >= 0 else "negative",
            subtitle="variación de margen",
            theme_color="amber",
        )
    with k4:
        render_kpi_card(
            "Incremento en Unidades",
            f"{(vol_factor - 1.0)*100:+.1f}%",
            icon="📦",
            subtitle=f"por elasticidad {elasticity}x",
            theme_color="cyan",
        )

    # Dynamic diagnostic recommendation
    if delta_profit > 0:
        render_insight_callout(
            title="Estrategia Comercial Favorable",
            message=(
                f"El descuento del {discount_pct}% genera un aumento neto de utilidad de <b>+${delta_profit:,.2f}</b> "
                f"gracias a la elasticidad de volumen (+{(vol_factor-1.0)*100:.1f}% en unidades). "
                f"La promoción es rentable y recomendada para dinamizar rotación de inventario."
            ),
            icon="✅",
        )
    else:
        render_insight_callout(
            title="Alerta de Destrucción de Margen",
            message=(
                f"Cuidado: El descuento propuesto genera una pérdida proyectada de <b>${delta_profit:,.2f}</b> "
                f"debido a que el incremento en volumen no compensa la caída en el precio unitario ni los costos de reposición. "
                f"Se recomienda un descuento menor (máx 5-8%) o un bundle condicionado."
            ),
            icon="⚠️",
        )

    # Comparison Bar Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Ventas ($)", "Costo Mercancía ($)", "Ganancia Bruta ($)"],
        y=[base_sales, base_cogs, base_profit],
        name="Escenario Actual",
        marker_color=COLORS["primary"],
        text=[f"${base_sales:,.0f}", f"${base_cogs:,.0f}", f"${base_profit:,.0f}"],
        textposition="auto",
    ))
    fig.add_trace(go.Bar(
        x=["Ventas ($)", "Costo Mercancía ($)", "Ganancia Bruta ($)"],
        y=[sim_sales, sim_cogs, sim_profit],
        name="Escenario Simulado",
        marker_color=COLORS["emerald"] if delta_profit >= 0 else COLORS["rose"],
        text=[f"${sim_sales:,.0f}", f"${sim_cogs:,.0f}", f"${sim_profit:,.0f}"],
        textposition="auto",
    ))
    fig.update_layout(
        barmode="group",
        title="Comparativo Financiero: Base vs Escenario Simulado",
    )
    with st.container(border=True):
        st.plotly_chart(fig, width="stretch", alt="Comparativo financiero base vs escenario simulado")


if __name__ == "__main__" or "page" in __name__:
    render_what_if_page()
