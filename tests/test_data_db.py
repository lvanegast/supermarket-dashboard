"""Unit tests for data access and KPI calculations."""
import pytest
import pandas as pd
from src.data.db import (
    init_database,
    load_data,
    calculate_kpis,
    format_delta_pct,
    calculate_previous_period,
)


def test_init_database():
    assert init_database() is True


def test_load_data():
    df = load_data()
    assert not df.empty
    assert "Sales" in df.columns
    assert "gross income" in df.columns
    assert "Hour" in df.columns
    assert "DayName" in df.columns
    assert len(df) == 1000


def test_calculate_kpis():
    df = load_data()
    kpis = calculate_kpis(df)
    assert kpis["total_sales"] > 0
    assert kpis["transactions"] == 1000
    assert kpis["branches_count"] == 3
    assert kpis["avg_ticket"] > 0


def test_format_delta_pct():
    delta_str, status = format_delta_pct(120.0, 100.0)
    assert delta_str == "+20.0%"
    assert status == "positive"

    delta_str, status = format_delta_pct(80.0, 100.0)
    assert delta_str == "-20.0%"
    assert status == "negative"


def test_calculate_previous_period():
    df = load_data()
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    # Full range should not invent a prior period outside dataset bounds
    prev_df, label = calculate_previous_period(df, min_date, max_date, {})
    assert prev_df.empty
    assert label is None

    # Partial range with valid preceding data
    sub_start = pd.Timestamp("2019-02-01").date()
    sub_end = pd.Timestamp("2019-02-28").date()
    prev_sub, label_sub = calculate_previous_period(df, sub_start, sub_end, {})
    assert not prev_sub.empty
    assert label_sub == "vs período anterior"
