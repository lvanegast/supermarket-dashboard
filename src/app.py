"""SuperMarket Analytics Pro — Modern Multi-Page Architecture.
Executive Retail Intelligence & Demand Forecasting Dashboard.
"""
import sys
from pathlib import Path

# Add project root to sys.path so 'src' and absolute imports resolve cleanly
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

# Setup Page Configuration
st.set_page_config(
    page_title="SuperMarket Analytics Pro",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database if needed
from src.data.db import init_database
from src.core.theme import load_css

init_database()
load_css()

# Pages definition
SRC_DIR = Path(__file__).resolve().parent
PAGES_DIR = SRC_DIR / "pages"

pages = {
    "Tablero principal": [
        st.Page(
            str(PAGES_DIR / "1_📊_Overview.py"),
            title="Panel ejecutivo",
            icon=":material/dashboard:",
            default=True,
        ),
    ],
    "Analítica avanzada e IA": [
        st.Page(
            str(PAGES_DIR / "2_📈_Forecast.py"),
            title="Pronóstico y demanda",
            icon=":material/trending_up:",
        ),
        st.Page(
            str(PAGES_DIR / "3_🛒_Products_Basket.py"),
            title="Productos y canasta",
            icon=":material/shopping_cart:",
        ),
        st.Page(
            str(PAGES_DIR / "4_👥_Customers_RFM.py"),
            title="Clientes y segmentación",
            icon=":material/group:",
        ),
        st.Page(
            str(PAGES_DIR / "5_🤖_AI_Copilot.py"),
            title="Retail AI copilot",
            icon=":material/smart_toy:",
        ),
        st.Page(
            str(PAGES_DIR / "6_⚡_What_If_Simulator.py"),
            title="Simulador what-if",
            icon=":material/tune:",
        ),
    ],
    "Datos y administración": [
        st.Page(
            str(PAGES_DIR / "7_📥_Data_Explorer.py"),
            title="Explorador y SQL",
            icon=":material/database:",
        ),
    ],
}

# Run Streamlit Multi-Page Navigation
pg = st.navigation(pages)
pg.run()
