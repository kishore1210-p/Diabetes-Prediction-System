"""Model and dataset analytics page."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from preprocess import TARGET_COLUMN, load_clean_dataset
from utils.ui import footer, metric_card


@st.cache_data(show_spinner=False)
def _analytics_data() -> pd.DataFrame:
    return load_clean_dataset()


def _plotly() -> tuple[Any, Any] | None:
    try:
        import plotly.express as px
        import plotly.graph_objects as go

        return px, go
    except ImportError:
        return None


def _chart_layout(figure: Any, height: int = 340) -> Any:
    figure.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=35, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#526b80", family="Arial"),
        legend_title_text="",
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="#e8eff4", zeroline=False)
    return figure


def render(metadata: dict[str, Any] | None) -> None:
    """Render interactive exploration of the clean dataset and trained models."""
    st.markdown('<p class="eyebrow">Model transparency</p>', unsafe_allow_html=True)
    st.title("Data and model performance, made visible.")
    st.markdown("Explore the distributions behind GlucoSense and see how the candidate models performed on the held-out test set.")

    library = _plotly()
    if library is None:
        st.error("Interactive analytics needs Plotly. Install project dependencies with `pip install -r requirements.txt`.")
        footer()
        return
    px, go = library
    data = _analytics_data()
    metrics = (metadata or {}).get("best_metrics", {})

    stats = st.columns(4)
    metric_values = [
        ("Clean records", f"{len(data):,}", "After duplicate removal"),
        ("Features", str(len(data.columns) - 1), "Model inputs"),
        ("Best ROC–AUC", f"{metrics.get('roc_auc', 0):.3f}" if metrics else "—", "Held-out test set"),
        ("Best model", (metadata or {}).get("best_model", "—"), "Selected by ROC–AUC"),
    ]
    for column, values in zip(stats, metric_values):
        with column:
            st.markdown(metric_card(*values), unsafe_allow_html=True)

    overview, distributions, relationships, models = st.tabs(["Overview", "Clinical distributions", "Relationships", "Model comparison"])

    with overview:
        left, right = st.columns(2, gap="large")
        labels = data[TARGET_COLUMN].map({0: "Non-diabetic", 1: "Diabetic"})
        counts = labels.value_counts().rename_axis("Outcome").reset_index(name="Patients")
        with left:
            figure = px.pie(counts, names="Outcome", values="Patients", hole=0.66, color="Outcome", color_discrete_map={"Non-diabetic": "#5ab797", "Diabetic": "#e26a6a"})
            figure.update_traces(textinfo="percent+label", textposition="outside")
            st.plotly_chart(_chart_layout(figure, 330), width="stretch")
        with right:
            smoking = data["smoking_history"].replace("No Info", "Not recorded").value_counts().rename_axis("Smoking history").reset_index(name="Patients")
            figure = px.bar(smoking, x="Smoking history", y="Patients", color="Smoking history", color_discrete_sequence=["#1677c9", "#39a38a", "#78b8df", "#efb95c", "#8b9fbd", "#bcc8d4"])
            figure.update_layout(showlegend=False)
            st.plotly_chart(_chart_layout(figure, 330), width="stretch")

    with distributions:
        labelled = data.copy()
        labelled["Outcome"] = labelled[TARGET_COLUMN].map({0: "Non-diabetic", 1: "Diabetic"})
        colors = {"Non-diabetic": "#5ab797", "Diabetic": "#e26a6a"}
        chart_specs = [
            ("age", "Age distribution", "Age (years)", 2),
            ("bmi", "BMI distribution", "BMI", 1),
            ("blood_glucose_level", "Blood glucose distribution", "Blood glucose (mg/dL)", 3),
            ("HbA1c_level", "HbA1c distribution", "HbA1c (%)", 1),
        ]
        columns = st.columns(2, gap="large")
        for index, (field, title, label, _precision) in enumerate(chart_specs):
            with columns[index % 2]:
                figure = px.histogram(labelled, x=field, color="Outcome", barmode="overlay", nbins=38, opacity=0.7, color_discrete_map=colors, labels={field: label})
                figure.update_layout(title=title)
                st.plotly_chart(_chart_layout(figure, 310), width="stretch")

    with relationships:
        numeric = data[["age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level", TARGET_COLUMN]]
        correlations = numeric.corr(numeric_only=True).round(2)
        labels = [name.replace("_", " ").title() for name in correlations.columns]
        heatmap = go.Figure(
            data=go.Heatmap(
                z=correlations.values,
                x=labels,
                y=labels,
                colorscale="RdBu_r",
                zmin=-1,
                zmax=1,
                colorbar=dict(title="Correlation"),
                hovertemplate="%{x} × %{y}: %{z:.2f}<extra></extra>",
            )
        )
        heatmap.update_layout(title="Correlation heatmap", height=520, margin=dict(l=8, r=8, t=45, b=8), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(heatmap, width="stretch")
        st.caption("Correlation indicates association in this dataset; it does not establish causation.")

    with models:
        comparison = pd.DataFrame((metadata or {}).get("model_comparison", []))
        if comparison.empty:
            st.info("Train the model to populate comparison metrics.")
        else:
            readable = comparison.copy()
            for column in ["accuracy", "precision", "recall", "f1_score", "roc_auc"]:
                readable[column] = readable[column].map(lambda value: f"{value:.3f}")
            readable = readable.rename(columns={"model": "Model", "accuracy": "Accuracy", "precision": "Precision", "recall": "Recall", "f1_score": "F1 score", "roc_auc": "ROC–AUC"})
            st.dataframe(readable[["Model", "Accuracy", "Precision", "Recall", "F1 score", "ROC–AUC"]], hide_index=True, width="stretch")
            score_long = comparison.melt(id_vars="model", value_vars=["accuracy", "precision", "recall", "f1_score", "roc_auc"], var_name="Metric", value_name="Score")
            score_long["Metric"] = score_long["Metric"].replace({"f1_score": "F1 score", "roc_auc": "ROC–AUC"}).str.title().replace({"Roc–Auc": "ROC–AUC"})
            figure = px.bar(score_long, x="model", y="Score", color="Metric", barmode="group", color_discrete_sequence=["#1677c9", "#38a88e", "#e7a23d", "#8c7bd2", "#dd6b71"])
            figure.update_layout(title="Held-out test performance", yaxis_range=[0, 1], xaxis_title="", yaxis_title="Score")
            st.plotly_chart(_chart_layout(figure, 390), width="stretch")

        importance = pd.DataFrame((metadata or {}).get("feature_importance", []))
        if not importance.empty:
            importance = importance.head(12).sort_values("importance")
            figure = px.bar(importance, x="importance", y="feature", orientation="h", color="importance", color_continuous_scale=["#bee9df", "#1677c9"])
            figure.update_layout(title="Feature importance from selected model", coloraxis_showscale=False, xaxis_title="Relative importance", yaxis_title="")
            st.plotly_chart(_chart_layout(figure, 410), width="stretch")

        skipped = (metadata or {}).get("skipped_models", [])
        if skipped:
            st.caption("Optional model status: " + "; ".join(f'{item["model"]} — {item["reason"]}' for item in skipped))

    footer()
