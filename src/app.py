import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from datetime import timedelta

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ==============================================
# CONFIGURACION PAGINA
# ==============================================
st.set_page_config(page_title="SuperMarket Analytics", page_icon="🛒", layout="wide")

# ==============================================
# PALETA Y CONSTANTES DE DISEÑO
# ==============================================
COLORS = {
    "primary": "#6366f1",
    "primary_light": "#818cf8",
    "accent": "#10b981",
    "accent2": "#f59e0b",
    "accent3": "#ef4444",
    "accent4": "#ec4899",
    "surface": "#1e1e2f",
    "surface_hover": "#2a2a40",
    "border": "#334155",
    "text": "#F9FAFB",
    "text_muted": "#94a3b8",
    "bg": "#111827",
}

PALETTE = [
    "#6366f1", "#10b981", "#f59e0b", "#ef4444", "#ec4899",
    "#06b6d4", "#8b5cf6", "#f97316",
]

# Plotly layout base reutilizable
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text"]),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font=dict(size=16, color=COLORS["text"]),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=11),
    ),
    colorway=PALETTE,
)

# ==============================================
# CSS MODERNO
# ==============================================
st.markdown(f"""
<style>
/* ==========================================
   GLASSMORPHISM DESIGN SYSTEM
   ========================================== */

/* ---- Fonts ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ---- CSS Variables ---- */
:root {{
    --glass-bg: rgba(30, 30, 47, 0.4);
    --glass-border: rgba(139, 92, 246, 0.15);
    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    --glass-blur: 16px;
    --animation-speed: 0.6s;
}}

/* ---- Global Styles ---- */
html, body, [class*="css"] {{
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}}

/* ---- Enhanced Dark Background ---- */
.stApp {{
    background: linear-gradient(135deg,
        #0a0a1f 0%,
        #1a0b2e 25%,
        #16213e 50%,
        #0f0f23 75%,
        #0a0a1f 100%
    );
    background-attachment: fixed;
}}

/* Animated gradient mesh overlay */
.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 50%);
    pointer-events: none;
    animation: meshPulse 15s ease-in-out infinite;
    z-index: 0;
}}

/* ==========================================
   ANIMATIONS
   ========================================== */

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes shimmer {{
    0%   {{ background-position: -200% center; }}
    100% {{ background-position: 200% center; }}
}}

@keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50%      {{ transform: scale(1.05); }}
}}

@keyframes glowPulse {{
    0%, 100% {{
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3),
                    0 0 40px rgba(99, 102, 241, 0.1);
    }}
    50% {{
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.5),
                    0 0 60px rgba(99, 102, 241, 0.2);
    }}
}}

@keyframes gradientShift {{
    0%, 100% {{ background-position: 0% 50%; }}
    50%      {{ background-position: 100% 50%; }}
}}

@keyframes borderGlow {{
    0%, 100% {{ opacity: 0.5; }}
    50%      {{ opacity: 1; }}
}}

@keyframes meshPulse {{
    0%, 100% {{ opacity: 0.6; }}
    50%      {{ opacity: 0.9; }}
}}

/* ==========================================
   SIDEBAR GLASS EFFECT
   ========================================== */

section[data-testid="stSidebar"] {{
    background: rgba(17, 17, 35, 0.6) !important;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid rgba(139, 92, 246, 0.2) !important;
}}

section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}

.sidebar-logo {{
    background: linear-gradient(135deg,
        rgba(99, 102, 241, 0.15) 0%,
        rgba(139, 92, 246, 0.15) 100%
    );
    border-radius: 16px;
    padding: 24px 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    backdrop-filter: blur(10px);
    text-align: center;
    animation: fadeInUp var(--animation-speed) ease-out;
}}

.sidebar-logo-icon {{
    font-size: 3rem;
    display: block;
    margin-bottom: 12px;
    animation: pulse 3s ease-in-out infinite;
}}

.sidebar-logo-title {{
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #a5b4fc, #c4b5fd);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s ease infinite;
    letter-spacing: -0.02em;
}}

.sidebar-logo-subtitle {{
    font-size: 0.8rem;
    color: {COLORS["text_muted"]};
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

.sidebar-section-header {{
    font-weight: 600;
    font-size: 0.75rem;
    color: {COLORS["text_muted"]};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 24px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(139, 92, 246, 0.2);
}}

section[data-testid="stSidebar"] .stMultiSelect > div,
section[data-testid="stSidebar"] .stDateInput > div > div {{
    background: rgba(30, 30, 47, 0.5) !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    border-radius: 10px !important;
}}

/* ==========================================
   HERO HEADER
   ========================================== */

.hero-header {{
    background: linear-gradient(135deg,
        rgba(99, 102, 241, 0.1) 0%,
        rgba(139, 92, 246, 0.08) 50%,
        rgba(16, 185, 129, 0.06) 100%
    );
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 24px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
    animation: fadeInUp var(--animation-speed) ease-out;
}}

.hero-header::before {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
    animation: meshPulse 8s ease-in-out infinite;
}}

.hero-title {{
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
    background: linear-gradient(135deg,
        {COLORS["text"]} 0%,
        #a5b4fc 50%,
        {COLORS["primary_light"]} 100%
    );
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 5s ease infinite;
    position: relative;
    z-index: 1;
}}

.hero-subtitle {{
    color: {COLORS["text_muted"]};
    font-size: 1rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}}

.hero-stats-strip {{
    display: flex;
    gap: 24px;
    margin-top: 20px;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}}

.hero-stat {{
    flex: 1;
    min-width: 150px;
    padding: 12px 20px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid rgba(139, 92, 246, 0.15);
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}}

.hero-stat:hover {{
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(139, 92, 246, 0.3);
    transform: translateY(-2px);
}}

.hero-stat-label {{
    font-size: 0.7rem;
    color: {COLORS["text_muted"]};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}}

.hero-stat-value {{
    font-size: 1.2rem;
    color: {COLORS["text"]};
    font-weight: 700;
    margin-top: 4px;
}}

/* ==========================================
   GLASS KPI CARDS
   ========================================== */

.kpi-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur)) saturate(180%);
    -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(180%);
    padding: 28px 24px;
    border-radius: 20px;
    text-align: center;
    border: 1px solid var(--glass-border);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp var(--animation-speed) ease-out backwards;
}}

.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg,
        {COLORS["primary"]} 0%,
        {COLORS["primary_light"]} 25%,
        #a5b4fc 50%,
        {COLORS["primary_light"]} 75%,
        {COLORS["primary"]} 100%
    );
    background-size: 200% auto;
    border-radius: 20px 20px 0 0;
    animation: gradientShift 3s linear infinite, borderGlow 2s ease-in-out infinite;
}}

.kpi-card::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.08) 50%,
        transparent 100%
    );
    background-size: 200% 100%;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}}

.kpi-card:hover {{
    transform: translateY(-6px) scale(1.02);
    box-shadow:
        0 20px 40px rgba(99, 102, 241, 0.2),
        0 0 80px rgba(99, 102, 241, 0.1),
        inset 0 0 40px rgba(99, 102, 241, 0.05);
    border-color: rgba(139, 92, 246, 0.4);
}}

.kpi-card:hover::after {{
    animation: shimmer 1.5s infinite;
    opacity: 1;
}}

.kpi-icon {{
    font-size: 2.5rem;
    margin-bottom: 12px;
    display: block;
    filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.3));
    animation: pulse 4s ease-in-out infinite;
}}

.kpi-title {{
    color: {COLORS["text_muted"]};
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}}

.kpi-value {{
    color: {COLORS["text"]};
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    text-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
}}

.kpi-delta {{
    font-size: 0.8rem;
    font-weight: 700;
    margin-top: 10px;
    padding: 4px 14px;
    border-radius: 20px;
    display: inline-block;
    backdrop-filter: blur(8px);
    border: 1px solid transparent;
}}

.kpi-delta.up {{
    color: #34d399;
    background: rgba(16, 185, 129, 0.15);
    border-color: rgba(16, 185, 129, 0.3);
}}

.kpi-delta.down {{
    color: #f87171;
    background: rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.3);
}}

.kpi-delta.neutral {{
    color: {COLORS["text_muted"]};
    background: rgba(148, 163, 184, 0.15);
    border-color: rgba(148, 163, 184, 0.3);
}}

/* ==========================================
   GLASS-STYLE PILL TABS
   ========================================== */

div[data-baseweb="tab-list"] {{
    gap: 8px;
    background: rgba(30, 30, 47, 0.5);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 6px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
}}

button[data-baseweb="tab"] {{
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid transparent !important;
}}

button[data-baseweb="tab"]:hover {{
    background: rgba(99, 102, 241, 0.1) !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]}) !important;
    box-shadow:
        0 4px 15px rgba(99, 102, 241, 0.3),
        0 0 30px rgba(99, 102, 241, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}}

/* ==========================================
   CHART GLASS CONTAINERS
   ========================================== */

div[data-testid="stPlotlyChart"] {{
    background: rgba(30, 30, 47, 0.3);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid rgba(139, 92, 246, 0.15);
    box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    animation: fadeInUp var(--animation-speed) ease-out;
    transition: all 0.3s ease;
}}

div[data-testid="stPlotlyChart"]:hover {{
    border-color: rgba(139, 92, 246, 0.25);
    box-shadow:
        0 12px 32px rgba(0, 0, 0, 0.4),
        0 0 40px rgba(99, 102, 241, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}

/* ==========================================
   DATAFRAME GLASS STYLING
   ========================================== */

div[data-testid="stDataFrame"] {{
    background: rgba(30, 30, 47, 0.4);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(139, 92, 246, 0.2);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}}

/* ==========================================
   METRIC CARDS (st.metric)
   ========================================== */

div[data-testid="stMetric"] {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    padding: 20px 24px;
    border-radius: 16px;
    border: 1px solid var(--glass-border);
    transition: all 0.3s ease;
}}

div[data-testid="stMetric"]:hover {{
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}}

/* ==========================================
   BUTTONS & INTERACTIONS
   ========================================== */

button[data-testid="stDownloadButton"] {{
    background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-weight: 700 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}}

button[data-testid="stDownloadButton"]:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
}}

div[role="radiogroup"] {{
    background: rgba(30, 30, 47, 0.4);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 8px;
    border: 1px solid rgba(139, 92, 246, 0.15);
}}

div[data-testid="stCheckbox"] {{
    background: rgba(30, 30, 47, 0.3);
    backdrop-filter: blur(8px);
    border-radius: 8px;
    padding: 8px 12px;
    border: 1px solid rgba(139, 92, 246, 0.1);
}}

/* ==========================================
   ALERTS & BANNERS
   ========================================== */

div[data-testid="stAlert"] {{
    background: rgba(30, 30, 47, 0.5) !important;
    backdrop-filter: blur(12px);
    border-radius: 14px;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}}

/* ==========================================
   GLASS FOOTER
   ========================================== */

.glass-footer {{
    background: rgba(30, 30, 47, 0.4);
    backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 20px;
    margin-top: 40px;
    border: 1px solid rgba(139, 92, 246, 0.15);
    text-align: center;
}}

.glass-footer p {{
    color: {COLORS["text_muted"]};
    font-size: 0.85rem;
    margin: 0;
}}

.glass-footer a {{
    color: {COLORS["primary_light"]};
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s ease;
}}

.glass-footer a:hover {{
    color: #c4b5fd;
    text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}}

/* ==========================================
   RESPONSIVE
   ========================================== */

@media (max-width: 768px) {{
    .hero-title {{ font-size: 1.8rem; }}
    .kpi-card {{ padding: 20px 16px; }}
    .kpi-value {{ font-size: 1.5rem; }}
    .hero-stats-strip {{ flex-direction: column; gap: 12px; }}
}}
</style>
""", unsafe_allow_html=True)

