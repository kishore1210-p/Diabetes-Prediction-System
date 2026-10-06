"""Patient input and result presentation page."""

from __future__ import annotations

from typing import Any

import streamlit as st

from preprocess import patient_frame
from utils.clinical import personalised_recommendations, risk_band
from utils.ui import footer, metric_card, recommendation_cards


def _render_result(result: dict[str, Any]) -> None:
    probability = float(result["probability"])
    patient = result["patient"]
    prediction = bool(result["prediction"])
    level, colour, css_class = risk_band(probability)
    display_label = "Diabetic" if prediction else "Non-diabetic"
    label_background = "#ffeef0" if prediction else "#eaf9f4"
    label_colour = "#c64153" if prediction else "#128462"

    st.markdown('<div class="section-heading"><p class="eyebrow">Your screening result</p><h2>Risk estimate overview</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="result-shell">', unsafe_allow_html=True)
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(
            f'<span class="status-pill" style="background:{label_background}; color:{label_colour};">{display_label}</span>'
            f'<h2 style="margin-top:.7rem !important;">{level} risk estimate</h2>'
            '<p>This model-based score is a screening aid. It does not confirm or rule out a medical condition.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="progress-track"><div class="progress-fill {css_class}" style="width:{probability * 100:.1f}%; background:{colour};"></div></div>'
            f'<div class="risk-key"><span>Low</span><strong style="color:{colour};">{level} · {probability:.1%}</strong><span>High</span></div>',
            unsafe_allow_html=True,
        )
    with right:
        metric_columns = st.columns(2)
        with metric_columns[0]:
            st.markdown(metric_card("Model confidence", f"{probability:.1%}", "Estimated probability"), unsafe_allow_html=True)
        with metric_columns[1]:
            st.markdown(metric_card("Risk band", level, "Low · Moderate · High"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if probability >= 0.50:
        st.markdown(
            '<div class="notice"><strong>Important:</strong> A higher screening estimate is a reason to speak with a qualified healthcare professional; it is not a diagnosis. Seek urgent care if you have severe or rapidly worsening symptoms.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-heading"><p class="eyebrow">Supportive next steps</p><h2>Personalised wellbeing suggestions</h2></div>', unsafe_allow_html=True)
    recommendation_cards(personalised_recommendations(patient, probability))

    with st.expander("Review entered health information"):
        review = {
            "Gender": str(patient["gender"]),
            "Age": f'{patient["age"]} years',
            "Hypertension": "Yes" if patient["hypertension"] else "No",
            "Heart disease": "Yes" if patient["heart_disease"] else "No",
            "Smoking history": str(patient["smoking_history"]),
            "BMI": f'{patient["bmi"]:.1f}',
            "HbA1c": f'{patient["HbA1c_level"]}%',
            "Blood glucose": f'{patient["blood_glucose_level"]} mg/dL',
        }
        st.table({"Health measure": list(review.keys()), "Entered value": list(review.values())})


def render(bundle: dict[str, Any] | None) -> None:
    """Render the assessment form and its most recent result."""
    st.markdown('<p class="eyebrow">Personal risk assessment</p>', unsafe_allow_html=True)
    st.title("Take a closer look at your health profile.")
    st.markdown("Use recent measurements where possible. Your entries stay within this local Streamlit session and are used only to generate this estimate.")

    if bundle is None:
        st.error("The trained model is not available yet. Run `python train_model.py` from the project folder, then refresh this page.")
        footer()
        return

    st.markdown('<div class="form-shell">', unsafe_allow_html=True)
    with st.form("prediction_form", clear_on_submit=False):
        st.markdown("### Patient information")
        st.caption("All fields are required. Clinical measurements should come from a qualified test or your health record.")
        first, second = st.columns(2, gap="large")
        with first:
            gender = st.selectbox("Gender", ["Female", "Male", "Other"], help="Select the category that best matches the patient record.")
            age = st.number_input("Age", min_value=0.0, max_value=120.0, value=35.0, step=1.0, format="%.0f")
            hypertension = st.selectbox("Hypertension", ["No", "Yes"], help="A prior diagnosis of high blood pressure.")
            heart_disease = st.selectbox("Heart disease", ["No", "Yes"], help="A history of heart disease or cardiovascular condition.")
        with second:
            smoking_history = st.selectbox("Smoking history", ["never", "former", "current", "not current", "ever", "No Info"])
            bmi = st.number_input("BMI", min_value=10.0, max_value=80.0, value=25.0, step=0.1, format="%.1f")
            hba1c = st.number_input("HbA1c level (%)", min_value=3.0, max_value=20.0, value=5.7, step=0.1, format="%.1f")
            glucose = st.number_input("Blood glucose level (mg/dL)", min_value=40, max_value=600, value=100, step=1)
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Generate risk estimate  →", type="primary", width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        patient = {
            "gender": gender,
            "age": float(age),
            "hypertension": int(hypertension == "Yes"),
            "heart_disease": int(heart_disease == "Yes"),
            "smoking_history": smoking_history,
            "bmi": float(bmi),
            "HbA1c_level": float(hba1c),
            "blood_glucose_level": int(glucose),
        }
        with st.spinner("Analysing your health profile securely…"):
            frame = patient_frame(patient)
            pipeline = bundle["pipeline"]
            probability = float(pipeline.predict_proba(frame)[0, 1])
            prediction = int(pipeline.predict(frame)[0])
            st.session_state["latest_prediction"] = {
                "patient": patient,
                "probability": probability,
                "prediction": prediction,
            }

    latest = st.session_state.get("latest_prediction")
    if latest:
        _render_result(latest)

    footer()
