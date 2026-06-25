"""Bank Charges Verification."""
import plotly.express as px
import streamlit as st
from components.charts import charge_waterfall
from components.ui import kpi_card, page_header, track_page_view
from utils.analytics import verify_bank_charges
from utils.data_helpers import load_uploaded_file, sample_bank_data
from utils.theme import COLORS

def render():
    track_page_view("Bank Charges Verification")
    page_header("Bank Charges & Interest Verification", "Verify bank charges against approved treasury agreements")
    c1, c2 = st.columns(2)
    with c1: stmt_file = st.file_uploader("Bank Statements", type=["xlsx", "csv"], key="bank_stmt")
    with c2: terms_file = st.file_uploader("Approved Banking Terms", type=["xlsx", "csv"], key="bank_terms")
    if st.button("Load Demo Data"):
        statements, terms = sample_bank_data()
    elif stmt_file and terms_file:
        statements = load_uploaded_file(stmt_file)
        terms = load_uploaded_file(terms_file)
    else:
        st.info("Upload files or load demo data.")
        return
    if statements is None or terms is None:
        return
    results = verify_bank_charges(statements, terms)
    st.session_state.bank_verification = results
    for col, card in zip(st.columns(4), [
        ("Accounts Reviewed", str(results["Account"].nunique()), "", "🏦"),
        ("Overcharges", str(len(results[results['Flag'] == 'Overcharge'])), "", "📈"),
        ("Net Variance", f"${results['Variance'].sum():,.2f}", "", "💰"),
        ("High Risk Items", str(len(results[results['Risk'] == 'High'])), "", "⚠️"),
    ]):
        with col: st.markdown(kpi_card(*card), unsafe_allow_html=True)
    st.plotly_chart(charge_waterfall(results), use_container_width=True)
    fig = px.bar(results, x="Charge Type", y=["Expected", "Actual"], barmode="group", color_discrete_sequence=[COLORS["teal"], COLORS["purple"]])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=300)
    st.plotly_chart(fig, use_container_width=True)
    output = results.rename(columns={"Flag": "Impact"})[["Account", "Expected", "Actual", "Variance", "Impact", "Risk"]]
    st.dataframe(output, use_container_width=True, hide_index=True)
