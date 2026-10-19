"""Data access layer supporting DuckDB and SQLite for high-performance OLAP queries."""
import sqlite3
from datetime import timedelta
from typing import Optional, Tuple
import pandas as pd
import streamlit as st

from src.core.config import CSV_PATH, DUCKDB_PATH, SQLITE_PATH, DATABASE_DIR

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


def init_database() -> bool:
    """Ensure database directory exists and tables are populated in DuckDB and SQLite."""
    if not CSV_PATH.exists():
        return False

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Initialize SQLite (for backward compatibility)
    try:
        conn_sq = sqlite3.connect(str(SQLITE_PATH))
        df_raw = pd.read_csv(CSV_PATH)
        df_raw.to_sql("sales", conn_sq, if_exists="replace", index=False)
        conn_sq.close()
    except Exception as e:
        print(f"Warning: Failed to populate SQLite: {e}")

    # 2. Initialize DuckDB (for modern high-speed analytics)
    if DUCKDB_AVAILABLE:
        try:
            con = duckdb.connect(str(DUCKDB_PATH))
            con.execute(f"CREATE OR REPLACE TABLE sales AS SELECT * FROM read_csv_auto('{CSV_PATH.as_posix()}')")
            con.close()
        except Exception as e:
            print(f"Warning: Failed to populate DuckDB: {e}")

    return True


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load and prepare supermarket transactions with consistent data types."""
    df: Optional[pd.DataFrame] = None

    # Try DuckDB first
    if DUCKDB_AVAILABLE and DUCKDB_PATH.exists():
        try:
            con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
            df = con.execute("SELECT * FROM sales").fetchdf()
            con.close()
        except Exception:
            df = None

    # Fallback to SQLite
    if df is None and SQLITE_PATH.exists():
        try:
            conn = sqlite3.connect(str(SQLITE_PATH))
            df = pd.read_sql_query("SELECT * FROM sales", conn)
            conn.close()
        except Exception:
            df = None

    # Fallback directly to CSV
    if df is None and CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)

    if df is None or df.empty:
        # Attempt auto-init
        if init_database() and CSV_PATH.exists():
            df = pd.read_csv(CSV_PATH)
        else:
            return pd.DataFrame()

    # Data transformation and cleaning
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Extract Hour robustly from 12-hour or 24-hour formats
    if "Time" in df.columns:
        parsed_hour = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.hour
        if parsed_hour.isna().sum() > len(df) * 0.4:
            parsed_hour = pd.to_datetime(df["Time"], format="%I:%M:%S %p", errors="coerce").dt.hour
        df["Hour"] = parsed_hour.fillna(12).astype(int)
    else:
        df["Hour"] = 12

    df["DayName"] = df["Date"].dt.day_name()
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["MonthYear"] = df["Date"].dt.to_period("M").astype(str)
    df["Net Profit"] = df["gross income"]

    return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Compute executive KPI metrics for the given dataframe."""
    if df.empty:
        return {
            "total_sales": 0.0,
            "transactions": 0,
            "total_profit": 0.0,
            "avg_margin": 0.0,
            "avg_ticket": 0.0,
            "avg_rating": 0.0,
            "branches_count": 0,
            "units_sold": 0,
        }

    total_sales = float(df["Sales"].sum())
    transactions = int(len(df))
    total_profit = float(df["gross income"].sum())
    avg_margin = float(df["gross margin percentage"].mean())
    avg_ticket = total_sales / transactions if transactions > 0 else 0.0
    avg_rating = float(df["Rating"].mean())
    branches_count = int(df["Branch"].nunique())
    units_sold = int(df["Quantity"].sum())

    return {
        "total_sales": total_sales,
        "transactions": transactions,
        "total_profit": total_profit,
        "avg_margin": avg_margin,
        "avg_ticket": avg_ticket,
        "avg_rating": avg_rating,
        "branches_count": branches_count,
        "units_sold": units_sold,
    }


def calculate_previous_period(
    df_full: pd.DataFrame,
    start_date,
    end_date,
    filters: dict,
) -> Tuple[pd.DataFrame, Optional[str]]:
    """Filter records for the prior period of equivalent duration if available."""
    if not (start_date and end_date and start_date <= end_date):
        return pd.DataFrame(), None

    duration = pd.Timestamp(end_date) - pd.Timestamp(start_date)
    prev_end = pd.Timestamp(start_date) - timedelta(days=1)
    prev_start = prev_end - duration

    # If the prior period starts before the dataset minimum, no full prior period exists
    if prev_start < df_full["Date"].min():
        return pd.DataFrame(), None

    mask = (df_full["Date"] >= prev_start) & (df_full["Date"] <= prev_end)
    prev_df = df_full[mask].copy()

    for col, values in filters.items():
        if col in prev_df.columns and values:
            prev_df = prev_df[prev_df[col].isin(values)]

    if not prev_df.empty:
        return prev_df, "vs período anterior"

    return pd.DataFrame(), None


def format_delta_pct(current: float, previous: Optional[float], suffix: str = "%") -> Tuple[Optional[str], str]:
    """Return formatted delta string and status ('positive', 'negative', 'neutral')."""
    if previous is None or previous == 0:
        return None, "neutral"

    pct = ((current - previous) / abs(previous)) * 100
    if pct > 0:
        return f"+{pct:.1f}{suffix}", "positive"
    elif pct < 0:
        return f"{pct:.1f}{suffix}", "negative"
    else:
        return f"0.0{suffix}", "neutral"
