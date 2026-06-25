"""Training & AI Adoption Hub."""
import streamlit as st
from components.charts import ai_maturity_curve
from components.ui import gauge_html, kpi_card, page_header, track_page_view
from utils.analytics import county_benchmark_data
from utils.theme import COLORS

def render():
    track_page_view("Training & AI Adoption")
    page_header("Training & AI Adoption Hub", "Track courses, certifications, and AI maturity")
    for col, card in zip(st.columns(4), [
        ("Staff Trained", "342", "+28 this month", "👥"),
        ("Certifications", "89", "+12 earned", "🏅"),
        ("AI Readiness", "78.4%", "+6.2 pts", "🤖"),
        ("Adoption Rate", "64%", "+8%", "📊"),
    ]):
        with col: st.markdown(kpi_card(*card, color=COLORS["purple"]), unsafe_allow_html=True)
    st.plotly_chart(ai_maturity_curve(), use_container_width=True)
    st.markdown(gauge_html("Learning Dashboard Completion", 82.5, COLORS["azure"]), unsafe_allow_html=True)
    st.dataframe({
        "Course": ["Treasury Fundamentals", "AI for Auditors", "Shared Services 101", "Fraud Analytics", "Compliance Mastery"],
        "Enrolled": [45, 32, 58, 28, 41],
        "Completed": [38, 24, 52, 19, 35],
        "Status": ["Active", "Active", "Active", "Active", "Active"],
    }, use_container_width=True, hide_index=True)
    st.markdown('<div class="section-title">County Benchmarking</div>', unsafe_allow_html=True)
    st.dataframe(county_benchmark_data()[["County", "AI Readiness", "Compliance Score"]], use_container_width=True, hide_index=True)
