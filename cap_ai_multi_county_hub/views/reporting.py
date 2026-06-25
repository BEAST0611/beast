"""Reporting Suite."""
from datetime import datetime
import pandas as pd
import streamlit as st
from components.ui import page_header, render_logo, track_page_view
from utils.analytics import county_benchmark_data, dashboard_kpis
from utils.data_helpers import sample_transactions
from utils.reports import generate_audit_workbook, generate_executive_pdf

def render():
    track_page_view("Reports")
    page_header("Reporting Suite", "Executive PDF reports and Excel audit workbooks")
    render_logo(100)
    kpis = dashboard_kpis()
    findings = [
        "23 high-risk transactions identified across 4 counties",
        "Bank charge verification flagged $340 in overcharges",
        "Idle cash opportunity cost estimated at $189K annually",
        "Signatory validation detected 3 authority breaches",
    ]
    recommendations = [
        "Deploy automated sweep rules for Franklin and Clayton counties",
        "Renegotiate wire fee schedule with primary banking partner",
        "Expand shared services marketplace to 3 additional asset categories",
        "Complete AI governance training for all treasury officers by Q3",
    ]
    if st.button("Generate Executive PDF"):
        pdf = generate_executive_pdf(
            "Executive Governance Report",
            "Comprehensive analysis of multi-county shared services, treasury oversight, and compliance posture.",
            findings, recommendations, kpis,
        )
        st.download_button("Download PDF", pdf, f"CAP_AI_Report_{datetime.now():%Y%m%d}.pdf", "application/pdf")
    if st.button("Generate Excel Audit Workbook"):
        data = {
            "Dashboard": county_benchmark_data(),
            "Exceptions": sample_transactions().head(20),
            "Round-Tripping": st.session_state.get("round_trip_alerts", sample_transactions().head(5)),
            "Treasury": county_benchmark_data()[["County", "Treasury Score", "Savings ($M)"]],
            "Compliance": county_benchmark_data()[["County", "Compliance Score"]],
            "Recommendations": pd.DataFrame({"Recommendation": recommendations}),
        }
        xlsx = generate_audit_workbook(data)
        st.download_button("Download Workbook", xlsx, f"CAP_AI_Audit_{datetime.now():%Y%m%d}.xlsx")
