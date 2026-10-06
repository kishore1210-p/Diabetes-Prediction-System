"""GlucoSense — a polished local diabetes risk screening application."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import streamlit as st

from pages import about, analytics, home, prediction
from utils.ui import inject_styles, sidebar_brand


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "model" / "diabetes_model.joblib"
NAVIGATION_PAGES = ["Home", "Prediction", "Analytics", "About"]
NAVIGATION_KEY = "primary_navigation"


@st.cache_resource(show_spinner=False)
def load_model_bundle() -> dict[str, Any] | None:
    """Load the complete fitted pipeline and its presentation metadata."""
    if not MODEL_PATH.exists():
        return None
    bundle = joblib.load(MODEL_PATH)
    if not isinstance(bundle, dict) or "pipeline" not in bundle or "metadata" not in bundle:
        raise ValueError("The saved model artifact has an invalid format. Retrain with python train_model.py.")
    return bundle


def _sidebar_navigation() -> str:
    """Render navigation with a stable widget key across every page rerun."""
    requested_page = st.session_state.pop("requested_page", None)
    if requested_page in NAVIGATION_PAGES:
        # This assignment occurs before the radio is created, which is the safe
        # Streamlit pattern for programmatic navigation from a page button.
        st.session_state[NAVIGATION_KEY] = requested_page
    elif NAVIGATION_KEY not in st.session_state:
        st.session_state[NAVIGATION_KEY] = "Home"

    sidebar_brand()
    st.sidebar.markdown("<p style='font-size:.72rem;opacity:.70;text-transform:uppercase;letter-spacing:.1em;font-weight:800;margin-bottom:.25rem;'>Navigate</p>", unsafe_allow_html=True)
    selected = st.sidebar.radio(
        "Navigate",
        NAVIGATION_PAGES,
        key=NAVIGATION_KEY,
        label_visibility="collapsed",
    )
    st.sidebar.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='border:1px solid rgba(255,255,255,.17);border-radius:14px;padding:.8rem .85rem;background:rgba(255,255,255,.08);font-size:.77rem;line-height:1.55;opacity:.95;'><strong>Screening, not diagnosis</strong><br>Use this estimate to support—not replace—professional medical guidance.</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='position:fixed;bottom:1.3rem;font-size:.7rem;opacity:.72;'>Private local experience<br>GlucoSense Health Tools</div>", unsafe_allow_html=True)
    return selected


def main() -> None:
    st.set_page_config(
        page_title="GlucoSense | Diabetes Risk Screening",
        page_icon="✚",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={"About": "GlucoSense is an educational diabetes risk screening tool."},
    )
    inject_styles()
    selected_page = _sidebar_navigation()

    try:
        bundle = load_model_bundle()
    except Exception as exc:  # Present a clear recovery path rather than failing the entire app.
        st.error(f"The saved model could not be loaded: {exc}")
        bundle = None

    metadata = bundle.get("metadata") if bundle else None
    if selected_page == "Home":
        home.render(metadata)
    elif selected_page == "Prediction":
        prediction.render(bundle)
    elif selected_page == "Analytics":
        analytics.render(metadata)
    else:
        about.render(metadata)


if __name__ == "__main__":
    main()
