"""Executive Overview Dashboard Page - Modernized Dynamic Retail Intelligence."""
import sys
from pathlib import Path
from datetime import timedelta

import pandas as pd
import streamlit as st

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
    plot_capital_flow_sankey,
    plot_branch_radar_benchmark,
    plot_target_gauge,
)

# 1. Page Setup & Styling
load_css()
df_raw = load_data()

if df_raw.empty:
    st.error("No se encontraron registros en la base de datos.")
    st.stop()

# 2. Sidebar Filters
df_filtered, filters = render_sidebar_filters(df_raw)

if df_filtered.empty:
    st.warning("No hay registros que coincidan con la combinación de filtros.")
    st.stop()

# 3. Dynamic Quick Horizon Selector (Top Control Bar)
col_title, col_quick = st.columns([1.4, 1.0], vertical_alignment="center")

with col_title:
    st.title("Panel Ejecutivo de Operaciones")
    st.caption("Inteligencia comercial, análisis de rentabilidad y benchmark dinámico de sucursales")

with col_quick:
    quick_preset = st.pills(
        "Horizonte temporal rápido",
        options=["Todo el período", "Últimos 60 días", "Últimos 30 días", "Últimos 14 días"],
        default="Todo el período",
        selection_mode="single",
        label_visibility="collapsed",
    )

# Apply Quick Horizon Filter if selected
df = df_filtered.copy()
max_dataset_date = df["Date"].max()

if quick_preset == "Últimos 14 días":
    cutoff = max_dataset_date - timedelta(days=14)
    df = df[df["Date"] >= cutoff]
elif quick_preset == "Últimos 30 días":
    cutoff = max_dataset_date - timedelta(days=30)
    df = df[df["Date"] >= cutoff]
elif quick_preset == "Últimos 60 días":
    cutoff = max_dataset_date - timedelta(days=60)
    df = df[df["Date"] >= cutoff]

if df.empty:
    st.warning("No hay datos disponibles en el rango temporal seleccionado.")
    st.stop()

# 4. KPI Calculations & Delta Comparison
kpis = calculate_kpis(df)
curr_start = df["Date"].min().date()
curr_end = df["Date"].max().date()

prev_df, comp_label = calculate_previous_period(
    df_raw,
    curr_start,
    curr_end,
    {"Branch": filters.get("branches", []), "Product line": filters.get("products", [])},
)
prev_kpis = calculate_kpis(prev_df) if not prev_df.empty else None

sales_delta, s_status = format_delta_pct(kpis["total_sales"], prev_kpis["total_sales"] if prev_kpis else None)
tx_delta, t_status = format_delta_pct(kpis["transactions"], prev_kpis["transactions"] if prev_kpis else None)
profit_delta, p_status = format_delta_pct(kpis["total_profit"], prev_kpis["total_profit"] if prev_kpis else None)
ticket_delta, tk_status = format_delta_pct(kpis["avg_ticket"], prev_kpis["avg_ticket"] if prev_kpis else None)

# Sparkline series
daily_group = df.groupby(pd.Grouper(key="Date", freq="D"))
sales_spark = daily_group["Sales"].sum().fillna(0).tolist()
tx_spark = daily_group["Sales"].count().fillna(0).tolist()
profit_spark = daily_group["gross income"].sum().fillna(0).tolist()
ticket_spark = (daily_group["Sales"].sum() / daily_group["Sales"].count().replace(0, 1)).fillna(0).tolist()

# 5. Primary Executive KPI Row (Horizontal container with sparklines)
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

# 6. Operational Targets & Efficiency Row
with st.container(horizontal=True):
    render_kpi_card(
        "Margen bruto promedio",
        f"{kpis['avg_margin']:.1f}%",
        icon=":material/percent:",
        help_text="Margen sobre costo estipulado para la cadena",
    )
    render_kpi_card(
        "Índice de satisfacción",
        f"{kpis['avg_rating']:.2f} / 10",
        icon=":material/star:",
        help_text="Puntuación promedio de NPS y satisfacción directa",
    )
    render_kpi_card(
        "Unidades vendidas",
        f"{kpis['units_sold']:,}",
        icon=":material/inventory_2:",
    )
    render_kpi_card(
        "Sucursales operativas",
        f"{kpis['branches_count']}",
        icon=":material/store:",
    )

# 7. Automated Dynamic Insight & Operational Pacing
top_branch = df.groupby("Branch")["Sales"].sum().idxmax()
top_branch_sales = df.groupby("Branch")["Sales"].sum().max()
top_prod = df.groupby("Product line")["Sales"].sum().idxmax()

render_insight_callout(
    title="Diagnóstico Ejecutivo Automatizado",
    message=(
        f"La sucursal con mayor tracción es **{top_branch}** generando **${top_branch_sales:,.2f}** en facturación. "
        f"La línea líder en demanda es **{top_prod}**, sosteniendo un margen promedio del **{kpis['avg_margin']:.1f}%**. "
        f"Se han procesado **{kpis['transactions']:,}** órdenes con un ticket promedio de **${kpis['avg_ticket']:.2f}**."
    ),
    icon=":material/bolt:",
)

# 8. Interactive Analytical Workspaces (Structured Modern Tabs)
tab_flow, tab_benchmark, tab_commercial, tab_heatmap = st.tabs([
    "📈 Tendencias & Flujo de Capital",
    "🏪 Benchmark de Sucursales",
    "🛒 Desempeño Comercial & Segmentos",
    "🔥 Intensidad Horaria & Días",
])

