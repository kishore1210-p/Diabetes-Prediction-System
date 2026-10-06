"""Shared UI components and custom CSS for a polished Streamlit experience."""

from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def inject_styles() -> None:
    """Apply the application visual system once per run."""
    st.markdown(
        """
        <style>
        :root {
            --ink: #12304a;
            --muted: #6c8092;
            --blue: #1677c9;
            --blue-dark: #0e5e9f;
            --teal: #159b75;
            --mint: #edf9f5;
            --line: #deebf3;
            --paper: #ffffff;
            --canvas: #f5f9fc;
            --amber: #ef9d32;
            --red: #df5656;
        }
        .stApp { background: var(--canvas); color: var(--ink); }
        [data-testid="stHeader"] { background: rgba(245,249,252,.78); backdrop-filter: blur(12px); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0e5e9f 0%, #0d6ba7 55%, #0e867f 100%); }
        [data-testid="stSidebar"] * { color: #f8fcff; }
        [data-testid="stSidebar"] .stRadio label { padding: .42rem .3rem; border-radius: 10px; transition: background .2s ease; }
        [data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,.13); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: inherit; }
        .block-container { max-width: 1220px; padding-top: 2.1rem; padding-bottom: 3.4rem; }
        h1, h2, h3 { color: var(--ink); letter-spacing: -.035em; }
        h1 { font-size: clamp(2.05rem, 4vw, 3.6rem) !important; line-height: 1.06 !important; margin-bottom: .9rem !important; }
        h2 { font-size: 1.6rem !important; margin-top: 1.6rem !important; }
        h3 { font-size: 1.02rem !important; letter-spacing: -.015em; }
        p, li { color: var(--muted); }
        .brand { display: flex; gap: 10px; align-items: center; padding: .25rem 0 1.35rem; }
        .brand-mark { width: 35px; height: 35px; border-radius: 11px; display: grid; place-items: center; background: rgba(255,255,255,.17); border: 1px solid rgba(255,255,255,.28); font-size: 1.15rem; }
        .brand-name { font-weight: 800; font-size: 1.05rem; letter-spacing: -.02em; color: white; }
        .brand-subtitle { font-size: .72rem; opacity: .76; color: white; margin-top: 1px; }
        .eyebrow { color: var(--blue); font-size: .76rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 800; margin: 0 0 .7rem; }
        .hero-copy { padding: .75rem 0 1rem; }
        .hero-copy p { font-size: 1.08rem; max-width: 540px; line-height: 1.65; }
        .hero-visual { position: relative; min-height: 365px; border-radius: 28px; overflow: hidden; background: radial-gradient(circle at 20% 20%, #c7f2ea 0, transparent 31%), radial-gradient(circle at 90% 15%, #c9e9fb 0, transparent 37%), linear-gradient(135deg, #effaff, #e8f8f3); border: 1px solid #d9eaf1; }
        .hero-orbit { position: absolute; border: 1px solid rgba(22,119,201,.18); border-radius: 999px; }
        .orbit-one { width: 330px; height: 330px; right: -70px; top: 24px; }
        .orbit-two { width: 250px; height: 250px; left: -100px; bottom: -105px; }
        .hero-panel { position: absolute; background: rgba(255,255,255,.87); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,.92); box-shadow: 0 18px 42px rgba(16,90,141,.12); border-radius: 20px; }
        .heart-panel { width: 155px; height: 155px; display: grid; place-items: center; top: 68px; left: calc(50% - 77px); color: #de5c66; font-size: 4.4rem; animation: float 4s ease-in-out infinite; }
        .pulse-panel { right: 26px; top: 35px; padding: 13px 15px; font-size: .82rem; color: var(--ink); }
        .pulse-line { color: var(--teal); font-size: 1.18rem; letter-spacing: -3px; }
        .shield-panel { left: 28px; bottom: 33px; padding: 15px 17px; color: var(--ink); font-size: .83rem; }
        .shield-panel span { color: var(--teal); font-weight: 800; font-size: 1.2rem; margin-right: 7px; }
        @keyframes float { 50% { transform: translateY(-9px); } }
        .feature-card, .info-card, .result-card, .recommendation-card { background: rgba(255,255,255,.88); border: 1px solid var(--line); box-shadow: 0 9px 25px rgba(25,66,96,.055); border-radius: 18px; }
        .feature-card { padding: 1.28rem; min-height: 168px; transition: transform .2s ease, box-shadow .2s ease; }
        .feature-card:hover { transform: translateY(-4px); box-shadow: 0 16px 32px rgba(25,66,96,.1); }
        .feature-icon { width: 37px; height: 37px; display: grid; place-items: center; border-radius: 12px; color: var(--blue); background: #eaf5ff; margin-bottom: 1rem; font-weight: 900; }
        .feature-card p { font-size: .9rem; margin: 0; line-height: 1.55; }
        .metric-card { background: white; border: 1px solid var(--line); border-radius: 16px; padding: 1.05rem 1.2rem; min-height: 107px; box-shadow: 0 7px 20px rgba(25,66,96,.04); }
        .metric-label { color: var(--muted); font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
        .metric-value { color: var(--ink); font-size: 1.75rem; font-weight: 800; letter-spacing: -.05em; margin-top: .35rem; }
        .metric-hint { color: var(--teal); font-size: .79rem; margin-top: .15rem; }
        .section-heading { margin: 2.3rem 0 1rem; }
        .form-shell { background: rgba(255,255,255,.92); border: 1px solid var(--line); box-shadow: 0 12px 36px rgba(25,66,96,.07); border-radius: 22px; padding: 1.35rem 1.4rem .7rem; }
        .result-shell { background: linear-gradient(135deg, #fff 20%, #f0fbf8); border: 1px solid #d7ece7; border-radius: 24px; padding: 1.55rem; box-shadow: 0 16px 42px rgba(16,101,91,.08); }
        .status-pill { display: inline-block; padding: .32rem .72rem; border-radius: 999px; font-size: .78rem; font-weight: 800; }
        .progress-track { height: 11px; border-radius: 999px; background: #e6eef4; overflow: hidden; margin: .85rem 0 .42rem; }
        .progress-fill { height: 100%; border-radius: inherit; }
        .risk-key { display:flex; justify-content:space-between; font-size:.76rem; color:var(--muted); }
        .recommendation-card { padding: 1rem; min-height: 122px; }
        .recommendation-icon { color: var(--teal); font-size: 1.12rem; font-weight: 800; margin-right: .43rem; }
        .recommendation-card h3 { display:inline; }
        .recommendation-card p { font-size: .86rem; margin: .55rem 0 0; line-height: 1.5; }
        .notice { background: #fff9ed; border: 1px solid #f5dfad; border-radius: 13px; padding: .8rem 1rem; font-size: .88rem; color: #806124; }
        .footer-note { border-top: 1px solid var(--line); margin-top: 3rem; padding-top: 1.15rem; font-size: .78rem; color: var(--muted); }
        .about-card { padding: 1.3rem; height: 100%; }
        .stButton > button, .stFormSubmitButton > button { border: none !important; background: linear-gradient(135deg, #1677c9, #0e679f) !important; color: white !important; padding: .68rem 1.05rem !important; border-radius: 10px !important; font-weight: 750 !important; box-shadow: 0 7px 17px rgba(22,119,201,.2) !important; transition: transform .15s ease, box-shadow .15s ease !important; }
        .stButton > button:hover, .stFormSubmitButton > button:hover { transform: translateY(-2px); box-shadow: 0 11px 24px rgba(22,119,201,.27) !important; }
        [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div { border-radius: 10px !important; border-color: #d9e6ee !important; }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { border-radius: 9px; padding: .4rem .8rem; }
        @media (max-width: 720px) { .hero-visual { min-height: 285px; margin-top: .5rem; } .block-container { padding: 1.35rem 1rem 2.5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="brand">
          <div class="brand-mark">✚</div>
          <div><div class="brand-name">GlucoSense</div><div class="brand-subtitle">Diabetes risk screening</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero_illustration() -> None:
    st.markdown(
        """
        <div class="hero-visual" aria-label="Healthcare illustration">
          <div class="hero-orbit orbit-one"></div><div class="hero-orbit orbit-two"></div>
          <div class="hero-panel pulse-panel"><strong>Live health view</strong><br><span class="pulse-line">⌁⌁⌁⌁⌁⌁⌁</span></div>
          <div class="hero-panel heart-panel">♥</div>
          <div class="hero-panel shield-panel"><span>✚</span><strong>Informed, not alarming</strong><br>Private risk screening</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, hint: str = "") -> str:
    safe_label, safe_value, safe_hint = map(html.escape, (label, value, hint))
    hint_html = f'<div class="metric-hint">{safe_hint}</div>' if hint else ""
    return f'<div class="metric-card"><div class="metric-label">{safe_label}</div><div class="metric-value">{safe_value}</div>{hint_html}</div>'


def feature_card(icon: str, title: str, text: str) -> str:
    return (
        '<div class="feature-card">'
        f'<div class="feature-icon">{html.escape(icon)}</div><h3>{html.escape(title)}</h3>'
        f'<p>{html.escape(text)}</p></div>'
    )


def footer() -> None:
    st.markdown(
        """
        <div class="footer-note">
          GlucoSense provides an educational screening estimate, not a diagnosis or emergency service. For urgent symptoms or medical concerns, contact a qualified healthcare professional or local emergency service.
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_cards(items: Iterable[dict[str, str]]) -> None:
    columns = st.columns(2)
    for index, item in enumerate(items):
        with columns[index % 2]:
            st.markdown(
                '<div class="recommendation-card">'
                f'<span class="recommendation-icon">{html.escape(item["icon"])}</span>'
                f'<h3>{html.escape(item["title"])}</h3>'
                f'<p>{html.escape(item["text"])}</p></div>',
                unsafe_allow_html=True,
            )
