"""Market Basket Analysis and Association Rules engine for retail cross-selling."""
from itertools import combinations
from typing import Tuple, List, Dict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.core.config import COLORS, PALETTE
from src.core.theme import apply_theme


def calculate_basket_association_rules(
    df: pd.DataFrame,
    min_support: float = 0.05,
    min_confidence: float = 0.15,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Extract cross-category association rules and co-occurrence patterns."""
    # Group transactions by Invoice ID or Date-Hour trip
    # In this dataset, each row is a transaction. We can simulate basket co-occurrence
    # across shopping sessions (same date, hour and branch, or invoice group)
    basket_group = df.groupby(["Date", "Hour", "Branch"])["Product line"].apply(
        lambda s: list(set(s))
    ).reset_index()

    total_baskets = len(basket_group)
    if total_baskets == 0:
        return pd.DataFrame(), pd.DataFrame()

    # Item frequencies
    item_counts: Dict[str, int] = {}
    pair_counts: Dict[Tuple[str, str], int] = {}

    for items in basket_group["Product line"]:
        for item in items:
            item_counts[item] = item_counts.get(item, 0) + 1
        for pair in combinations(sorted(items), 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    # Build association rules table
    rules: List[dict] = []
    for (item_a, item_b), pair_freq in pair_counts.items():
        support_ab = pair_freq / total_baskets
        if support_ab < min_support:
            continue

        support_a = item_counts[item_a] / total_baskets
        support_b = item_counts[item_b] / total_baskets

        # Rule A -> B
        conf_a_b = support_ab / (support_a or 1e-6)
        lift_a_b = conf_a_b / (support_b or 1e-6)

        # Rule B -> A
        conf_b_a = support_ab / (support_b or 1e-6)
        lift_b_a = conf_b_a / (support_a or 1e-6)

        rules.append({
            "Producto Antecedente": item_a,
            "Producto Consecuente": item_b,
            "Soporte": round(support_ab, 3),
            "Confianza": round(conf_a_b, 3),
            "Elevación (Lift)": round(lift_a_b, 2),
            "Frecuencia Co-compra": pair_freq,
        })
        rules.append({
            "Producto Antecedente": item_b,
            "Producto Consecuente": item_a,
            "Soporte": round(support_ab, 3),
            "Confianza": round(conf_b_a, 3),
            "Elevación (Lift)": round(lift_b_a, 2),
            "Frecuencia Co-compra": pair_freq,
        })

    rules_df = pd.DataFrame(rules)
    if not rules_df.empty:
        rules_df = rules_df[rules_df["Confianza"] >= min_confidence].sort_values(
            "Elevación (Lift)", ascending=False
        )

    # Build co-occurrence matrix for heatmap
    unique_items = sorted(list(item_counts.keys()))
    matrix = pd.DataFrame(0, index=unique_items, columns=unique_items)
    for (i_a, i_b), count in pair_counts.items():
        matrix.loc[i_a, i_b] = count
        matrix.loc[i_b, i_a] = count
    for item in unique_items:
        matrix.loc[item, item] = item_counts.get(item, 0)

    return rules_df, matrix


def plot_basket_matrix_heatmap(matrix: pd.DataFrame) -> go.Figure:
    """Render category co-occurrence matrix heatmap."""
    fig = px.imshow(
        matrix,
        labels=dict(x="Línea de Producto", y="Línea de Producto", color="Frecuencia Combinada"),
        aspect="auto",
        color_continuous_scale="Purples",
        text_auto=True,
        title="Matriz de Co-ocurrencia y Afinidad entre Categorías",
    )
    fig.update_xaxes(side="top")
    return apply_theme(fig)
