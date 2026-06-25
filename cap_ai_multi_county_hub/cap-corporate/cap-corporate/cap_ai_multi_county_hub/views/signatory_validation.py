"""Signatory Validation."""
import plotly.express as px
import streamlit as st
from components.ui import gauge_html, page_header, track_page_view
from utils.analytics import validate_signatories
from utils.data_helpers import load_uploaded_file, sample_signatory_data
from utils.theme import COLORS

def render():
    track_page_view("Signatory Validation")
    page_header("Authorised Signatory Verification", "Detect unauthorized approvals and mandate breaches")
    c1, c2 = st.columns(2)
    with c1: master_file = st.file_uploader("Signatory Master", type=["xlsx", "csv"], key="sig_master")
    with c2: log_file = st.file_uploader("Payment Approval Log", type=["xlsx", "csv"], key="sig_log")
    if st.button("Load Demo Data", key="sig_demo"):
        master, approvals = sample_signatory_data()
    elif master_file and log_file:
        master = load_uploaded_file(master_file)
        approvals = load_uploaded_file(log_file)
    else:
        st.info("Upload files or load demo data.")
        return
    if master is None or approvals is None:
        return
    issues = validate_signatories(master, approvals)
    st.session_state.signatory_issues = issues
    compliance = max(0, 100 - len(issues) * 15)
    st.markdown(gauge_html("Compliance Gauge", compliance, COLORS["teal"]), unsafe_allow_html=True)
    if not issues.empty:
        fig = px.imshow([[compliance, len(issues)]], x=["Compliance", "Issues"], y=["Score"], color_continuous_scale=[COLORS["deep_navy"], COLORS["danger"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=200, title="Approval Risk Matrix")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(issues, use_container_width=True, hide_index=True)
    else:
        st.success("All approvals validated successfully.")
    st.markdown('<div class="section-title">Approval Hierarchy</div>', unsafe_allow_html=True)
    st.dataframe(master, use_container_width=True, hide_index=True)