# ==============================================
# CARGA DE DATOS
# ==============================================
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "sales.db"


@st.cache_data
def load_data():
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    df["Date"] = pd.to_datetime(df["Date"])
    return df


df = load_data()

if df is None or df.empty:
    st.error("No se encontro la base de datos. Ejecuta primero: `python src/load_data.py`")
    st.stop()

# ==============================================
# SIDEBAR - FILTROS
# ==============================================
st.sidebar.markdown(
    '''
    <div class="sidebar-logo">
        <span class="sidebar-logo-icon">🛒</span>
        <div class="sidebar-logo-title">SuperMarket</div>
        <div class="sidebar-logo-subtitle">Analytics Pro</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-section-header">🎯 Filtros de Datos</div>',
                    unsafe_allow_html=True)

# Rango de fechas
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Multiselects
cities = sorted(df["City"].unique().tolist())
city_sel = st.sidebar.multiselect("Ciudad", cities, default=cities)

products = sorted(df["Product line"].unique().tolist())
product_sel = st.sidebar.multiselect("Linea de Producto", products, default=products)

genders = sorted(df["Gender"].unique().tolist())
gender_sel = st.sidebar.multiselect("Genero", genders, default=genders)

payments = sorted(df["Payment"].unique().tolist())
payment_sel = st.sidebar.multiselect("Metodo de Pago", payments, default=payments)

customer_types = sorted(df["Customer type"].unique().tolist())
ctype_sel = st.sidebar.multiselect("Tipo de Cliente", customer_types, default=customer_types)

# Aplicar filtros
df_filtered = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered["Date"].dt.date >= start_date)
        & (df_filtered["Date"].dt.date <= end_date)
    ]

df_filtered = df_filtered[df_filtered["City"].isin(city_sel)]
df_filtered = df_filtered[df_filtered["Product line"].isin(product_sel)]
df_filtered = df_filtered[df_filtered["Gender"].isin(gender_sel)]
df_filtered = df_filtered[df_filtered["Payment"].isin(payment_sel)]
df_filtered = df_filtered[df_filtered["Customer type"].isin(ctype_sel)]

# ==============================================
# TITULO
# ==============================================
total_records = len(df_filtered)
date_range_str = (f"{df_filtered['Date'].min().strftime('%b %d')} - "
                  f"{df_filtered['Date'].max().strftime('%b %d, %Y')}")
cities_count = df_filtered['City'].nunique()

st.markdown(
    f'''
    <div class="hero-header">
        <div class="hero-title">🛒 SuperMarket Dashboard</div>
        <div class="hero-subtitle">Panel interactivo de ventas y segmentacion de clientes</div>
        <div class="hero-stats-strip">
            <div class="hero-stat">
                <div class="hero-stat-label">Periodo</div>
                <div class="hero-stat-value">{date_range_str}</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-label">Registros</div>
                <div class="hero-stat-value">{total_records:,}</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-label">Ciudades</div>
                <div class="hero-stat-value">{cities_count}</div>
            </div>
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# Banner filtros activos
active_filters = []
if len(city_sel) < len(cities):
    active_filters.append(f"**Ciudades:** {', '.join(city_sel)}")
if len(product_sel) < len(products):
    active_filters.append(f"**Productos:** {', '.join(product_sel)}")
if len(gender_sel) < len(genders):
    active_filters.append(f"**Genero:** {', '.join(gender_sel)}")
if len(payment_sel) < len(payments):
    active_filters.append(f"**Pago:** {', '.join(payment_sel)}")
if len(ctype_sel) < len(customer_types):
    active_filters.append(f"**Tipo:** {', '.join(ctype_sel)}")
if isinstance(date_range, tuple) and len(date_range) == 2:
    if date_range[0] != min_date or date_range[1] != max_date:
        active_filters.append(f"**Fechas:** {date_range[0]} a {date_range[1]}")

if active_filters:
    st.info(" · ".join(active_filters))

if df_filtered.empty:
    st.warning("No hay datos para la combinacion de filtros seleccionada.")
    st.stop()

# ==============================================
# HELPERS
# ==============================================

def kpi_card(title, value, icon, delta_str=None):
    """Render a glassmorphism KPI card with animated borders and optional delta."""
    delta_html = ""
    if delta_str is not None:
        css_class = "up" if delta_str.startswith("+") else ("down" if delta_str.startswith("-") else "neutral")
        delta_html = f'<div class="kpi-delta {css_class}">{delta_str}</div>'
    st.markdown(
        f'''
        <div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        ''',
        unsafe_allow_html=True,
    )


def apply_layout(fig, **extra):
    """Apply consistent layout to any Plotly figure."""
    layout = {**PLOTLY_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig


# ==============================================
# PERIODO ANTERIOR PARA DELTAS
# ==============================================
def get_previous_period(df_full, date_range_val):
    if not (isinstance(date_range_val, tuple) and len(date_range_val) == 2):
        return pd.DataFrame()
    start = pd.Timestamp(date_range_val[0])
    end = pd.Timestamp(date_range_val[1])
    duration = end - start
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - duration
    mask = (df_full["Date"] >= prev_start) & (df_full["Date"] <= prev_end)
    prev = df_full[mask]
    prev = prev[prev["City"].isin(city_sel)]
    prev = prev[prev["Product line"].isin(product_sel)]
    prev = prev[prev["Gender"].isin(gender_sel)]
    prev = prev[prev["Payment"].isin(payment_sel)]
    prev = prev[prev["Customer type"].isin(ctype_sel)]
    return prev


df_prev = get_previous_period(df, date_range)


def calc_delta_pct(current, previous):
    if previous and previous != 0:
        pct = (current - previous) / abs(previous) * 100
        return f"{pct:+.1f}%"
    return None


# ==============================================
# TABS
# ==============================================
tabs = st.tabs(
    ["📊 KPIs", "📈 Ventas", "🛒 Productos", "👥 Clientes", "🤖 Modelos", "📥 Datos"]
)

# ===================== TAB 0: KPIs =====================
with tabs[0]:
    total_sales = df_filtered["Sales"].sum()
    total_tickets = len(df_filtered)
    total_profit = df_filtered["gross income"].sum()
    avg_margin = df_filtered["gross margin percentage"].mean()
    avg_ticket = total_sales / total_tickets if total_tickets > 0 else 0
    avg_rating = df_filtered["Rating"].mean()

    prev_sales = df_prev["Sales"].sum() if not df_prev.empty else None
    prev_tickets = len(df_prev) if not df_prev.empty else None
    prev_profit = df_prev["gross income"].sum() if not df_prev.empty else None
    prev_margin = df_prev["gross margin percentage"].mean() if not df_prev.empty else None
    prev_avg_ticket = (prev_sales / prev_tickets) if (prev_tickets and prev_tickets > 0) else None
    prev_rating = df_prev["Rating"].mean() if not df_prev.empty else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Ventas Totales", f"${total_sales:,.0f}", "💰",
                 calc_delta_pct(total_sales, prev_sales))
    with c2:
        kpi_card("Tickets", f"{total_tickets:,}", "🧾",
                 calc_delta_pct(total_tickets, prev_tickets))
    with c3:
        kpi_card("Utilidad Total", f"${total_profit:,.0f}", "📈",
                 calc_delta_pct(total_profit, prev_profit))
    with c4:
        kpi_card("Margen", f"{avg_margin:.1f}%", "📊",
                 f"{(avg_margin - prev_margin):+.2f} pp" if prev_margin else None)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    c5, c6, c7 = st.columns(3)
    with c5:
        kpi_card("Ticket Promedio", f"${avg_ticket:,.2f}", "🎫",
                 calc_delta_pct(avg_ticket, prev_avg_ticket))
    with c6:
        kpi_card("Rating Promedio", f"{avg_rating:.2f} / 10", "⭐",
                 f"{(avg_rating - prev_rating):+.2f}" if prev_rating else None)
    with c7:
        kpi_card("Sucursales", f"{df_filtered['Branch'].nunique()}", "🏪", None)

# ===================== TAB 1: Ventas =====================
with tabs[1]:
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        freq = st.radio("Agrupacion", ["Diario", "Semanal"], horizontal=True, key="freq_ventas")
    with col_opt2:
        by_branch = st.checkbox("Desglosar por Sucursal")

    freq_code = "D" if freq == "Diario" else "W"

    if by_branch:
        sales_time = (
            df_filtered.groupby([pd.Grouper(key="Date", freq=freq_code), "Branch"])["Sales"]
            .sum().reset_index()
        )
        fig_time = px.line(
            sales_time, x="Date", y="Sales", color="Branch",
            markers=True, title="Tendencia de Ventas por Sucursal",
        )
    else:
        sales_time = (
            df_filtered.groupby(pd.Grouper(key="Date", freq=freq_code))["Sales"]
            .sum().reset_index()
        )
        fig_time = px.line(
            sales_time, x="Date", y="Sales",
            markers=True, title="Tendencia de Ventas",
        )
        fig_time.update_traces(
            line=dict(width=2.5, color=COLORS["primary"]),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.08)",
        )

    apply_layout(fig_time)
    st.plotly_chart(fig_time, use_container_width=True)

    # Acumulado real con cumsum
    sales_cum = (
        df_filtered.groupby(pd.Grouper(key="Date", freq=freq_code))["Sales"]
        .sum().reset_index().sort_values("Date")
    )
    sales_cum["Acumulado"] = sales_cum["Sales"].cumsum()

    fig_area = px.area(
        sales_cum, x="Date", y="Acumulado",
        title="Ventas Acumuladas",
    )
    fig_area.update_traces(
        line=dict(width=2, color=COLORS["accent"]),
        fillcolor="rgba(16, 185, 129, 0.12)",
    )
    apply_layout(fig_area)
    st.plotly_chart(fig_area, use_container_width=True)

