"""Products Performance & Market Basket Analysis Page."""
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
from src.models.basket_analysis import (
    calculate_basket_association_rules,
    plot_basket_matrix_heatmap,
)


def render_products_basket_page():
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
                <h1>Rendimiento de Productos & Market Basket Analysis</h1>
                <p>Matriz de rentabilidad por categoría, reglas de asociación cruzada y bundles recomendados</p>
            </div>
            <div>
                <span class="badge-status">Minería de Asociación</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_perf, t_basket = st.tabs(["📊 Matriz de Productos & Margen", "🛒 Canasta de Compra & Venta Cruzada"])

    # TAB 1: Product Performance Matrix
    with t_perf:
        summary = (
            df.groupby("Product line")
            .agg(
                Ventas_Totales=("Sales", "sum"),
                Unidades=("Quantity", "sum"),
                Transacciones=("Sales", "count"),
                Ganancia_Bruta=("gross income", "sum"),
                Margen_Promedio=("gross margin percentage", "mean"),
                Ticket_Promedio=("Sales", "mean"),
                Calificacion_Promedio=("Rating", "mean"),
            )
            .reset_index()
            .sort_values("Ventas_Totales", ascending=False)
        )

        top_cat = summary.iloc[0]["Product line"]
        high_margin_cat = summary.sort_values("Ganancia_Bruta", ascending=False).iloc[0]["Product line"]

        render_insight_callout(
            title="Diagnóstico de Portafolio",
            message=(
                f"La categoría con mayor volumen de facturación es <b>{top_cat}</b> con "
                f"<b>${summary.iloc[0]['Ventas_Totales']:,.2f}</b>. Por otra parte, <b>{high_margin_cat}</b> "
                f"aporta la mayor contribución a la ganancia nuta."
            ),
            icon="🏆",
        )

        # Quadrant Matrix: Scatter Sales vs Margin % vs Units (Bubble size)
        fig_quad = px.scatter(
            summary,
            x="Ventas_Totales",
            y="Margen_Promedio",
            size="Unidades",
            color="Product line",
            text="Product line",
            title="Matriz de Posicionamiento: Ventas vs Margen % (Tamaño = Unidades)",
            labels={"Ventas_Totales": "Ventas ($)", "Margen_Promedio": "Margen Bruto (%)"},
            color_discrete_sequence=PALETTE,
        )
        fig_quad.update_traces(textposition="top center")
        apply_theme(fig_quad)
        st.plotly_chart(fig_quad, width="stretch", alt="Matriz de ventas vs margen por categoría")

        st.markdown("#### Desglose Detallado por Línea")
        st.dataframe(
            summary,
            width="stretch",
            alt="Resumen detallado de ventas por línea de producto",
            column_config={
                "Ventas_Totales": st.column_config.NumberColumn("Ventas ($)", format="$%,.2f"),
                "Ganancia_Bruta": st.column_config.NumberColumn("Ganancia Bruta ($)", format="$%,.2f"),
                "Unidades": st.column_config.NumberColumn("Unidades", format="%d uds"),
                "Margen_Promedio": st.column_config.NumberColumn("Margen %", format="%.2f%%"),
                "Ticket_Promedio": st.column_config.NumberColumn("Ticket Medio", format="$%.2f"),
                "Calificacion_Promedio": st.column_config.NumberColumn("Rating", format="%.2f ⭐"),
            },
        )

    # TAB 2: Market Basket Analysis
    with t_basket:
        st.markdown("### 🔍 Reglas de Asociación de Productos (Cross-Selling)")
        st.caption("Identificación de patrones donde clientes adquieren conjuntamente distintas líneas de producto.")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            min_sup = st.slider("Soporte Mínimo (%)", min_value=1, max_value=20, value=3) / 100.0
        with col_b2:
            min_conf = st.slider("Confianza Mínima (%)", min_value=5, max_value=50, value=15) / 100.0

        rules_df, matrix = calculate_basket_association_rules(df, min_support=min_sup, min_confidence=min_conf)

        if not rules_df.empty:
            # Highlight top rule
            top_rule = rules_df.iloc[0]
            st.success(
                f"💡 **Oportunidad de Bundle:** Los clientes que compran **'{top_rule['Producto Antecedente']}'** tienen "
                f"una probabilidad de comprar **'{top_rule['Producto Consecuente']}'** con un Lift de **{top_rule['Elevación (Lift)']:.2f}x** "
                f"(Soporte: {top_rule['Soporte']*100:.1f}%, Confianza: {top_rule['Confianza']*100:.1f}%)."
            )

            st.dataframe(
                rules_df,
                width="stretch",
                alt="Tabla de reglas de asociación entre productos",
                column_config={
                    "Soporte": st.column_config.NumberColumn("Soporte", format="%.3f"),
                    "Confianza": st.column_config.NumberColumn("Confianza", format="%.3f"),
                    "Elevación (Lift)": st.column_config.ProgressColumn(
                        "Elevación (Lift)",
                        format="%.2fx",
                        min_value=0.0,
                        max_value=float(rules_df["Elevación (Lift)"].max() * 1.2),
                    ),
                },
            )
        else:
            st.info("No se encontraron reglas con los umbrales seleccionados. Intenta reducir el soporte mínimo.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        if not matrix.empty:
            fig_mat = plot_basket_matrix_heatmap(matrix)
            st.plotly_chart(fig_mat, width="stretch", alt="Matriz de afinidad de canasta de compra")


if __name__ == "__main__" or "page" in __name__:
    render_products_basket_page()
