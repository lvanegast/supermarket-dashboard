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
        format_func=lambda x: {
            "Todo el período": "🌐 Todo",
            "Últimos 60 días": "📅 60D",
            "Últimos 30 días": "🗓️ 30D",
            "Últimos 14 días": "⚡ 14D",
        }.get(x, x),
        selection_mode="single",
        label_visibility="collapsed",
    )

# Apply Quick Horizon Filter if selected
df = df_filtered.copy()
max_dataset_date = df["Date"].max()

if quick_preset in ["Últimos 14 días", "14D"]:
    cutoff = max_dataset_date - timedelta(days=14)
    df = df[df["Date"] >= cutoff]
elif quick_preset in ["Últimos 30 días", "30D"]:
    cutoff = max_dataset_date - timedelta(days=30)
    df = df[df["Date"] >= cutoff]
elif quick_preset in ["Últimos 60 días", "60D"]:
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

top_branch = df.groupby("Branch")["Sales"].sum().idxmax()
top_branch_sales = df.groupby("Branch")["Sales"].sum().max()
top_prod = df.groupby("Product line")["Sales"].sum().idxmax()

# Interactive Action Toolbar
with st.container():
    c_bar_info, c_bar_refresh, c_bar_alerts, c_bar_download = st.columns(
        [1.6, 0.15, 0.15, 0.15], vertical_alignment="center"
    )
    with c_bar_info:
        st.markdown(
            f'<div class="badge-status-pulse"><div class="pulse-dot"></div> Sistema activo · Sucursal destacada: <b>{top_branch}</b> (${top_branch_sales:,.0f})</div>',
            unsafe_allow_html=True,
        )
    with c_bar_refresh:
        if st.button("", icon=":material/refresh:", help="Refrescar caché de datos y métricas", key="btn_refresh_exec"):
            st.cache_data.clear()
            st.toast("Datos y métricas actualizados", icon=":material/check_circle:")
            st.rerun()
    with c_bar_alerts:
        with st.popover("", icon=":material/bolt:", help="Alertas de rendimiento y anomalías en vivo"):
            st.markdown("#### Alertas de Rendimiento")
            st.caption("Monitoreo automatizado del período")
            st.divider()
            st.markdown(f"🚀 **Sucursal con mayor tracción:** **{top_branch}** (${top_branch_sales:,.2f})")
            st.markdown(f"⭐ **Línea líder:** **{top_prod}**")
            if s_status == "negative":
                st.warning(f"Ventas con tendencia a la baja vs período anterior ({sales_delta}).")
            else:
                st.success(f"Ritmo comercial positivo vs histórico ({sales_delta}).")
    with c_bar_download:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="",
            data=csv_bytes,
            file_name="supermarket_sales_executive.csv",
            mime="text/csv",
            icon=":material/download:",
            help="Descargar reporte actual en CSV",
            key="btn_download_exec",
        )

# Prepare Interactive Drilldown Payloads for KPIs
branch_sales = df.groupby("Branch")["Sales"].sum()
tot_s = kpis["total_sales"] or 1
sales_drilldown = {
    "title": "Desglose de Ventas",
    "subtitle": "Volumen y porcentaje por sucursal",
    "items": [
        (f"Sucursal {b} ({'Yangon' if b=='A' else 'Naypyitaw' if b=='B' else 'Mandalay'})", f"${val:,.2f}", f"{(val/tot_s)*100:.1f}%")
        for b, val in branch_sales.items()
    ],
    "stats": {
        "Venta media/día": f"${daily_group['Sales'].sum().mean():,.0f}",
        "Venta pico/día": f"${daily_group['Sales'].sum().max():,.0f}",
    },
    "tip": f"Sucursal {branch_sales.idxmax()} lidera el período con {branch_sales.max()/tot_s*100:.1f}% de cuota.",
}

pay_counts = df["Payment"].value_counts()
tot_tx = len(df) or 1
tx_drilldown = {
    "title": "Desglose de Transacciones",
    "subtitle": "Distribución por método de pago",
    "items": [
        (p_name, f"{cnt:,} órdenes", f"{(cnt/tot_tx)*100:.1f}%")
        for p_name, cnt in pay_counts.items()
    ],
    "stats": {
        "Órdenes / día": f"{daily_group['Sales'].count().mean():.1f}",
        "Pico diario": f"{daily_group['Sales'].count().max():,}",
    },
    "tip": f"{pay_counts.idxmax()} es el método favorito ({pay_counts.max()/tot_tx*100:.1f}% del total).",
}

