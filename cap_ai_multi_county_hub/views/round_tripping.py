"""Round-Tripping Detection Engine."""
import tempfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from components.charts import fraud_radar, sankey_flow
from components.ui import kpi_card, page_header, track_page_view
from utils.analytics import detect_round_tripping
from utils.data_helpers import load_uploaded_file, sample_transactions

def _network_graph(alerts_df):
    try:
        import networkx as nx
        from pyvis.network import Network
        g = nx.Graph()
        if alerts_df.empty:
            g.add_edge("ACC-001", "ACC-002")
            g.add_edge("ACC-002", "ACC-003")
        else:
            for _, row in alerts_df.head(15).iterrows():
                parts = str(row["Accounts"]).replace("→", "↔").split("↔")
                if len(parts) >= 2:
                    g.add_edge(parts[0].strip(), parts[1].strip())
        net = Network(height="400px", width="100%", bgcolor="#0D1B5E", font_color="white")
        net.from_nx(g)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            html = Path(tmp.name).read_text(encoding="utf-8")
        components.html(html, height=420)
    except Exception as exc:
        st.warning(f"Network graph unavailable: {exc}")

def render():
    track_page_view("Round-Tripping Detection")
    page_header("Round-Tripping Detection Engine", "Identify circular movement of public funds")
    window_days = st.sidebar.slider("Return Window (days)", 1, 30, 7)
    amount_tol = st.sidebar.slider("Amount Tolerance (%)", 0.0, 5.0, 1.0) / 100
    uploaded = st.file_uploader("Upload Transactions Workbook", type=["xlsx", "xls", "csv"])
    if uploaded:
        df = load_uploaded_file(uploaded)
    elif st.button("Run Demo Analysis"):
        df = sample_transactions()
    else:
        st.info("Upload transactions or run demo analysis.")
        return
    if df is None:
        return
    try:
        alerts = detect_round_tripping(df, window_days=window_days, amount_tolerance=amount_tol)
    except ValueError as exc:
        st.error(str(exc))
        return
    st.session_state.round_trip_alerts = alerts
    high = len(alerts[alerts["Alert Level"] == "High"]) if not alerts.empty else 0
    exposure = alerts["Exposure Amount"].sum() if not alerts.empty else 0
    avg_risk = alerts["Risk Score"].mean() if not alerts.empty else 0
    for col, card in zip(st.columns(4), [
        ("Alerts Detected", str(len(alerts)), "", "🚨"),
        ("High Risk", str(high), "", "⚠️"),
        ("Total Exposure", f"${exposure:,.0f}", "", "💸"),
        ("Avg Risk Score", f"{avg_risk:.0f}", "", "📊"),
    ]):
        with col:
            st.markdown(kpi_card(*card), unsafe_allow_html=True)
    st.markdown('<div class="section-title">Fraud Radar & Flow Analysis</div>', unsafe_allow_html=True)
    v1, v2 = st.columns(2)
    with v1: st.plotly_chart(fraud_radar(alerts), use_container_width=True)
    with v2: st.plotly_chart(sankey_flow(alerts), use_container_width=True)
    st.markdown('<div class="section-title">Transaction Relationship Map</div>', unsafe_allow_html=True)
    _network_graph(alerts)
    st.markdown('<div class="section-title">Detection Results</div>', unsafe_allow_html=True)
    if not alerts.empty:
        st.dataframe(alerts, use_container_width=True, hide_index=True)
    else:
        st.success("No round-tripping patterns detected.")
