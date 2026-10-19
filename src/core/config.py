"""Configuration, constants, and paths for SuperMarket Analytics Pro."""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"
CSS_PATH = ASSETS_DIR / "css" / "glassmorphism.css"

CSV_PATH = DATA_DIR / "SuperMarket.csv"
DUCKDB_PATH = DATABASE_DIR / "sales.duckdb"
SQLITE_PATH = DATABASE_DIR / "sales.db"

# App Branding
APP_TITLE = "SuperMarket Analytics Pro"
APP_SUBTITLE = "Retail Intelligence & Demand Forecasting"
APP_ICON = "🛒"
APP_VERSION = "2.0.0"

# Executive Color Palette
COLORS = {
    "primary": "#6366F1",         # Indigo
    "primary_light": "#818CF8",   # Indigo Light
    "emerald": "#10B981",         # Success / Profit
    "emerald_light": "#34D399",
    "amber": "#F59E0B",           # Warning / Moderate
    "amber_light": "#FBBF24",
    "rose": "#F43F5E",            # Negative / Risk
    "rose_light": "#FB7185",
    "cyan": "#06B6D4",            # Operations / Info
    "cyan_light": "#22D3EE",
    "violet": "#8B5CF6",          # Accents
    "bg_main": "#0B0F19",         # Deep Slate Main Background
    "bg_card": "#111827",         # Glass Card Surface
    "bg_card_hover": "#1E293B",   # Card Hover
    "border_subtle": "rgba(255, 255, 255, 0.08)",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
}

# Standard categorical palette for Plotly charts
PALETTE = [
    "#6366F1", "#10B981", "#06B6D4", "#F59E0B", "#F43F5E",
    "#8B5CF6", "#EC4899", "#14B8A6", "#3B82F6", "#EAB308",
]

# Standard continuous color scale for monetary gradients
COLORSCALE_MONEY = ["#1E1B4B", "#4338CA", "#6366F1", "#818CF8", "#A5B4FC"]
COLORSCALE_PROFIT = ["#064E3B", "#047857", "#10B981", "#34D399", "#6EE7B7"]
COLORSCALE_WARNING = ["#451A03", "#78350F", "#D97706", "#F59E0B", "#FCD34D"]
