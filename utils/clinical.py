"""Patient-facing risk interpretation and non-diagnostic health guidance."""

from __future__ import annotations

from typing import Any


def risk_band(probability: float) -> tuple[str, str, str]:
    """Map model probability to a plain-language risk band and display colour."""
    if probability < 0.20:
        return "Low", "#159b75", "low"
    if probability < 0.50:
        return "Moderate", "#ef9d32", "moderate"
    return "High", "#e05252", "high"


def personalised_recommendations(patient: dict[str, Any], probability: float) -> list[dict[str, str]]:
    """Return conservative, general wellbeing suggestions tailored to entered values."""
    recommendations: list[dict[str, str]] = []
    bmi = float(patient["bmi"])
    glucose = float(patient["blood_glucose_level"])
    hba1c = float(patient["HbA1c_level"])
    smoker = str(patient["smoking_history"]).lower()

    if probability >= 0.50:
        recommendations.append(
            {
                "icon": "✦",
                "title": "Arrange a clinical review",
                "text": "Discuss this screening result with a qualified clinician, especially if you have symptoms or prior concerns.",
            }
        )
    elif probability >= 0.20:
        recommendations.append(
            {
                "icon": "◌",
                "title": "Monitor with your care team",
                "text": "Consider sharing your readings and health history at your next routine health appointment.",
            }
        )

    if glucose >= 140 or hba1c >= 5.7:
        recommendations.append(
            {
                "icon": "⌁",
                "title": "Choose steady-energy meals",
                "text": "Prioritise fibre-rich vegetables, whole grains, protein, and less-added-sugar drinks and snacks.",
            }
        )

    if bmi >= 25:
        recommendations.append(
            {
                "icon": "◒",
                "title": "Support a sustainable weight range",
                "text": "Small, lasting nutrition and activity changes can support cardiometabolic health. A clinician can personalise goals.",
            }
        )

    if smoker in {"current", "ever", "not current"}:
        recommendations.append(
            {
                "icon": "◈",
                "title": "Ask about tobacco support",
                "text": "If tobacco is part of your routine, a healthcare professional can help you find an evidence-based cessation plan.",
            }
        )

    recommendations.extend(
        [
            {
                "icon": "↗",
                "title": "Move regularly",
                "text": "Aim for activity that suits your ability and routine; even short walks can be a useful starting point.",
            },
            {
                "icon": "☾",
                "title": "Protect sleep and hydration",
                "text": "Keep a regular sleep routine and drink water throughout the day unless your clinician advises otherwise.",
            },
        ]
    )

    return recommendations[:5]