# ===================== TAB 2: Productos =====================
with tabs[2]:
    sales_by_product = (
        df_filtered.groupby("Product line")
        .agg(Ventas=("Sales", "sum"), Utilidad=("gross income", "sum"))
        .reset_index()
        .sort_values("Ventas")
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_ps = px.bar(
            sales_by_product, x="Ventas", y="Product line", orientation="h",
            title="Ventas por Categoria",
            color="Ventas", color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
        )
        fig_ps.update_traces(marker_line_width=0)
        fig_ps.update_coloraxes(showscale=False)
        apply_layout(fig_ps)
        st.plotly_chart(fig_ps, use_container_width=True)

    with col_p2:
        fig_pp = px.bar(
            sales_by_product, x="Utilidad", y="Product line", orientation="h",
            title="Utilidad por Categoria",
            color="Utilidad", color_continuous_scale=["#064e3b", "#10b981", "#6ee7b7"],
        )
        fig_pp.update_traces(marker_line_width=0)
        fig_pp.update_coloraxes(showscale=False)
        apply_layout(fig_pp)
        st.plotly_chart(fig_pp, use_container_width=True)

    # Ticket promedio
    avg_ticket_prod = (
        df_filtered.groupby("Product line")["Sales"]
        .mean().reset_index()
        .rename(columns={"Sales": "Ticket Promedio"})
        .sort_values("Ticket Promedio")
    )
    fig_at = px.bar(
        avg_ticket_prod, x="Ticket Promedio", y="Product line", orientation="h",
        title="Ticket Promedio por Categoria",
        color="Ticket Promedio", color_continuous_scale=["#4c1d95", "#8b5cf6", "#c4b5fd"],
    )
    fig_at.update_traces(marker_line_width=0)
    fig_at.update_coloraxes(showscale=False)
    apply_layout(fig_at)
    st.plotly_chart(fig_at, use_container_width=True)

    # Tabla resumen
    st.markdown(f'<p style="font-weight:600;font-size:1rem;margin:20px 0 8px">'
                f'Resumen por Linea de Producto</p>', unsafe_allow_html=True)
    summary = (
        df_filtered.groupby("Product line")
        .agg(
            Ventas=("Sales", "sum"),
            Tickets=("Sales", "count"),
            Ticket_Promedio=("Sales", "mean"),
            Utilidad=("gross income", "sum"),
            Rating_Promedio=("Rating", "mean"),
        )
        .round(2)
        .sort_values("Ventas", ascending=False)
    )
    st.dataframe(summary, use_container_width=True)

# ===================== TAB 3: Clientes =====================
with tabs[3]:
    col1, col2 = st.columns(2)
    with col1:
        gender_seg = df_filtered.groupby("Gender")["Sales"].sum().reset_index()
        fig_g = px.pie(
            gender_seg, names="Gender", values="Sales",
            title="Ventas por Genero",
            hole=0.45,
            color_discrete_sequence=[COLORS["primary"], COLORS["accent4"]],
        )
        fig_g.update_traces(textinfo="percent+label", textfont_size=12)
        apply_layout(fig_g)
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        payment_seg = df_filtered.groupby("Payment")["Sales"].sum().reset_index()
        fig_p = px.pie(
            payment_seg, names="Payment", values="Sales",
            title="Ventas por Metodo de Pago",
            hole=0.45,
            color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["accent2"]],
        )
        fig_p.update_traces(textinfo="percent+label", textfont_size=12)
        apply_layout(fig_p)
        st.plotly_chart(fig_p, use_container_width=True)

    # Member vs Normal
    st.markdown(f'<p style="font-weight:600;font-size:1rem;margin:20px 0 8px">'
                f'Miembros vs Normales</p>', unsafe_allow_html=True)
    member_stats = (
        df_filtered.groupby("Customer type")
        .agg(
            Ventas=("Sales", "sum"),
            Tickets=("Sales", "count"),
            Ticket_Promedio=("Sales", "mean"),
            Rating_Promedio=("Rating", "mean"),
        )
        .round(2)
    )
    st.dataframe(member_stats, use_container_width=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        fig_mv = px.bar(
            member_stats.reset_index(), x="Customer type", y="Ventas",
            title="Ventas: Miembros vs Normales",
            color="Customer type",
            color_discrete_sequence=[COLORS["primary"], COLORS["accent"]],
        )
        fig_mv.update_traces(marker_line_width=0)
        apply_layout(fig_mv, showlegend=False)
        st.plotly_chart(fig_mv, use_container_width=True)
    with col_m2:
        fig_mr = px.bar(
            member_stats.reset_index(), x="Customer type", y="Rating_Promedio",
            title="Rating Promedio por Tipo",
            color="Customer type",
            color_discrete_sequence=[COLORS["primary"], COLORS["accent"]],
        )
        fig_mr.update_traces(marker_line_width=0)
        apply_layout(fig_mr, showlegend=False)
        st.plotly_chart(fig_mr, use_container_width=True)

    # Treemap
    sales_treemap = (
        df_filtered.groupby(["Product line", "Gender"])["Sales"].sum().reset_index()
    )
    fig_tm = px.treemap(
        sales_treemap, path=["Product line", "Gender"], values="Sales",
        title="Distribucion de Ventas por Categoria y Genero",
        color="Sales", color_continuous_scale="Viridis",
    )
    fig_tm.update_coloraxes(showscale=False)
    apply_layout(fig_tm)
    st.plotly_chart(fig_tm, use_container_width=True)

    # Rating por segmento
    rating_seg = (
        df_filtered.groupby(["Gender", "Customer type"])["Rating"].mean().reset_index()
    )
    fig_rs = px.bar(
        rating_seg, x="Gender", y="Rating", color="Customer type",
        barmode="group", title="Rating Promedio por Genero y Tipo de Cliente",
        color_discrete_sequence=[COLORS["primary"], COLORS["accent"]],
    )
    fig_rs.update_traces(marker_line_width=0)
    apply_layout(fig_rs)
    st.plotly_chart(fig_rs, use_container_width=True)

# ===================== TAB 4: Modelos =====================
with tabs[4]:
    # ---------- HEATMAP ----------
    st.markdown(f'<p style="font-weight:600;font-size:1.1rem;margin-bottom:12px">'
                f'Mapa de Calor: Ventas por Dia y Hora</p>', unsafe_allow_html=True)

    hm_mode = st.radio("Metrica del Heatmap", ["Total", "Promedio"], horizontal=True, key="hm_mode")

    df_hm = df_filtered.copy()
    df_hm["weekday"] = df_hm["Date"].dt.day_name()

    if "Time" in df_hm.columns:
        df_hm["hour"] = pd.to_datetime(df_hm["Time"], format="%H:%M", errors="coerce").dt.hour
        # Fallback: try 12-hour format if most are NaT
        if df_hm["hour"].isna().sum() > len(df_hm) * 0.5:
            df_hm["hour"] = pd.to_datetime(df_hm["Time"], format="%I:%M:%S %p", errors="coerce").dt.hour
    else:
        df_hm["hour"] = 0
    df_hm["hour"] = df_hm["hour"].fillna(0).astype(int)

    agg_func = "sum" if hm_mode == "Total" else "mean"
    heatmap_data = df_hm.groupby(["weekday", "hour"])["Sales"].agg(agg_func).reset_index()

    order_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data["weekday"] = pd.Categorical(
        heatmap_data["weekday"], categories=order_days, ordered=True,
    )
    pivot = heatmap_data.pivot(index="weekday", columns="hour", values="Sales").fillna(0)

    label_color = f"Ventas {'Total' if hm_mode == 'Total' else 'Promedio'} ($)"
    fig_hm = px.imshow(
        pivot,
        labels=dict(x="Hora del Dia", y="Dia de la Semana", color=label_color),
        aspect="auto",
        color_continuous_scale="Viridis",
        text_auto=".0f",
    )
    apply_layout(fig_hm, xaxis=dict(side="top"),
                 title=f"Intensidad de Ventas por Dia y Hora ({hm_mode})")
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("---")

    # ---------- CLUSTERING ----------
    st.markdown(f'<p style="font-weight:600;font-size:1.1rem;margin-bottom:4px">'
                f'Segmentacion de Clientes (K-Means)</p>', unsafe_allow_html=True)
    st.caption(
        "Nota: Se agrupa por Invoice ID, que no necesariamente representa un cliente unico. "
        "Los resultados son orientativos."
    )

    if SKLEARN_AVAILABLE:
        customer = (
            df_filtered.groupby("Invoice ID")
            .agg({"Sales": "sum", "Quantity": "sum", "Rating": "mean"})
            .reset_index()
        )
        customer.columns = ["invoice", "total_sales", "total_qty", "avg_rating"]

        max_k = min(6, len(customer) - 1) if len(customer) > 2 else 2

        if len(customer) < 3:
            st.warning("No hay suficientes datos para clustering con los filtros actuales.")
        else:
            k = st.slider("Numero de clusters (k)", 2, max_k, min(3, max_k))

            scaler = StandardScaler()
            X = scaler.fit_transform(customer[["total_sales", "total_qty", "avg_rating"]])

            kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
            customer["cluster"] = kmeans.fit_predict(X).astype(str)

            sil = silhouette_score(X, customer["cluster"]) if k < len(customer) else 0.0

            col_sil, _ = st.columns([1, 3])
            with col_sil:
                st.metric("Silhouette Score", f"{sil:.3f}")

            fig_cl = px.scatter_3d(
                customer, x="total_sales", y="total_qty", z="avg_rating",
                color="cluster", title=f"Clusters de Clientes (k={k})",
                color_discrete_sequence=PALETTE,
            )
            apply_layout(fig_cl)
            st.plotly_chart(fig_cl, use_container_width=True)

            # Elbow
            st.markdown(f'<p style="font-weight:600;font-size:1rem;margin:16px 0 8px">'
                        f'Grafico de Codo (Elbow)</p>', unsafe_allow_html=True)
            max_elbow = min(8, len(customer) - 1)
            if max_elbow >= 2:
                inertias = []
                k_range = list(range(2, max_elbow + 1))
                for ki in k_range:
                    km = KMeans(n_clusters=ki, n_init=10, random_state=42)
                    km.fit(X)
                    inertias.append(km.inertia_)

                fig_elbow = px.line(
                    x=k_range, y=inertias, markers=True,
                    title="Metodo del Codo",
                    labels={"x": "k (clusters)", "y": "Inercia"},
                )
                fig_elbow.update_traces(
                    line=dict(width=2.5, color=COLORS["accent2"]),
                    marker=dict(size=8, color=COLORS["accent2"]),
                )
                apply_layout(fig_elbow)
                st.plotly_chart(fig_elbow, use_container_width=True)

            st.markdown(f'<p style="font-weight:600;font-size:1rem;margin:16px 0 8px">'
                        f'Detalle por Cluster</p>', unsafe_allow_html=True)
            st.dataframe(customer, use_container_width=True)
    else:
        st.warning("scikit-learn no esta instalado. Instala con: `pip install scikit-learn`")

# ===================== TAB 5: Datos =====================
with tabs[5]:
    st.markdown(f'<p style="color:{COLORS["text_muted"]};font-size:0.9rem;margin-bottom:12px">'
                f'Mostrando <b>{len(df_filtered):,}</b> registros filtrados</p>',
                unsafe_allow_html=True)

    st.dataframe(df_filtered, use_container_width=True, height=420)

    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar datos filtrados (CSV)",
        data=csv,
        file_name="supermarket_datos_filtrados.csv",
        mime="text/csv",
    )

# ==============================================
# PIE DE PAGINA
# ==============================================
st.markdown(
    '''
    <div class="glass-footer">
        <p>Dashboard desarrollado con
        <a href="https://streamlit.io" target="_blank">Streamlit</a>,
        <a href="https://plotly.com" target="_blank">Plotly</a> y
        <a href="https://scikit-learn.org" target="_blank">scikit-learn</a>
        </p>
    </div>
    ''',
    unsafe_allow_html=True,
)
