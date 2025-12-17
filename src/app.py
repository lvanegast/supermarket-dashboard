import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import timedelta

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except:
    SKLEARN_AVAILABLE = False

# ==============================================
# CARGA DE DATOS
# ==============================================
@st.cache_data
def load_data():
    conn = sqlite3.connect("database/sales.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()
df["Date"] = pd.to_datetime(df["Date"])

# ==============================================
# CONFIGURACIÓN PÁGINA & STYLES DARK
# ==============================================
st.set_page_config(page_title="SuperMarket Analytics", page_icon="🛒", layout="wide")

st.markdown("""
<style>
body { background-color: #111827; }
.kpi-card { background: #1e1e2f; padding: 20px; border-radius: 14px; text-align:center;
           box-shadow:0 4px 10px rgba(0,0,0,0.4); transition: transform .2s; border:1px solid #2a2a40; }
.kpi-card:hover{ transform: scale(1.03); box-shadow:0 6px 18px rgba(0,0,0,0.6); }
.kpi-title{ color:#9ca3af; font-size:0.9rem; margin-bottom:5px; }
.kpi-value{ color:#ffffff; font-size:1.8rem; font-weight:bold; }
h1,h2,h3,h4,h5 { color: #F9FAFB !important; }
</style>
""", unsafe_allow_html=True)

def kpi(title, value, icon="📊"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div style="font-size:1.6rem">{icon}</div>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================================
# SIDEBAR FILTROS
# ==============================================
st.sidebar.header("Filtros")
cities = df["City"].unique().tolist()
city_selected = st.sidebar.selectbox("Ciudad", ["Todas"] + cities)

df_filtered = df if city_selected == "Todas" else df[df["City"] == city_selected]

# ==============================================
# TABS PRINCIPALES
# ==============================================
st.title("🛒 SuperMarket Dashboard — Dark Pro Edition")
tabs = st.tabs(["📊 KPIs", "📈 Ventas", "🛒 Productos", "👥 Clientes", "🤖 Models"])

# -----------------------------
# TAB 0: KPIs
# -----------------------------
with tabs[0]:
    st.subheader("Indicadores Generales")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Ventas Totales", f"${df_filtered['Sales'].sum():,.2f}", "💰")
    with c2:
        kpi("Tickets", f"{len(df_filtered):,}", "🧾")
    with c3:
        kpi("Utilidad Total", f"${df_filtered['gross income'].sum():,.2f}", "📈")
    with c4:
        kpi("Margen (%)", f"{df_filtered['gross margin percentage'].mean():.2f}%", "📊")

# -----------------------------
# TAB 1: Ventas (time series)
# -----------------------------
with tabs[1]:
    st.subheader("Ventas en el Tiempo")

    sales_time = df_filtered.groupby("Date")["Sales"].sum().reset_index()

    fig_time = px.line(
        sales_time,
        x="Date",
        y="Sales",
        markers=True,
        title="Tendencia de Ventas",
        template="plotly_dark"
    )
    st.plotly_chart(fig_time, use_container_width=True)

    # Nuevo gráfico: Área para mostrar acumulado
    fig_area = px.area(
        sales_time,
        x="Date",
        y="Sales",
        title="Ventas Acumuladas en el Tiempo",
        template="plotly_dark"
    )
    st.plotly_chart(fig_area, use_container_width=True)

# -----------------------------
# TAB 2: Productos
# -----------------------------
with tabs[2]:
    st.subheader("Ventas por Product Line")

    sales_by_product = df_filtered.groupby("Product line")["Sales"].sum().reset_index()

    fig_product = px.bar(
        sales_by_product,
        x="Sales",
        y="Product line",
        orientation='h',
        title="Ventas por Categoría (Horizontal)",
        template="plotly_dark",
    )

    st.plotly_chart(fig_product, use_container_width=True)

# -----------------------------
# TAB 3: Clientes
# -----------------------------
with tabs[3]:
    st.subheader("Segmentación de Clientes")

    col1, col2 = st.columns(2)

    with col1:
        gender_seg = df_filtered.groupby("Gender")["Sales"].sum().reset_index()
        fig_gender = px.pie(gender_seg, names="Gender", values="Sales", title="Ventas por Género", template="plotly_dark")
        st.plotly_chart(fig_gender, use_container_width=True)

    with col2:
        payment_seg = df_filtered.groupby("Payment")["Sales"].sum().reset_index()
        fig_payment = px.pie(payment_seg, names="Payment", values="Sales", title="Método de Pago", template="plotly_dark")
        st.plotly_chart(fig_payment, use_container_width=True)

    # Nuevo gráfico: Treemap para ventas por categoría y género
    st.subheader("Ventas por Categoría y Género")
    sales_treemap = df_filtered.groupby(["Product line", "Gender"])["Sales"].sum().reset_index()
    fig_treemap = px.treemap(
        sales_treemap,
        path=["Product line", "Gender"],
        values="Sales",
        title="Distribución de Ventas",
        template="plotly_dark"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

# -----------------------------
# TAB 4: AI MODELS
# -----------------------------
with tabs[4]:
    st.subheader("🤖 Models")

    # =============================
    # 1) FORECAST
    # =============================
    st.markdown("## 🔮 Heatmap")

    # -----------------------------
    # HEATMAP: Ventas por Día y Hora
    # -----------------------------
    st.subheader("Mapa de calor: Ventas por Día y Hora")

    df_hm = df_filtered.copy()

    # Día de la semana
    df_hm["weekday"] = df_hm["Date"].dt.day_name()

    # Parseo seguro de la hora
    if "Time" in df_hm.columns:
        df_hm["hour"] = pd.to_datetime(df_hm["Time"], errors="coerce").dt.hour
    else:
        df_hm["hour"] = 0

    df_hm["hour"] = df_hm["hour"].fillna(0).astype(int)

    # Agrupar ventas
    heatmap_data = df_hm.groupby(["weekday", "hour"])["Sales"].sum().reset_index()

    # Orden correcto de días
    order_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data["weekday"] = pd.Categorical(heatmap_data["weekday"], categories=order_days, ordered=True)

    # Pivot table
    pivot = heatmap_data.pivot(index="weekday", columns="hour", values="Sales").fillna(0)

    # Gráfico
    fig_heatmap = px.imshow(
        pivot,
        labels=dict(x="Hora del Día", y="Día de la Semana", color="Ventas ($)"),
        aspect="auto",
        color_continuous_scale="Viridis",
        text_auto=True,
    )

    fig_heatmap.update_layout(
        template="plotly_dark",
        xaxis=dict(side="top"),
        title="Intensidad de Ventas por Día y Hora",
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)


    st.markdown("---")

    # =============================
    # 2) CLUSTERING
    # =============================
    st.markdown("## 🧩 Segmentación de Clientes (K-Means)")

    if SKLEARN_AVAILABLE:

        df_cl = df_filtered.copy()

        customer = df_cl.groupby("Invoice ID").agg({
            "Sales": "sum",
            "Quantity": "sum",
            "Rating": "mean"
        }).reset_index()

        customer.columns = ["invoice", "total_sales", "total_qty", "avg_rating"]

        scaler = StandardScaler()
        X = scaler.fit_transform(customer[["total_sales", "total_qty", "avg_rating"]])

        kmeans = KMeans(n_clusters=3, n_init=10)
        customer["cluster"] = kmeans.fit_predict(X)

        fig_cluster = px.scatter_3d(
            customer,
            x="total_sales",
            y="total_qty",
            z="avg_rating",
            color="cluster",
            title="Clusters de Clientes",
            template="plotly_dark"
        )
        st.plotly_chart(fig_cluster, use_container_width=True)

        st.write("### Clientes por cluster")
        st.dataframe(customer)

    else:
        st.warning("scikit-learn no instalado.")


# ==============================================
# FIN
# ==============================================
st.markdown("---")
st.caption("Dashboard desarrollado con Streamlit · Prophet · scikit-learn · Plotly")
