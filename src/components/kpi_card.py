"""Executive KPI Card Component with Interactive Drilldowns & Micro-Interactions."""
from typing import Optional, Any, Dict, List, Tuple
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
    drilldown_data: Optional[Dict[str, Any]] = None,
    interactive_icon: str = ":material/insights:",
) -> None:
    """Render a modern native Streamlit metric card with built-in sparkline, border,

    and optional interactive popover drilldown.
    """
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

    if drilldown_data:
        with st.container(border=True):
            col_metric, col_action = st.columns([0.84, 0.16], vertical_alignment="top")
            with col_metric:
                st.metric(
                    label=title,
                    value=value,
                    delta=clean_delta,
                    delta_description=desc,
                    border=False,
                    icon=mat_icon,
                    chart_data=chart_data,
                    chart_type=chart_type,
                    help=help_text,
                )
            with col_action:
                with st.popover(
                    "",
                    icon=interactive_icon,
                    help="Clic para ver desglose interactivo",
                    use_container_width=True,
                ):
                    pop_title = drilldown_data.get("title", title)
                    pop_sub = drilldown_data.get("subtitle", "Desglose y analítica interactiva")
                    st.markdown(f"#### {pop_title}")
                    if pop_sub:
                        st.caption(pop_sub)

                    items = drilldown_data.get("items", [])
                    if items:
                        st.divider()
                        for it in items:
                            col_k, col_v = st.columns([1.3, 1.0])
                            col_k.caption(str(it[0]))
                            val_txt = f"**{it[1]}**"
                            if len(it) > 2 and it[2]:
                                val_txt += f"  ·  `{it[2]}`"
                            col_v.markdown(val_txt)

                    if "stats" in drilldown_data and isinstance(drilldown_data["stats"], dict):
                        st.divider()
                        stat_cols = st.columns(len(drilldown_data["stats"]))
                        for col_s, (s_label, s_val) in zip(stat_cols, drilldown_data["stats"].items()):
                            col_s.metric(s_label, s_val)

                    if "tip" in drilldown_data and drilldown_data["tip"]:
                        st.info(drilldown_data["tip"], icon=":material/lightbulb:")
    else:
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
    action_content: Optional[str] = None,
) -> None:
    """Render an executive highlight callout banner with optional interactive popover action."""
    mat_icon = icon
    icon_map = {
        "💡": ":material/lightbulb:",
        "⚡": ":material/bolt:",
        "🧠": ":material/psychology:",
        "🛡️": ":material/security:",
        "🏆": ":material/emoji_events:",
        "✅": ":material/check_circle:",
        "⚠️": ":material/warning:",
    }
    mat_icon = icon_map.get(icon, icon)

    with st.container(border=True):
        if action_content:
            col_c1, col_c2 = st.columns([0.9, 0.1], vertical_alignment="center")
            with col_c1:
                st.markdown(f"**{mat_icon} {title}**")
                st.markdown(message)
            with col_c2:
                with st.popover("", icon=":material/info:", help="Ver detalles adicionales"):
                    st.markdown("#### Detalle Operativo")
                    st.markdown(action_content)
        else:
            st.markdown(f"**{mat_icon} {title}**")
            st.markdown(message)
