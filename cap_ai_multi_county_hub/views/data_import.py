"""Data Import Hub."""
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from components.ui import kpi_card, page_header, track_page_view
from utils.data_helpers import compute_quality_metrics, df_to_excel_bytes, load_uploaded_file, sample_transactions
from utils.theme import COLORS

def render():
    track_page_view("Data Import Hub")
    page_header("Data Import Hub", "Enterprise drag-and-drop ingestion with data quality intelligence")
    uploaded = st.file_uploader("Drag and drop your file here", type=["xlsx", "xls", "csv"])
    if "imported_df" not in st.session_state:
        st.session_state.imported_df = None
    if uploaded:
        df = load_uploaded_file(uploaded)
        if df is not None:
            st.session_state.imported_df = df
            st.success(f"Loaded {uploaded.name} — {len(df):,} rows")
    if st.button("Load Sample Dataset"):
        st.session_state.imported_df = sample_transactions()
    df = st.session_state.imported_df
    if df is None:
        st.info("Upload a file or load the sample dataset to begin.")
        return
    metrics = compute_quality_metrics(df)
    cols = st.columns(5)
    cards = [
        ("Rows", f"{metrics['rows']:,}", "", "📋"),
        ("Columns", str(metrics["columns"]), "", "📊"),
        ("Duplicates", str(metrics["duplicates"]), "", "🔄"),
        ("Missing Values", str(metrics["missing_values"]), "", "❓"),
        ("Quality Score", f"{metrics['quality_score']}%", "", "⭐"),
    ]
    for col, card in zip(cols, cards):
        with col:
            st.markdown(kpi_card(*card, color=COLORS["azure"]), unsafe_allow_html=True)
    st.markdown('<div class="section-title">Interactive Data Preview</div>', unsafe_allow_html=True)
    search = st.text_input("Search across all columns")
    filtered = df
    if search:
        mask = df.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
        filtered = df[mask]
    gb = GridOptionsBuilder.from_dataframe(filtered)
    gb.configure_default_column(filterable=True, sortable=True, resizable=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    AgGrid(filtered, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE, theme="streamlit", height=450)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Export CSV", filtered.to_csv(index=False).encode("utf-8"), "cap_ai_export.csv")
    with c2:
        st.download_button("Export Excel", df_to_excel_bytes({"Data": filtered}), "cap_ai_export.xlsx")
