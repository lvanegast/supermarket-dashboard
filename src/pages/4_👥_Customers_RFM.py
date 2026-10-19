"""Customer Intelligence & RFM Segmentation Page."""
import streamlit as st
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.theme import load_css, apply_theme
from src.core.config import COLORS, PALETTE
from src.data.db import load_data
from src.components.filters import render_sidebar_filters
from src.components.kpi_card import render_kpi_card, render_insight_callout
from src.models.rfm_clustering import calculate_rfm_segments


def render_customers_rfm_page():
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
                <h1>Inteligencia de Clientes & Segmentación RFM</h1>
                <p>Clustering conductual, análisis de valor de vida (LTV) y fidelización Miembros vs Regulares</p>
            </div>
            <div>
                <span class="badge-status">K-Means Conductual</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_rfm, t_member = st.tabs(["🧩 Segmentación RFM & Clusters", "💳 Análisis Miembros vs Normal"])

    with t_rfm:
        col_ctrl, col_sil = st.columns([2, 1])
        with col_ctrl:
            k_clusters = st.slider("Número de Segmentos (k)", min_value=2, max_value=6, value=4)

        rfm_df, metrics, fig_3d = calculate_rfm_segments(df, n_clusters=k_clusters)

        with col_sil:
            render_kpi_card(
                "Silhouette Score",
                f"{metrics['silhouette_score']:.3f}",
                icon="🎯",
                subtitle="Calidad de separación matemática de clusters",
                theme_color="emerald" if metrics['silhouette_score'] > 0.35 else "amber",
            )

        render_insight_callout(
            title="Estrategia de Fidelización Retail",
            message=(
                "Los clientes agrupados en <b>💎 Alto Valor</b> presentan la mayor rentabilidad por visita. "
                "Para el segmento <b>⚠️ En Riesgo</b>, se recomienda activar incentivos por correo o cashback "
                "inmediato para recuperar la frecuencia antes de que deserten hacia la competencia."
            ),
            icon="🧠",
        )

        st.plotly_chart(fig_3d, width="stretch", alt="Diagrama 3D de segmentación de clientes")

        st.markdown("#### Resumen Estratégico por Segmento")
        st.dataframe(
            metrics["cluster_summary"],
            width="stretch",
            alt="Resumen estratégico de métricas por cluster de clientes",
            column_config={
                "Perfiles": st.column_config.NumberColumn("Transacciones", format="%d"),
                "Ticket_Promedio": st.column_config.NumberColumn("Ticket Medio ($)", format="$%,.2f"),
                "Recencia_Promedio": st.column_config.NumberColumn("Recencia Media (días)", format="%.1f d"),
                "Calificacion_Promedio": st.column_config.NumberColumn("Calificación", format="%.2f ⭐"),
            },
        )

    with t_member:
        st.markdown("### 🏆 Comportamiento Comparativo: Miembros vs Regulares")
        
        member_agg = (
            df.groupby("Customer type")
            .agg(
                Ventas=("Sales", "sum"),
                Transacciones=("Sales", "count"),
                Ticket_Promedio=("Sales", "mean"),
                Margen_Total=("gross income", "sum"),
                Rating_Promedio=("Rating", "mean"),
            )
            .round(2)
            .reset_index()
        )

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            fig_bar_sales = px.bar(
                member_agg,
                x="Customer type",
                y="Ventas",
                color="Customer type",
                title="Ventas Totales por Tipo de Cliente",
                color_discrete_sequence=[COLORS["primary"], COLORS["emerald"]],
                text_auto="$,.0f",
            )
            apply_theme(fig_bar_sales, showlegend=False)
            st.plotly_chart(fig_bar_sales, width="stretch", alt="Ventas por tipo de cliente")

        with col_m2:
            fig_bar_ticket = px.bar(
                member_agg,
                x="Customer type",
                y="Ticket_Promedio",
                color="Customer type",
                title="Ticket Promedio por Tipo de Cliente",
                color_discrete_sequence=[COLORS["cyan"], COLORS["amber"]],
                text_auto="$.2f",
            )
            apply_theme(fig_bar_ticket, showlegend=False)
            st.plotly_chart(fig_bar_ticket, width="stretch", alt="Ticket promedio por tipo de cliente")

        st.markdown("#### Comparativa Numérica Directa")
        st.dataframe(
            member_agg,
            width="stretch",
            alt="Comparativa directa miembros vs clientes regulares",
            column_config={
                "Ventas": st.column_config.NumberColumn("Ventas ($)", format="$%,.2f"),
                "Margen_Total": st.column_config.NumberColumn("Margen Bruto ($)", format="$%,.2f"),
                "Ticket_Promedio": st.column_config.NumberColumn("Ticket Medio", format="$%.2f"),
                "Rating_Promedio": st.column_config.NumberColumn("Calificación", format="%.2f ⭐"),
            },
        )


if __name__ == "__main__" or "page" in __name__:
    render_customers_rfm_page()
