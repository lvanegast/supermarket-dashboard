import streamlit as st
from src.core.config import CSS_PATH, COLORS, PALETTE


def load_css() -> None:
    """Inject the external glassmorphism CSS into the Streamlit app."""
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        # Minimal fallback if CSS file is moved
        st.markdown(
            """
            <style>
            .stApp { background-color: #0B0F19; color: #F8FAFC; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def get_plotly_layout(**extra) -> dict:
    """Return a unified, high-contrast, modern dark Plotly layout dictionary."""
    base_layout = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Plus Jakarta Sans, -apple-system, sans-serif",
            color=COLORS["text_primary"],
            size=12,
        ),
        margin=dict(l=24, r=20, t=44, b=32),
        title=dict(
            font=dict(size=15, color=COLORS["text_primary"], weight="bold"),
            x=0.01,
            xanchor="left",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=11, color=COLORS["text_secondary"]),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            linecolor="rgba(255, 255, 255, 0.1)",
            zerolinecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=11, color=COLORS["text_secondary"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            linecolor="rgba(255, 255, 255, 0.1)",
            zerolinecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=11, color=COLORS["text_secondary"]),
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#FFFFFF"),
        ),
        colorway=PALETTE,
    )
    base_layout.update(extra)
    return base_layout


def apply_theme(fig, **extra):
    """Update and return a Plotly figure with the standard executive theme."""
    fig.update_layout(**get_plotly_layout(**extra))
    return fig
