"""Standardized, high-aesthetic Plotly charts for retail analytics."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.core.config import COLORS, PALETTE, COLORSCALE_MONEY, COLORSCALE_PROFIT
from src.core.theme import apply_theme


def plot_revenue_trend(df: pd.DataFrame, freq: str = "D", by_branch: bool = False) -> go.Figure:
    """Generate modern sales trend line chart."""
    freq_code = "D" if freq == "Daily" else "W"
    
    if by_branch:
        grouped = (
            df.groupby([pd.Grouper(key="Date", freq=freq_code), "Branch"])["Sales"]
            .sum()
            .reset_index()
        )
        fig = px.line(
            grouped,
            x="Date",
            y="Sales",
            color="Branch",
            title="Tendencia de Ventas por Sucursal",
            markers=True,
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(
            line=dict(width=2.5),
            marker=dict(size=5),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Venta: $%{y:,.2f}<extra></extra>",
        )
    else:
        grouped = (
            df.groupby(pd.Grouper(key="Date", freq=freq_code))["Sales"]
            .sum()
            .reset_index()
        )
        fig = px.area(
            grouped,
            x="Date",
            y="Sales",
            title="Evolución Temporal de Ingresos",
            markers=True,
        )
        fig.update_traces(
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=5, color=COLORS["primary_light"]),
            fillcolor="rgba(99, 102, 241, 0.12)",
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Ingresos: $%{y:,.2f}<extra></extra>",
        )

    return apply_theme(fig)


def plot_category_margin_bar(df: pd.DataFrame) -> go.Figure:
    """Create stacked or grouped category sales and profit comparison."""
    summary = (
        df.groupby("Product line")
        .agg(Ventas=("Sales", "sum"), Margen=("gross income", "sum"))
        .reset_index()
        .sort_values("Ventas", ascending=True)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=summary["Product line"],
            x=summary["Ventas"],
            name="Ventas Totales",
            orientation="h",
            marker=dict(
                color=COLORS["primary"],
                line=dict(color="rgba(255,255,255,0.1)", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Ventas: $%{x:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=summary["Product line"],
            x=summary["Margen"],
            name="Ganancia Bruta",
            orientation="h",
            marker=dict(
                color=COLORS["emerald"],
                line=dict(color="rgba(255,255,255,0.1)", width=1),
            ),
            hovertemplate="<b>%{y}</b><br>Ganancia: $%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        title=dict(text="Desempeño por Categoría: Ventas vs Margen Bruto"),
        xaxis_title="Monto ($)",
        yaxis_title="",
    )
    return apply_theme(fig)


def plot_customer_distribution_donuts(df: pd.DataFrame):
    """Return two donut charts: Customer Type and Payment Method."""
    # 1. Customer Type
    ctype = df.groupby("Customer type")["Sales"].sum().reset_index()
    fig_cust = px.pie(
        ctype,
        names="Customer type",
        values="Sales",
        hole=0.6,
        title="Participación: Miembro vs Normal",
        color_discrete_sequence=[COLORS["primary"], COLORS["emerald"]],
    )
    fig_cust.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#0B0F19", width=2)),
        hovertemplate="<b>%{label}</b>: $%{value:,.2f} (%{percent})<extra></extra>",
    )
    apply_theme(fig_cust)

    # 2. Payment Method
    payment = df.groupby("Payment")["Sales"].sum().reset_index()
    fig_pay = px.pie(
        payment,
        names="Payment",
        values="Sales",
        hole=0.6,
        title="Canales de Pago",
        color_discrete_sequence=[COLORS["primary_light"], COLORS["cyan"], COLORS["amber"]],
    )
    fig_pay.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#0B0F19", width=2)),
        hovertemplate="<b>%{label}</b>: $%{value:,.2f} (%{percent})<extra></extra>",
    )
    apply_theme(fig_pay)

    return fig_cust, fig_pay


def plot_sales_heatmap(df: pd.DataFrame, metric: str = "Total") -> go.Figure:
    """Create Day-of-Week x Hour sales intensity heatmap."""
    agg_func = "sum" if metric == "Total" else "mean"
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    pivot = (
        df.groupby(["DayName", "Hour"])["Sales"]
        .agg(agg_func)
        .reset_index()
    )
    pivot["DayName"] = pd.Categorical(pivot["DayName"], categories=days_order, ordered=True)
    pivot_table = pivot.pivot(index="DayName", columns="Hour", values="Sales").fillna(0)

    fig = px.imshow(
        pivot_table,
        labels=dict(x="Hora del Día", y="Día de la Semana", color=f"Ventas {metric} ($)"),
        aspect="auto",
        color_continuous_scale="Viridis",
        text_auto=".0f",
        title=f"Mapa de Calor de Intensidad Comercial ({metric})",
    )
    fig.update_xaxes(side="top")
    return apply_theme(fig)


def plot_capital_flow_sankey(df: pd.DataFrame) -> go.Figure:
    """Generate an interactive Sankey diagram of capital flow: Branch -> Product Line -> Payment."""
    branches = sorted(df["Branch"].unique().tolist())
    products = sorted(df["Product line"].unique().tolist())
    payments = sorted(df["Payment"].unique().tolist())

    nodes = branches + products + payments
    node_indices = {name: i for i, name in enumerate(nodes)}

    sources: list[int] = []
    targets: list[int] = []
    values: list[float] = []

    # Branch -> Product Line
    bp = df.groupby(["Branch", "Product line"])["Sales"].sum().reset_index()
    for _, row in bp.iterrows():
        sources.append(node_indices[row["Branch"]])
        targets.append(node_indices[row["Product line"]])
        values.append(float(row["Sales"]))

    # Product Line -> Payment
    pp = df.groupby(["Product line", "Payment"])["Sales"].sum().reset_index()
    for _, row in pp.iterrows():
        sources.append(node_indices[row["Product line"]])
        targets.append(node_indices[row["Payment"]])
        values.append(float(row["Sales"]))

    node_colors = (
        ["#6366F1"] * len(branches)
        + ["#06B6D4"] * len(products)
        + ["#10B981"] * len(payments)
    )

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=18,
                    thickness=20,
                    line=dict(color="rgba(255, 255, 255, 0.2)", width=1),
                    label=nodes,
                    color=node_colors,
                    hovertemplate="<b>%{label}</b><br>Volumen total: $%{value:,.2f}<extra></extra>",
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(99, 102, 241, 0.22)",
                    hovertemplate="Flujo: <b>%{source.label}</b> ➔ <b>%{target.label}</b><br>Monto: $%{value:,.2f}<extra></extra>",
                ),
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Diagrama de Sankey: Flujo de Dinero (Sucursal ➔ Categoría ➔ Medio de Pago)"),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#F8FAFC"),
        margin=dict(l=10, r=10, t=40, b=20),
    )
    return apply_theme(fig)


def plot_branch_radar_benchmark(df: pd.DataFrame) -> go.Figure:
    """Generate a multi-dimensional radar benchmark chart comparing all branches."""
    branch_agg = df.groupby("Branch").agg(
        Sales=("Sales", "sum"),
        GrossIncome=("gross income", "sum"),
        Rating=("Rating", "mean"),
        Quantity=("Quantity", "sum"),
        Tx=("Invoice ID", "count"),
    ).reset_index()

    branch_agg["AvgTicket"] = branch_agg["Sales"] / branch_agg["Tx"]

    metrics = ["Sales", "GrossIncome", "Rating", "Quantity", "AvgTicket"]
    labels = ["Ventas ($)", "Ganancia ($)", "Satisfacción ⭐", "Volumen Uds.", "Ticket Prom. ($)"]

    # Normalize 20 - 100 for visual balance on radar
    norm_df = branch_agg.copy()
    for m in metrics:
        min_v = norm_df[m].min()
        max_v = norm_df[m].max()
        rng = max_v - min_v if max_v != min_v else 1.0
        norm_df[m] = 20 + ((norm_df[m] - min_v) / rng) * 80

    fig = go.Figure()
    colors = [COLORS["primary"], COLORS["emerald"], COLORS["amber"], COLORS["cyan"]]

    for idx, (_, row) in enumerate(norm_df.iterrows()):
        vals = [float(row[m]) for m in metrics]
        vals.append(vals[0])  # close polygon
        b_name = row["Branch"]
        c = colors[idx % len(colors)]
        
        # Real values for hover
        real_row = branch_agg[branch_agg["Branch"] == b_name].iloc[0]
        hover_txt = (
            f"<b>Sucursal {b_name}</b><br>"
            f"Ventas: ${real_row['Sales']:,.2f}<br>"
            f"Ganancia: ${real_row['GrossIncome']:,.2f}<br>"
            f"Satisfacción: {real_row['Rating']:.2f}/10<br>"
            f"Volumen: {int(real_row['Quantity']):,} uds<br>"
            f"Ticket: ${real_row['AvgTicket']:.2f}<extra></extra>"
        )

        fig.add_trace(
            go.Scatterpolar(
                r=vals,
                theta=labels + [labels[0]],
                fill="toself",
                name=f"Sucursal {b_name}",
                line=dict(color=c, width=2.5),
                fillcolor=c.replace("rgb", "rgba").replace(")", ", 0.18)") if "rgb" in c else "rgba(99, 102, 241, 0.15)",
                hoverinfo="text",
                hovertext=hover_txt,
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 105], showticklabels=False, gridcolor="rgba(255,255,255,0.08)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.15)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(text="Benchmark Multidimensional de Sucursales (Radar Index)"),
        showlegend=True,
    )
    return apply_theme(fig)


def plot_target_gauge(
    current_val: float,
    target_val: float,
    title: str,
    suffix: str = "%",
    max_range: float = 10.0,
) -> go.Figure:
    """Generate a sleek speedometer / gauge chart comparing current value vs target."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=current_val,
            number={"suffix": suffix, "font": {"size": 28, "color": "#F8FAFC"}},
            delta={
                "reference": target_val,
                "position": "bottom",
                "suffix": suffix,
                "increasing": {"color": COLORS["emerald"]},
                "decreasing": {"color": COLORS["rose"]},
            },
            title={"text": f"<b>{title}</b><br><span style='font-size:0.75em;color:#94A3B8'>Meta: {target_val}{suffix}</span>", "font": {"size": 14, "color": "#E2E8F0"}},
            gauge={
                "axis": {"range": [0, max_range], "tickwidth": 1, "tickcolor": "rgba(255,255,255,0.2)"},
                "bar": {"color": COLORS["primary"], "thickness": 0.28},
                "bgcolor": "rgba(255, 255, 255, 0.05)",
                "borderwidth": 1,
                "bordercolor": "rgba(255, 255, 255, 0.1)",
                "steps": [
                    {"range": [0, target_val * 0.8], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [target_val * 0.8, target_val], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [target_val, max_range], "color": "rgba(16, 185, 129, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#10B981", "width": 3},
                    "thickness": 0.8,
                    "value": target_val,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        height=220,
    )
    return fig
