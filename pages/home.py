"""Home page for the GlucoSense application."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.ui import feature_card, footer, hero_illustration, metric_card


def render(metadata: dict[str, Any] | None) -> None:
    """Render the patient-facing landing page."""
    metrics = (metadata or {}).get("best_metrics", {})
    summary = (metadata or {}).get("training_summary", {})
    accuracy = metrics.get("accuracy")
    roc_auc = metrics.get("roc_auc")
    model_name = (metadata or {}).get("best_model", "Validated model")

    left, right = st.columns([1.08, 0.92], gap="large")
    with left:
        st.markdown('<div class="hero-copy">', unsafe_allow_html=True)
        st.markdown('<p class="eyebrow">Personal health, made clearer</p>', unsafe_allow_html=True)
        st.title("Understand your diabetes risk with a clearer next step.")
        st.markdown(
            "GlucoSense turns a few routine health details into a private, easy-to-read screening estimate—then helps you make sense of what to do next."
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start a risk assessment  →", type="primary", width="content"):
            st.session_state["requested_page"] = "Prediction"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        hero_illustration()

    st.markdown('<div class="section-heading"><p class="eyebrow">Designed for understanding</p><h2>Simple input. Thoughtful insight.</h2></div>', unsafe_allow_html=True)
    cards = [
        ("⌁", "Personalised screening", "Enter common clinical measurements and receive a model-based diabetes risk estimate in seconds."),
        ("◌", "Clear risk language", "Probability, risk band, and colour cues keep the result understandable without unnecessary alarm."),
        ("✦", "Practical next steps", "General wellbeing suggestions help you prepare for an informed conversation with your care team."),
    ]
    columns = st.columns(3)
    for column, card in zip(columns, cards):
        with column:
            st.markdown(feature_card(*card), unsafe_allow_html=True)

    st.markdown('<div class="section-heading"><p class="eyebrow">At a glance</p><h2>Built on real-world health data</h2></div>', unsafe_allow_html=True)
    data_rows = summary.get("clean_rows", 0)
    positive_count = summary.get("target_distribution", {}).get("diabetic", 0)
    positive_rate = (positive_count / data_rows * 100) if data_rows else 0
    stat_columns = st.columns(4)
    stats = [
        ("Model accuracy", f"{accuracy:.1%}" if accuracy is not None else "—", "Held-out test set"),
        ("ROC–AUC", f"{roc_auc:.3f}" if roc_auc is not None else "—", "Discrimination quality"),
        ("Patient records", f"{data_rows:,}" if data_rows else "100,000", "Cleaned dataset"),
        ("Positive class", f"{positive_rate:.1f}%" if data_rows else "—", "Diabetes-labelled records"),
    ]
    for column, stat in zip(stat_columns, stats):
        with column:
            st.markdown(metric_card(*stat), unsafe_allow_html=True)

    st.markdown('<div class="section-heading"><p class="eyebrow">Model intelligence</p><h2>Reliable by design, transparent by default</h2></div>', unsafe_allow_html=True)
    info_left, info_right = st.columns(2, gap="large")
    with info_left:
        st.markdown(
            f'''<div class="info-card about-card"><div class="feature-icon">◒</div><h3>Model validation</h3>
            <p>GlucoSense compares Logistic Regression, Decision Tree, and Random Forest models on a held-out test set, selecting the strongest available model by ROC–AUC.</p>
            <p><strong>Selected model:</strong> {model_name}</p></div>''',
            unsafe_allow_html=True,
        )
    with info_right:
        st.markdown(
            '''<div class="info-card about-card"><div class="feature-icon">✚</div><h3>Dataset coverage</h3>
            <p>The prediction model considers demographics, smoking history, BMI, HbA1c, blood glucose, hypertension, and heart-disease history.</p>
            <p>Inputs are cleaned, imputed, encoded, and scaled inside the saved prediction pipeline to keep scoring consistent.</p></div>''',
            unsafe_allow_html=True,
        )

    footer()
