"""Executive KPI Card Component using modern native Streamlit st.metric."""
from typing import Optional, Any
import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    icon: Optional[str] = None,
    delta_str: Optional[str] = None,
    delta_status: str = "neutral",
    subtitle: Optional[str] = None,
    theme_color: str = "primary",
    chart_data: Optional[Any] = None,
    chart_type: str = "line",
    help_text: Optional[str] = None,
) -> None:
    """Render a modern native Streamlit metric card with built-in sparkline and border."""
    # Native Material symbol icon conversion if emoji provided
    mat_icon = icon
    if icon == "💰":
        mat_icon = ":material/payments:"
    elif icon == "🧾":
        mat_icon = ":material/receipt_long:"
    elif icon == "📈":
        mat_icon = ":material/trending_up:"
    elif icon == "🎫":
        mat_icon = ":material/confirmation_number:"
    elif icon == "📊":
        mat_icon = ":material/bar_chart:"
    elif icon == "⭐":
        mat_icon = ":material/star:"
    elif icon == "📦":
        mat_icon = ":material/inventory_2:"
    elif icon == "🏪":
        mat_icon = ":material/store:"

    # Only show delta if valid and not empty
    clean_delta = delta_str if (delta_str and delta_str != "N/A") else None
    desc = subtitle if clean_delta else None

    st.metric(
        label=title,
        value=value,
        delta=clean_delta,
        delta_description=desc,
        border=True,
        icon=mat_icon,
        chart_data=chart_data,
        chart_type=chart_type,
        help=help_text,
    )


def render_insight_callout(
    title: str,
    message: str,
    icon: str = ":material/lightbulb:",
) -> None:
    """Render an executive highlight callout banner using native container."""
    mat_icon = icon
    if icon in ["💡", "⚡", "🧠", "🛡️", "🏆", "✅", "⚠️"]:
        icon_map = {
            "💡": ":material/lightbulb:",
            "⚡": ":material/bolt:",
            "🧠": ":material/psychology:",
            "🛡️": ":material/security:",
            "🏆": ":material/emoji_events:",
            "✅": ":material/check_circle:",
            "⚠️": ":material/warning:",
        }
        mat_icon = icon_map.get(icon, ":material/info:")

    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.markdown(message)
