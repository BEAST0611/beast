"""Reusable UI components for CAP AI."""

from __future__ import annotations

import streamlit as st

from utils.auth import log_activity
from utils.theme import COLORS, LOGO_PATH


def render_logo(width: int = 120, centered: bool = False) -> None:
    if LOGO_PATH.exists():
        if centered:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(str(LOGO_PATH), width=width)
        else:
            st.image(str(LOGO_PATH), width=width)
    else:
        st.markdown(
            f"<div style='font-size:2rem;font-weight:800;color:{COLORS['azure']}'>CAP AI</div>",
            unsafe_allow_html=True,
        )


def page_header(title: str, subtitle: str = "") -> None:
    col1, col2 = st.columns([1, 5])
    with col1:
        render_logo(80)
    with col2:
        st.markdown(
            f"""
            <div class="page-header">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def kpi_card(label: str, value: str, delta: str = "", icon: str = "📊", color: str | None = None) -> str:
    accent = color or COLORS["azure"]
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="glass-card kpi-card floating-card" style="border-left: 4px solid {accent};">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def render_kpi_row(kpis: list[tuple[str, str, str, str]]) -> None:
    cols = st.columns(len(kpis))
    for col, (label, value, delta, icon) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(label, value, delta, icon), unsafe_allow_html=True)


def gauge_html(label: str, score: float, color: str) -> str:
    pct = min(100, max(0, score))
    return f"""
    <div class="glass-card gauge-card">
        <div class="gauge-label">{label}</div>
        <div class="gauge-bar"><div class="gauge-fill" style="width:{pct}%;background:{color};"></div></div>
        <div class="gauge-score">{pct:.1f}%</div>
    </div>
    """


def risk_thermometer(score: float) -> str:
    if score >= 75:
        level, color = "Critical", COLORS["danger"]
    elif score >= 50:
        level, color = "Elevated", COLORS["warning"]
    elif score >= 25:
        level, color = "Moderate", COLORS["azure"]
    else:
        level, color = "Low", COLORS["success"]
    return f"""
    <div class="glass-card thermometer">
        <div class="gauge-label">Risk Level: {level}</div>
        <div class="thermo-track">
            <div class="thermo-fill" style="height:{score}%;background:{color};"></div>
        </div>
        <div class="gauge-score">{score:.0f}</div>
    </div>
    """


def particle_background() -> None:
    st.markdown(
        """
        <div id="particles-bg">
            <div class="particle"></div><div class="particle"></div><div class="particle"></div>
            <div class="particle"></div><div class="particle"></div><div class="particle"></div>
            <div class="particle"></div><div class="particle"></div><div class="particle"></div>
            <div class="particle"></div><div class="particle"></div><div class="particle"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def glass_section(title: str, content_fn) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    content_fn()


def track_page_view(page_name: str) -> None:
    log_activity("PAGE_VIEW", page_name)
