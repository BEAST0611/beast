"""Executive Command Center."""
import streamlit as st
from components.charts import ai_adoption_index, compliance_trend, county_map, resource_utilization, savings_forecast, treasury_heatmap
from components.ui import gauge_html, kpi_card, page_header, render_kpi_row, risk_thermometer, track_page_view
from utils.analytics import county_benchmark_data, dashboard_kpis
from utils.theme import COLORS

def render():
    track_page_view("Executive Command Center")
    page_header("Executive Command Center", "Real-time governance, treasury, and AI adoption intelligence")
    kpis = dashboard_kpis()
    render_kpi_row([
        ("Counties Connected", str(kpis["counties_connected"]), "+2 this quarter", "🏛️"),
        ("Shared Assets", f"{kpis['shared_assets']:,}", "+48 new", "📦"),
        ("AI Tools Shared", str(kpis["ai_tools_shared"]), "+6 deployed", "🤖"),
        ("Savings Identified", f"${kpis['savings_identified']/1e6:.1f}M", "+$2.1M", "💰"),
    ])
    render_kpi_row([
        ("High Risk Transactions", str(kpis["high_risk_transactions"]), "5 resolved", "⚠️"),
        ("Treasury Health", f"{kpis['treasury_health']}%", "+1.2 pts", "🏦"),
        ("Compliance Score", f"{kpis['compliance_score']}%", "+0.8 pts", "✅"),
        ("Training Participation", f"{kpis['training_participation']}%", "+4.2%", "🎓"),
    ])
    county_df = county_benchmark_data()
    st.markdown('<div class="section-title">Executive Scorecards</div>', unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)
    with g1: st.markdown(gauge_html("Treasury Health Index", kpis["treasury_health"], COLORS["teal"]), unsafe_allow_html=True)
    with g2: st.markdown(gauge_html("Compliance Maturity", kpis["compliance_score"], COLORS["azure"]), unsafe_allow_html=True)
    with g3: st.markdown(gauge_html("AI Readiness Score", 78.4, COLORS["purple"]), unsafe_allow_html=True)
    with g4: st.markdown(risk_thermometer(34), unsafe_allow_html=True)
    st.markdown('<div class="section-title">County Performance Intelligence</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(county_map(county_df), use_container_width=True)
    with c2: st.plotly_chart(treasury_heatmap(county_df), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(compliance_trend(), use_container_width=True)
        st.plotly_chart(resource_utilization(), use_container_width=True)
    with c4:
        st.plotly_chart(savings_forecast(), use_container_width=True)
        st.altair_chart(ai_adoption_index(), use_container_width=True)
    st.markdown('<div class="section-title">Shared Services Savings Calculator</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1: jurisdictions = st.slider("Jurisdictions Sharing", 2, 20, 8)
    with sc2: avg_budget = st.number_input("Avg. Annual Budget ($M)", 1.0, 500.0, 45.0)
    with sc3: sharing_pct = st.slider("Shared Services %", 5, 40, 15)
    projected = jurisdictions * avg_budget * (sharing_pct / 100) * 0.22
    st.markdown(kpi_card("Projected Annual Savings", f"${projected:.2f}M", "Regional benchmark", "📈", COLORS["teal"]), unsafe_allow_html=True)
    st.markdown('<div class="section-title">County Benchmarking Engine</div>', unsafe_allow_html=True)
    st.dataframe(county_df, use_container_width=True, hide_index=True)
