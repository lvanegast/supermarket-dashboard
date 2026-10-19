"""Executive Overview Dashboard Page."""
import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.theme import load_css
from src.data.db import (
    load_data,
    calculate_kpis,
    calculate_previous_period,
    format_delta_pct,
)
from src.components.filters import render_sidebar_filters
from src.components.kpi_card import render_kpi_card, render_insight_callout
from src.components.charts import (
    plot_revenue_trend,
    plot_category_margin_bar,
    plot_customer_distribution_donuts,
    plot_sales_heatmap,
)


def render_overview_page():
    load_css()
    df_raw = load_data()

    if df_raw.empty:
        st.error("No se encontraron datos en la base de datos.")
        return

    df, filters = render_sidebar_filters(df_raw)

    if df.empty:
        st.warning("No hay registros para la combinación de filtros seleccionada.")
        return

    # Executive Header
    st.markdown(
        f"""
        <div class="executive-header">
            <div class="executive-header-left">
                <h1>Panel Ejecutivo de Ventas & Rendimiento</h1>
                <p>Monitoreo en tiempo real de transacciones, margen comercial y comportamiento de sucursales</p>
            </div>
            <div>
                <span class="badge-status">Motor OLAP DuckDB Activo</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Calculate KPIs
    kpis = calculate_kpis(df)
    prev_df, comp_label = calculate_previous_period(
        df_raw, filters["start_date"], filters["end_date"],
        {"Branch": filters["branches"], "Product line": filters["products"]}
    )
    prev_kpis = calculate_kpis(prev_df) if not prev_df.empty else None

    # Delta calculations
    sales_delta, s_status = format_delta_pct(kpis["total_sales"], prev_kpis["total_sales"] if prev_kpis else None)
    tx_delta, t_status = format_delta_pct(kpis["transactions"], prev_kpis["transactions"] if prev_kpis else None)
    profit_delta, p_status = format_delta_pct(kpis["total_profit"], prev_kpis["total_profit"] if prev_kpis else None)
    ticket_delta, tk_status = format_delta_pct(kpis["avg_ticket"], prev_kpis["avg_ticket"] if prev_kpis else None)

    # Sparkline trends for KPIs
    daily_group = df.groupby(pd.Grouper(key="Date", freq="D"))
    sales_spark = daily_group["Sales"].sum().fillna(0).tolist()
    tx_spark = daily_group["Sales"].count().fillna(0).tolist()
    profit_spark = daily_group["gross income"].sum().fillna(0).tolist()
    ticket_spark = (daily_group["Sales"].sum() / daily_group["Sales"].count().replace(0, 1)).fillna(0).tolist()

    # Top KPI Row (Responsive Horizontal Container as per Streamlit dashboards.md)
    with st.container(horizontal=True):
        render_kpi_card(
            "Ventas totales",
            f"${kpis['total_sales']:,.2f}",
            icon=":material/payments:",
            delta_str=sales_delta,
            delta_status=s_status,
            subtitle=comp_label,
            chart_data=sales_spark,
            chart_type="area",
        )
        render_kpi_card(
            "Transacciones",
            f"{kpis['transactions']:,}",
            icon=":material/receipt_long:",
            delta_str=tx_delta,
            delta_status=t_status,
            subtitle=comp_label,
            chart_data=tx_spark,
            chart_type="line",
        )
        render_kpi_card(
            "Ganancia bruta",
            f"${kpis['total_profit']:,.2f}",
            icon=":material/trending_up:",
            delta_str=profit_delta,
            delta_status=p_status,
            subtitle=comp_label,
            chart_data=profit_spark,
            chart_type="area",
        )
        render_kpi_card(
            "Ticket promedio",
            f"${kpis['avg_ticket']:.2f}",
            icon=":material/confirmation_number:",
            delta_str=ticket_delta,
            delta_status=tk_status,
            subtitle=comp_label,
            chart_data=ticket_spark,
            chart_type="line",
        )

    # Secondary KPI Row
    with st.container(horizontal=True):
        render_kpi_card(
            "Margen promedio",
            f"{kpis['avg_margin']:.1f}%",
            icon=":material/bar_chart:",
        )
        render_kpi_card(
            "Calificación promedio",
            f"{kpis['avg_rating']:.2f} / 10",
            icon=":material/star:",
        )
        render_kpi_card(
            "Unidades vendidas",
            f"{kpis['units_sold']:,}",
            icon=":material/inventory_2:",
        )
        render_kpi_card(
            "Sucursales activas",
            f"{kpis['branches_count']}",
            icon=":material/store:",
        )

    # Automated Dynamic Insight
    best_branch = df.groupby("Branch")["Sales"].sum().idxmax()
    best_branch_sales = df.groupby("Branch")["Sales"].sum().max()
    best_category = df.groupby("Product line")["Sales"].sum().idxmax()
    
    render_insight_callout(
        title="Diagnóstico Ejecutivo Automatizado",
        message=(
            f"La sucursal líder del período es <b>{best_branch}</b> con <b>${best_branch_sales:,.2f}</b> en ventas totales. "
            f"La línea de mayor demanda es <b>{best_category}</b>, manteniendo un margen comercial saludable "
            f"del {kpis['avg_margin']:.1f}%. El comportamiento de compra refleja alta fidelidad en clientes Miembro."
        ),
        icon="⚡",
    )

    # Revenue Evolution
    with st.container(border=True):
        col_ctrl1, col_ctrl2 = st.columns([1, 1])
        with col_ctrl1:
            freq_opt = st.segmented_control("Agrupación temporal", ["Diaria", "Semanal"], default="Diaria")
        with col_ctrl2:
            branch_split = st.checkbox("Desglosar por sucursal", value=False)

        trend_freq = "Daily" if freq_opt == "Diaria" else "Weekly"
        fig_trend = plot_revenue_trend(df, freq=trend_freq, by_branch=branch_split)
        st.plotly_chart(fig_trend, width="stretch", alt="Evolución de ventas en el tiempo")

    # Category and Customer Breakdown
    col_cat, col_donuts = st.columns([1.1, 0.9])
    with col_cat:
        with st.container(border=True):
            fig_cat = plot_category_margin_bar(df)
            st.plotly_chart(fig_cat, width="stretch", alt="Ventas y margen por categoría")

    with col_donuts:
        with st.container(border=True):
            fig_cust, fig_pay = plot_customer_distribution_donuts(df)
            sub_t1, sub_t2 = st.tabs(["👥 Segmento cliente", "💳 Medio de pago"])
            with sub_t1:
                st.plotly_chart(fig_cust, width="stretch", alt="Participación de clientes")
            with sub_t2:
                st.plotly_chart(fig_pay, width="stretch", alt="Canales de pago")

    # Commercial Heatmap
    with st.container(border=True):
        st.markdown("### 🔥 Mapa de calor: intensidad de ventas por hora y día")
        hm_mode = st.segmented_control("Cálculo de intensidad", ["Total", "Promedio"], default="Total")
        fig_hm = plot_sales_heatmap(df, metric=hm_mode)
        st.plotly_chart(fig_hm, width="stretch", alt="Mapa de calor de ventas por hora y día")


if __name__ == "__main__" or "page" in __name__:
    render_overview_page()
