"""Unit tests for ML and analytical models."""
import pytest
import pandas as pd
from src.data.db import load_data
from src.models.forecasting import generate_demand_forecast, calculate_safety_stock_matrix
from src.models.basket_analysis import calculate_basket_association_rules
from src.models.rfm_clustering import calculate_rfm_segments


@pytest.fixture
def sample_data():
    return load_data()


def test_forecasting_model(sample_data):
    forecast_df, metrics = generate_demand_forecast(sample_data, horizon_days=14)
    assert not forecast_df.empty
    assert len(forecast_df) == 14
    assert "Forecast" in forecast_df.columns
    assert "Upper_Bound" in forecast_df.columns
    assert metrics["expected_revenue"] > 0


def test_safety_stock_matrix(sample_data):
    matrix = calculate_safety_stock_matrix(sample_data, lead_time_days=7)
    assert not matrix.empty
    assert "Punto de Reorden (ROP)" in matrix.columns
    assert "Stock de Seguridad (SS)" in matrix.columns
    assert len(matrix) == sample_data["Product line"].nunique()


def test_basket_analysis(sample_data):
    rules_df, matrix = calculate_basket_association_rules(sample_data, min_support=0.01, min_confidence=0.05)
    assert isinstance(rules_df, pd.DataFrame)
    assert isinstance(matrix, pd.DataFrame)
    assert matrix.shape[0] == sample_data["Product line"].nunique()


def test_rfm_clustering(sample_data):
    rfm_df, metrics, fig = calculate_rfm_segments(sample_data, n_clusters=3)
    assert not rfm_df.empty
    assert "Cluster" in rfm_df.columns
    assert "Segmento" in rfm_df.columns
    assert metrics["n_clusters"] == 3
    assert -1.0 <= metrics["silhouette_score"] <= 1.0