prod_profit = df.groupby("Product line")["gross income"].sum().sort_values(ascending=False).head(3)
tot_p = kpis["total_profit"] or 1
profit_drilldown = {
    "title": "Desglose de Ganancia Bruta",
    "subtitle": "Top categorías por aporte a la utilidad",
    "items": [
        (cat, f"${p:,.2f}", f"{(p/tot_p)*100:.1f}%")
        for cat, p in prod_profit.items()
    ],
    "stats": {
        "Margen promedio": f"{kpis['avg_margin']:.1f}%",
        "Ganancia / día": f"${daily_group['gross income'].sum().mean():,.0f}",
    },
    "tip": f"Línea más rentable: {prod_profit.index[0]} aportando ${prod_profit.iloc[0]:,.2f}.",
}

cust_tickets = df.groupby("Customer type")["Sales"].mean()
ticket_drilldown = {
    "title": "Desglose de Ticket Promedio",
    "subtitle": "Segmentos de clientes y tamaño de canasta",
    "items": [
        (f"Cliente {c_type}", f"${t_val:.2f}", "Ticket medio")
        for c_type, t_val in cust_tickets.items()
    ] + [
        ("Unidades por ticket", f"{df['Quantity'].mean():.2f} unids", "Canasta media")
    ],
    "stats": {
        "Ticket mín": f"${df['Sales'].min():.2f}",
        "Ticket máx": f"${df['Sales'].max():.2f}",
    },
    "tip": "Clientes fidelizados ('Member') presentan compras con mayor predictibilidad.",
}

# 5. Primary Executive KPI Row with Interactive Drilldowns
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    render_kpi_card(
        "Ventas totales",
        f"${kpis['total_sales']:,.2f}",
        icon=":material/payments:",
        delta_str=sales_delta,
        delta_status=s_status,
        subtitle=comp_label,
        chart_data=sales_spark,
        chart_type="area",
        drilldown_data=sales_drilldown,
        interactive_icon=":material/insights:",
    )
with col_kpi2:
    render_kpi_card(
        "Transacciones",
        f"{kpis['transactions']:,}",
        icon=":material/receipt_long:",
        delta_str=tx_delta,
        delta_status=t_status,
        subtitle=comp_label,
        chart_data=tx_spark,
        chart_type="line",
        drilldown_data=tx_drilldown,
        interactive_icon=":material/pie_chart:",
    )
with col_kpi3:
    render_kpi_card(
        "Ganancia bruta",
        f"${kpis['total_profit']:,.2f}",
        icon=":material/trending_up:",
        delta_str=profit_delta,
        delta_status=p_status,
        subtitle=comp_label,
        chart_data=profit_spark,
        chart_type="area",
        drilldown_data=profit_drilldown,
        interactive_icon=":material/query_stats:",
    )
with col_kpi4:
    render_kpi_card(
        "Ticket promedio",
        f"${kpis['avg_ticket']:.2f}",
        icon=":material/confirmation_number:",
        delta_str=ticket_delta,
        delta_status=tk_status,
        subtitle=comp_label,
        chart_data=ticket_spark,
        chart_type="line",
        drilldown_data=ticket_drilldown,
        interactive_icon=":material/account_balance_wallet:",
    )

# 6. Operational Targets & Efficiency Row
col_op1, col_op2, col_op3, col_op4 = st.columns(4)
with col_op1:
    render_kpi_card(
        "Margen bruto promedio",
        f"{kpis['avg_margin']:.1f}%",
        icon=":material/percent:",
        help_text="Margen sobre costo estipulado para la cadena",
    )
with col_op2:
    render_kpi_card(
        "Índice de satisfacción",
        f"{kpis['avg_rating']:.2f} / 10",
        icon=":material/star:",
        help_text="Puntuación promedio de NPS y satisfacción directa",
    )
with col_op3:
    render_kpi_card(
        "Unidades vendidas",
        f"{kpis['units_sold']:,}",
        icon=":material/inventory_2:",
    )
with col_op4:
    render_kpi_card(
        "Sucursales operativas",
        f"{kpis['branches_count']}",
        icon=":material/store:",
    )

# 7. Automated Dynamic Insight & Operational Pacing
render_insight_callout(
    title="Diagnóstico Ejecutivo Automatizado",
    message=(
        f"La sucursal con mayor tracción es **{top_branch}** generando **${top_branch_sales:,.2f}** en facturación. "
        f"La línea líder en demanda es **{top_prod}**, sosteniendo un margen promedio del **{kpis['avg_margin']:.1f}%**. "
        f"Se han procesado **{kpis['transactions']:,}** órdenes con un ticket promedio de **${kpis['avg_ticket']:.2f}**."
    ),
    icon=":material/bolt:",
    action_content=(
        f"**Detalles Estratégicos:**\n\n"
        f"- Margen promedio de la red: **{kpis['avg_margin']:.1f}%**\n"
        f"- Nivel de satisfacción de clientes: **{kpis['avg_rating']:.2f} / 10**\n"
        f"- Total de unidades en rotación: **{kpis['units_sold']:,} unidades**\n"
        f"- Rebalanceo sugerido: Priorizar inventario de alta rotación en sucursal {top_branch}."
    ),
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
