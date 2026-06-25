"""Idle Cash Monitoring."""
import streamlit as st
from components.charts import county_ranking, idle_cash_trend
from components.ui import gauge_html, kpi_card, page_header, track_page_view
from utils.analytics import analyze_idle_cash
from utils.data_helpers import load_uploaded_file, sample_cash_balances
from utils.theme import COLORS

def render():
    track_page_view("Idle Cash Monitoring")
    page_header("Idle Cash & Sweep Monitoring", "Identify public funds that should have been invested")
    rate = st.sidebar.slider("Investment Rate (%)", 1.0, 8.0, 4.5) / 100
    uploaded = st.file_uploader("Upload Cash Balances", type=["xlsx", "csv"])
    if uploaded:
        df = load_uploaded_file(uploaded)
    elif st.button("Load Demo Data"):
        df = sample_cash_balances()
    else:
        st.info("Upload cash balances or load demo data.")
        return
    if df is None:
        return
    analyzed, summary = analyze_idle_cash(df, rate=rate)
    st.session_state.idle_cash = analyzed
    for col, card in zip(st.columns(4), [
        ("Idle Cash", f"${summary['idle_cash']:,.0f}", "", "💤"),
        ("Potential Earnings", f"${summary['potential_earnings']:,.0f}", "", "📈"),
        ("Sweep Compliance", f"{summary['sweep_compliance']}%", "", "🔄"),
        ("Investment Opportunity", f"${summary['investment_opportunity']:,.0f}", "", "💰"),
    ]):
        with col: st.markdown(kpi_card(*card, color=COLORS["teal"]), unsafe_allow_html=True)
    st.markdown(gauge_html("Treasury Opportunity Score", summary["sweep_compliance"], COLORS["purple"]), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(idle_cash_trend(analyzed), use_container_width=True)
    with c2: st.plotly_chart(county_ranking(analyzed), use_container_width=True)
    st.dataframe(analyzed.head(100), use_container_width=True, hide_index=True)
