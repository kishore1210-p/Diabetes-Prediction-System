"""About page for GlucoSense."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.ui import feature_card, footer


def render(metadata: dict[str, Any] | None) -> None:
    """Explain the application, data processing, and model safeguards."""
    st.markdown('<p class="eyebrow">About GlucoSense</p>', unsafe_allow_html=True)
    st.title("Designed to support better health conversations.")
    st.markdown(
        "GlucoSense is a local machine-learning screening application that translates structured health information into an easy-to-understand estimate of diabetes risk."
    )

    first, second = st.columns(2, gap="large")
    with first:
        st.markdown("## The project")
        st.markdown(
            "The experience pairs a carefully structured patient form with a transparent model-comparison workflow. It is designed to help users recognise when a routine health conversation may be worthwhile - not to replace it."
        )
        st.markdown("## Dataset")
        st.markdown(
            "The supplied diabetes prediction dataset contains demographic, lifestyle, and clinical measurements including BMI, HbA1c, blood glucose, hypertension, heart-disease history, smoking history, and a binary diabetes label."
        )
    with second:
        st.markdown("## Data safeguards")
        st.markdown(
            "Before training, the application validates required columns, converts measurement fields safely, standardises text categories, removes duplicate records, and keeps data preparation inside each model pipeline to prevent leakage."
        )
        st.markdown("## Prediction safeguards")
        st.markdown(
            "The result includes probability and plain-language risk framing. General suggestions are intentionally conservative, and the interface repeatedly distinguishes screening from diagnosis."
        )

    st.markdown(
        '<div class="section-heading"><p class="eyebrow">Machine learning</p><h2>How the estimate is produced</h2></div>',
        unsafe_allow_html=True,
    )
    cards = [
        ("1", "Prepare", "Numeric values are imputed and standardised; categories are imputed and one-hot encoded."),
        ("2", "Compare", "Logistic Regression, Decision Tree, Random Forest, and XGBoost when available are evaluated on the same held-out set."),
        ("3", "Select", "The highest ROC-AUC candidate is saved with Joblib and reused for consistent future predictions."),
    ]
    columns = st.columns(3)
    for column, card in zip(columns, cards):
        with column:
            st.markdown(feature_card(*card), unsafe_allow_html=True)

    st.markdown("## Model record")
    if metadata:
        best_metrics = metadata.get("best_metrics", {})
        record = (
            f"**Selected model:** {metadata.get('best_model', '-')}<br>"
            f"**Training dataset:** {metadata.get('dataset_name', '-')}<br>"
            f"**Held-out accuracy:** {best_metrics.get('accuracy', 0):.1%}<br>"
            f"**Held-out ROC-AUC:** {best_metrics.get('roc_auc', 0):.3f}"
        )
        st.markdown(record, unsafe_allow_html=True)
    else:
        st.info("Training metadata will appear here after `python train_model.py` is run.")

    st.markdown("## Development")
    st.markdown(
        "Built as a Streamlit healthcare analytics application with scikit-learn, Joblib, Pandas, and Plotly. The app runs locally and does not transmit patient inputs to a remote service."
    )
    footer()
