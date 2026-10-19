"""Retail AI Copilot Page for conversational data querying and automated insights."""
import streamlit as st
import pandas as pd

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.theme import load_css
from src.data.db import load_data
from src.components.filters import render_sidebar_filters


def answer_retail_question(query: str, df: pd.DataFrame) -> str:
    """Analyze query and calculate dynamic insights from the current dataset."""
    q = query.lower()

    if "rentable" in q or "margen" in q or "ganancia" in q:
        cat_profit = df.groupby("Product line")["gross income"].sum().sort_values(ascending=False)
        top_cat = cat_profit.index[0]
        top_amt = cat_profit.iloc[0]
        branch_margin = df.groupby("Branch")["gross income"].sum().sort_values(ascending=False)
        return (
            f"📊 **Análisis de Rentabilidad y Margen:**\n\n"
            f"- La categoría con mayor ganancia bruta acumulada es **{top_cat}** con **${top_amt:,.2f}**.\n"
            f"- La sucursal con mejor contribución marginal es **{branch_margin.index[0]}** con **${branch_margin.iloc[0]:,.2f}**.\n"
            f"- El margen promedio general de la cadena se ubica en **{df['gross margin percentage'].mean():.2f}%**."
        )

    elif "ticket" in q or "promedio" in q:
        avg_overall = df["Sales"].mean()
        avg_member = df[df["Customer type"] == "Member"]["Sales"].mean()
        avg_normal = df[df["Customer type"] == "Normal"]["Sales"].mean()
        top_branch = df.groupby("Branch")["Sales"].mean().sort_values(ascending=False)
        return (
            f"🎫 **Ticket Promedio Comercial:**\n\n"
            f"- **Ticket Promedio Global:** ${avg_overall:.2f}\n"
            f"- **Clientes Miembro:** ${avg_member:.2f}\n"
            f"- **Clientes Regulares (Normal):** ${avg_normal:.2f}\n"
            f"- La sucursal con el ticket unitario más elevado es **Sucursal {top_branch.index[0]}** (${top_branch.iloc[0]:.2f})."
        )

    elif "horario" in q or "hora" in q or "dia" in q or "pico" in q:
        hour_sales = df.groupby("Hour")["Sales"].sum().sort_values(ascending=False)
        day_sales = df.groupby("DayName")["Sales"].sum().sort_values(ascending=False)
        return (
            f"⏰ **Patrones Horarios y Días Pico:**\n\n"
            f"- La **hora pico comercial** de mayor volumen de facturación son las **{hour_sales.index[0]}:00 hrs** (${hour_sales.iloc[0]:,.2f}).\n"
            f"- El **día de mayor actividad** comercial es el **{day_sales.index[0]}** con ${day_sales.iloc[0]:,.2f} en ventas.\n"
            f"- *Recomendación operativa:* Incrementar personal de cajas y reposición entre las 12:00 y las 15:00 hrs y entre 18:00 y 20:00 hrs."
        )

    elif "pago" in q or "medio de pago" in q or "wallet" in q:
        pay_summary = df.groupby(["Payment", "Customer type"])["Sales"].sum().unstack().fillna(0)
        top_pay = df.groupby("Payment")["Sales"].sum().sort_values(ascending=False)
        return (
            f"💳 **Comportamiento de Medios de Pago:**\n\n"
            f"- El método más utilizado en volumen total es **{top_pay.index[0]}** con **${top_pay.iloc[0]:,.2f}**.\n"
            f"- Los clientes Miembros prefieren principalmente pagos digitales (Ewallet/Credit card).\n"
            f"- *Recomendación:* Ofrecer promociones exclusivas y cashback en billeteras digitales para incentivar la recurrencia."
        )

    else:
        tot_sales = df["Sales"].sum()
        tot_tx = len(df)
        top_cat = df.groupby("Product line")["Sales"].sum().idxmax()
        top_branch = df.groupby("Branch")["Sales"].sum().idxmax()
        return (
            f"🤖 **Diagnóstico General Asistido por IA:**\n\n"
            f"Para los registros filtrados ({tot_tx:,} transacciones):\n"
            f"- **Ingresos Totales:** ${tot_sales:,.2f}\n"
            f"- **Sucursal Líder:** {top_branch}\n"
            f"- **Categoría Estrella:** {top_cat}\n"
            f"- **Calificación Promedio:** {df['Rating'].mean():.2f} / 10\n\n"
            f"Puedes hacerme preguntas más específicas sobre: *márgenes por categoría, horas pico de venta, tickets de miembros o medios de pago*."
        )


def render_ai_copilot_page():
    load_css()
    df_raw = load_data()

    if df_raw.empty:
        st.error("No se encontraron datos disponibles.")
        return

    df, filters = render_sidebar_filters(df_raw)

    st.markdown(
        """
        <div class="executive-header">
            <div class="executive-header-left">
                <h1>Retail AI Copilot — Consultas en Lenguaje Natural</h1>
                <p>Asistente analítico inteligente para responder dudas comerciales e interpretar tendencias</p>
            </div>
            <div>
                <span class="badge-status">AI Assistant Activo</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize chat history
    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = [
            {
                "role": "assistant",
                "content": (
                    "¡Hola! Soy tu **Retail AI Copilot**. Puedes preguntarme sobre tendencias de venta, "
                    "márgenes de producto, comportamiento de clientes o recomendaciones para optimizar tus sucursales."
                ),
            }
        ]

    # Quick Question Chips using native st.pills
    st.markdown("##### 💡 Preguntas frecuentes:")
    pill_options = [
        "📈 ¿Línea más rentable?",
        "🎫 ¿Ticket de miembros vs regulares?",
        "⏰ ¿Horarios y días pico?",
        "💳 ¿Medios de pago preferidos?",
    ]
    selected_pill = st.pills("Preguntas sugeridas", pill_options, label_visibility="collapsed")

    pill_query_map = {
        "📈 ¿Línea más rentable?": "¿Cuál fue la categoría más rentable y con mayor margen?",
        "🎫 ¿Ticket de miembros vs regulares?": "¿Cuál es el ticket promedio de miembros vs regulares?",
        "⏰ ¿Horarios y días pico?": "¿Cuáles son las horas y días de mayor afluencia y ventas?",
        "💳 ¿Medios de pago preferidos?": "¿Cuáles son los métodos de pago preferidos?",
    }
    quick_query = pill_query_map.get(selected_pill) if selected_pill else None

    # Display Chat History
    for msg in st.session_state.copilot_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle user interaction
    user_input = st.chat_input("Escribe tu consulta analítica sobre las ventas...") or quick_query

    if user_input:
        st.session_state.copilot_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response = answer_retail_question(user_input, df)

        st.session_state.copilot_messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)


if __name__ == "__main__" or "page" in __name__:
    render_ai_copilot_page()
