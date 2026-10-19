"""Customer RFM Segmentation and Behavioral Analytics module."""
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from src.core.config import COLORS, PALETTE
from src.core.theme import apply_theme


def calculate_rfm_segments(df: pd.DataFrame, n_clusters: int = 4) -> Tuple[pd.DataFrame, Dict[str, Any], go.Figure]:
    """Perform RFM segmentation and K-Means clustering on retail customer transactions."""
    ref_date = df["Date"].max() + pd.Timedelta(days=1)

    # In POS retail datasets where unique customer ID isn't tracked directly,
    # we aggregate by Customer Cohort Profile: (Customer type, Gender, City, Payment)
    # plus transaction profile
    rfm = (
        df.groupby(["Invoice ID"])
        .agg(
            Recency=("Date", lambda x: (ref_date - x.max()).days),
            Monetary=("Sales", "sum"),
            Quantity=("Quantity", "sum"),
            AvgRating=("Rating", "mean"),
            CustomerType=("Customer type", "first"),
            Branch=("Branch", "first"),
            Payment=("Payment", "first"),
        )
        .reset_index()
    )

    # Feature scaling for clustering
    scaler = StandardScaler()
    features = ["Recency", "Monetary", "Quantity", "AvgRating"]
    X_scaled = scaler.fit_transform(rfm[features])

    # K-Means clustering
    k = max(2, min(n_clusters, len(rfm) - 1))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(X_scaled)

    sil_score = float(silhouette_score(X_scaled, rfm["Cluster"])) if len(rfm) > k else 0.0

    # Assign meaningful business segment names based on cluster centroids
    cluster_means = rfm.groupby("Cluster")[["Monetary", "Recency", "Quantity"]].mean()
    cluster_order = cluster_means.sort_values(by="Monetary", ascending=False).index.tolist()

    segment_names = {}
    default_labels = [
        "💎 Clientes VIP / Alto Valor",
        "⭐ Compradores Frecuentes",
        "🌱 Clientes Ocasionales / En Crecimiento",
        "⚠️ Clientes en Riesgo / Bajo Gasto",
        "💤 Inactivos / Transacciones Mínimas",
        "🎯 Nuevos Prospectos",
    ]
    for i, c_id in enumerate(cluster_order):
        segment_names[c_id] = default_labels[i % len(default_labels)]

    rfm["Segmento"] = rfm["Cluster"].map(segment_names)

    # 3D Scatter plot
    fig = px.scatter_3d(
        rfm,
        x="Recency",
        y="Monetary",
        z="AvgRating",
        color="Segmento",
        title=f"Segmentación Conductual de Clientes (Silhouette: {sil_score:.3f})",
        labels={"Recency": "Recencia (Días)", "Monetary": "Gasto Total ($)", "AvgRating": "Calificación"},
        color_discrete_sequence=PALETTE,
        hover_data=["Invoice ID", "CustomerType", "Payment"],
    )
    apply_theme(fig)

    metrics = {
        "silhouette_score": sil_score,
        "n_clusters": k,
        "total_profiles": len(rfm),
        "cluster_summary": rfm.groupby("Segmento").agg(
            Perfiles=("Invoice ID", "count"),
            Ticket_Promedio=("Monetary", "mean"),
            Recencia_Promedio=("Recency", "mean"),
            Calificacion_Promedio=("AvgRating", "mean"),
        ).round(2).reset_index(),
    }

    return rfm, metrics, fig
