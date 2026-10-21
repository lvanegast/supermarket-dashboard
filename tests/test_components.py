"""Test UI Components and Interactive KPI Card behavior."""
from unittest.mock import patch, MagicMock
from src.components.kpi_card import render_kpi_card, render_insight_callout


@patch("streamlit.metric")
def test_render_kpi_card_standard(mock_metric):
    """Test standard KPI card without drilldown calls st.metric."""
    render_kpi_card(
        title="Test Metric",
        value="$1,234.00",
        icon="💰",
        delta_str="+5.2%",
        delta_status="positive",
        subtitle="vs prev",
    )
    mock_metric.assert_called_once()
    kwargs = mock_metric.call_args[1]
    assert kwargs["label"] == "Test Metric"
    assert kwargs["value"] == "$1,234.00"
    assert kwargs["delta"] == "+5.2%"
    assert kwargs["icon"] == ":material/payments:"
    assert kwargs["border"] is True


@patch("streamlit.container")
@patch("streamlit.columns")
@patch("streamlit.metric")
def test_render_kpi_card_with_drilldown(mock_metric, mock_columns, mock_container):
    """Test KPI card with interactive drilldown renders container and action button."""
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_columns.return_value = (mock_col1, mock_col2)

    drilldown = {
        "title": "Desglose de Ventas",
        "items": [("Sucursal A", "$100", "50%")],
        "stats": {"Promedio": "$50"},
        "tip": "Tip de prueba",
    }

    render_kpi_card(
        title="Ventas",
        value="$200",
        icon=":material/payments:",
        drilldown_data=drilldown,
        interactive_icon=":material/insights:",
    )

    mock_container.assert_called_with(border=True)


@patch("streamlit.container")
@patch("streamlit.markdown")
def test_render_insight_callout(mock_markdown, mock_container):
    """Test insight callout banner rendering."""
    render_insight_callout(
        title="Diagnóstico de Prueba",
        message="Mensaje de prueba",
        icon="⚡",
    )
    mock_container.assert_called_with(border=True)
