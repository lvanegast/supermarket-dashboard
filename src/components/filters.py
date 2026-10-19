"""Sidebar filter manager for SuperMarket Analytics Pro."""
from typing import Tuple, Dict, Any
import pandas as pd
import streamlit as st
from src.core.config import APP_TITLE, APP_SUBTITLE, APP_ICON


def render_sidebar_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Render modern sidebar filters and return the filtered dataset and active criteria."""
    st.sidebar.markdown(
        f"""
        <div style="padding: 12px 0 20px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">{APP_ICON}</span>
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF; letter-spacing: -0.02em;">
                        SuperMarket
                    </div>
                    <div style="font-size: 0.72rem; color: #818CF8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
                        Analytics Pro v2.0
                    </div>
                </div>
            </div>
            <p style="font-size: 0.78rem; color: #94A3B8; margin: 8px 0 0 0;">
                {APP_SUBTITLE}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        return df, {}

    st.sidebar.markdown("##### 🎯 Segmentación & Filtros")

    # Date Range
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    
    date_val = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Dimensions
    all_branches = sorted(df["Branch"].unique().tolist())
    selected_branches = st.sidebar.multiselect("Sucursales", all_branches, default=all_branches)

    all_products = sorted(df["Product line"].unique().tolist())
    selected_products = st.sidebar.multiselect("Líneas de Producto", all_products, default=all_products)

    with st.sidebar.expander("Filtros Adicionales (Clientes y Pago)", expanded=False):
        all_cities = sorted(df["City"].unique().tolist())
        selected_cities = st.multiselect("Ciudad", all_cities, default=all_cities)

        all_ctypes = sorted(df["Customer type"].unique().tolist())
        selected_ctypes = st.multiselect("Tipo de Cliente", all_ctypes, default=all_ctypes)

        all_payments = sorted(df["Payment"].unique().tolist())
        selected_payments = st.multiselect("Método de Pago", all_payments, default=all_payments)

        all_genders = sorted(df["Gender"].unique().tolist())
        selected_genders = st.multiselect("Género", all_genders, default=all_genders)

    # Filter execution
    df_filtered = df.copy()

    start_date, end_date = min_date, max_date
    if isinstance(date_val, tuple) and len(date_val) == 2:
        start_date, end_date = date_val
        df_filtered = df_filtered[
            (df_filtered["Date"].dt.date >= start_date)
            & (df_filtered["Date"].dt.date <= end_date)
        ]

    df_filtered = df_filtered[df_filtered["Branch"].isin(selected_branches)]
    df_filtered = df_filtered[df_filtered["Product line"].isin(selected_products)]
    df_filtered = df_filtered[df_filtered["City"].isin(selected_cities)]
    df_filtered = df_filtered[df_filtered["Customer type"].isin(selected_ctypes)]
    df_filtered = df_filtered[df_filtered["Payment"].isin(selected_payments)]
    df_filtered = df_filtered[df_filtered["Gender"].isin(selected_genders)]

    # Metrics on filtered records
    filter_summary = {
        "start_date": start_date,
        "end_date": end_date,
        "branches": selected_branches,
        "products": selected_products,
        "cities": selected_cities,
        "customer_types": selected_ctypes,
        "payments": selected_payments,
        "genders": selected_genders,
        "total_records": len(df_filtered),
    }

    st.sidebar.markdown(
        f"""
        <div style="margin-top: 24px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Registros Filtrados</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-top: 2px;">{len(df_filtered):,} <span style="font-size:0.8rem; color:#64748B;">/ {len(df):,}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return df_filtered, filter_summary