# TAB 1: Tendencias & Flujo de Capital
with tab_flow:
    with st.container(border=True):
        col_ctrl1, col_ctrl2 = st.columns([1, 1], vertical_alignment="center")
        with col_ctrl1:
            freq_choice = st.segmented_control(
                "Agrupación temporal",
                options=["Diaria", "Semanal"],
                default="Diaria",
            )
        with col_ctrl2:
            split_branches = st.checkbox("Desglosar curvas por sucursal", value=False)

        trend_freq = "Daily" if freq_choice == "Diaria" else "Weekly"
        fig_trend = plot_revenue_trend(df, freq=trend_freq, by_branch=split_branches)
        st.plotly_chart(fig_trend, width="stretch", alt="Curva de ingresos temporales")

    with st.container(border=True):
        st.subheader("Flujo de Capital Comercial")
        st.caption("Trazabilidad completa: Desde la sucursal de origen hasta el canal de recaudación")
        fig_sankey = plot_capital_flow_sankey(df)
        st.plotly_chart(fig_sankey, width="stretch", alt="Diagrama de flujo de capital Sankey")

# TAB 2: Benchmark de Sucursales
with tab_benchmark:
    col_radar, col_gauge = st.columns([1.3, 0.7])
    with col_radar:
        with st.container(border=True):
            fig_radar = plot_branch_radar_benchmark(df)
            st.plotly_chart(fig_radar, width="stretch", alt="Radar benchmark de sucursales")

    with col_gauge:
        with st.container(border=True):
            st.markdown("##### Cumplimiento de Metas")
            st.plotly_chart(
                plot_target_gauge(
                    current_val=round(kpis["avg_margin"], 2),
                    target_val=5.0,
                    title="Margen Bruto",
                    suffix="%",
                    max_range=10.0,
                ),
                width="stretch",
                alt="Medidor de cumplimiento de margen",
            )
            st.plotly_chart(
                plot_target_gauge(
                    current_val=round(kpis["avg_rating"], 2),
                    target_val=7.5,
                    title="Calificación Promedio",
                    suffix=" ⭐",
                    max_range=10.0,
                ),
                width="stretch",
                alt="Medidor de calificación de clientes",
            )

    # Leaderboard Table with In-Cell Sparklines & Progress Columns
    with st.container(border=True):
        st.markdown("##### Ranking Detallado y Tendencia por Sucursal")
        
        branch_summary = df.groupby("Branch").agg(
            Ventas=("Sales", "sum"),
            Margen=("gross income", "sum"),
            Transacciones=("Invoice ID", "count"),
            Satisfaccion=("Rating", "mean"),
        ).reset_index()

        branch_summary["Ticket Prom."] = branch_summary["Ventas"] / branch_summary["Transacciones"]

        # In-cell sparkline weekly trends
        branch_sparks = {}
        for b in branch_summary["Branch"]:
            b_trend = (
                df[df["Branch"] == b]
                .groupby(pd.Grouper(key="Date", freq="W"))["Sales"]
                .sum()
                .tolist()
            )
            branch_sparks[b] = b_trend

        branch_summary["Tendencia Semanal"] = branch_summary["Branch"].map(branch_sparks)

        st.dataframe(
            branch_summary,
            column_config={
                "Branch": st.column_config.TextColumn("Sucursal", help="Identificador de la sucursal"),
                "Ventas": st.column_config.ProgressColumn(
                    "Ventas Totales ($)",
                    format="$%,.2f",
                    min_value=0,
                    max_value=float(branch_summary["Ventas"].max() * 1.05),
                ),
                "Margen": st.column_config.NumberColumn("Ganancia Bruta ($)", format="$%,.2f"),
                "Transacciones": st.column_config.NumberColumn("Tickets Emitidos", format="%d"),
                "Ticket Prom.": st.column_config.NumberColumn("Ticket Promedio", format="$%.2f"),
                "Satisfaccion": st.column_config.NumberColumn("Calificación Promedio", format="%.2f ⭐"),
                "Tendencia Semanal": st.column_config.AreaChartColumn("Tendencia Semanal", width="medium"),
            },
            hide_index=True,
            width="stretch",
        )

# TAB 3: Desempeño Comercial & Segmentos
with tab_commercial:
    col_prod, col_dist = st.columns([1.1, 0.9])
    with col_prod:
        with st.container(border=True):
            fig_cat = plot_category_margin_bar(df)
            st.plotly_chart(fig_cat, width="stretch", alt="Ventas y margen por categoría")

    with col_dist:
        with st.container(border=True):
            fig_cust, fig_pay = plot_customer_distribution_donuts(df)
            sub_t1, sub_t2 = st.tabs(["👥 Segmento de Clientes", "💳 Canales de Pago"])
            with sub_t1:
                st.plotly_chart(fig_cust, width="stretch", alt="Distribución de ventas por cliente")
            with sub_t2:
                st.plotly_chart(fig_pay, width="stretch", alt="Distribución de ventas por método de pago")

# TAB 4: Intensidad Horaria & Días
with tab_heatmap:
    with st.container(border=True):
        col_hm_title, col_hm_ctrl = st.columns([1.5, 1.0], vertical_alignment="center")
        with col_hm_title:
            st.markdown("##### Mapa de Calor: Flujo de Compras por Hora y Día")
            st.caption("Identificación de franjas horarias pico para optimización de personal y stock")
        with col_hm_ctrl:
            hm_mode = st.segmented_control("Cálculo de intensidad", ["Total", "Promedio"], default="Total")

        fig_hm = plot_sales_heatmap(df, metric=hm_mode)
        st.plotly_chart(fig_hm, width="stretch", alt="Mapa de calor comercial")
