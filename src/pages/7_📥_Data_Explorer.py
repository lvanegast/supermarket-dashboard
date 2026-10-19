"""Data Explorer and DuckDB SQL Console Page."""
import io
import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.theme import load_css
from src.data.db import load_data, DUCKDB_AVAILABLE, DUCKDB_PATH
from src.components.filters import render_sidebar_filters

if DUCKDB_AVAILABLE:
    import duckdb


def render_data_explorer_page():
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
                <h1>Explorador de Datos & Consola DuckDB</h1>
                <p>Inspección detallada de registros, ejecución de consultas SQL analíticas y exportación de datos</p>
            </div>
            <div>
                <span class="badge-status">DuckDB SQL Engine</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_table, t_sql = st.tabs(["📋 Registros Filtrados", "⚡ Consola SQL DuckDB"])

    with t_table:
        st.markdown(f"Mostrando **{len(df):,}** registros según los filtros seleccionados.")

        st.dataframe(
            df,
            width="stretch",
            height=450,
            alt="Tabla de registros transaccionales filtrados",
            column_config={
                "Invoice ID": st.column_config.TextColumn("Factura"),
                "Date": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                "Sales": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
                "gross income": st.column_config.NumberColumn("Margen ($)", format="$%.2f"),
                "Rating": st.column_config.NumberColumn("Calificación", format="%.1f ⭐"),
            },
        )

        # Export buttons
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Descargar filtrado (CSV)",
                data=csv_bytes,
                file_name="supermarket_filtered.csv",
                mime="text/csv",
                width="stretch",
            )
        with col_exp2:
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            st.download_button(
                "⚡ Descargar formato columnar (Parquet)",
                data=buffer.getvalue(),
                file_name="supermarket_filtered.parquet",
                mime="application/octet-stream",
                width="stretch",
            )

    with t_sql:
        st.markdown("##### Ejecutar consulta SQL directa sobre la tabla `sales`:")
        default_query = "SELECT Branch, City, SUM(Sales) as Total_Ventas, AVG(Rating) as Calificacion_Media FROM sales GROUP BY Branch, City ORDER BY Total_Ventas DESC;"
        sql_input = st.text_area("Consulta SQL (DuckDB):", value=default_query, height=90)

        if st.button("🚀 Ejecutar SQL", width="stretch"):
            if DUCKDB_AVAILABLE and DUCKDB_PATH.exists():
                try:
                    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
                    res_df = con.execute(sql_input).fetchdf()
                    con.close()
                    st.success(f"Consulta ejecutada con éxito ({len(res_df)} filas devueltas):")
                    st.dataframe(res_df, width="stretch", alt="Resultado de la consulta SQL ejecutada")
                except Exception as err:
                    st.error(f"Error en consulta DuckDB: {err}")
            else:
                st.warning("DuckDB no está inicializado. Ejecuta primero la carga inicial.")


if __name__ == "__main__" or "page" in __name__:
    render_data_explorer_page()
