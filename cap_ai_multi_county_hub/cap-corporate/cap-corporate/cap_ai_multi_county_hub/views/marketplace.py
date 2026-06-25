"""Shared Services Marketplace."""
import streamlit as st
from components.ui import page_header, track_page_view

ITEMS = [
    {"title": "Fleet Vehicle Pool", "category": "Vehicles", "icon": "V", "available": 12, "utilization": 78, "savings": "$45K/yr"},
    {"title": "GIS Software License", "category": "Software Licenses", "icon": "S", "available": 5, "utilization": 91, "savings": "$28K/yr"},
    {"title": "Training Facility", "category": "Buildings", "icon": "B", "available": 3, "utilization": 65, "savings": "$62K/yr"},
    {"title": "Senior Finance Officer", "category": "Finance Officers", "icon": "F", "available": 2, "utilization": 100, "savings": "$95K/yr"},
    {"title": "Heavy Equipment Share", "category": "Equipment", "icon": "E", "available": 8, "utilization": 72, "savings": "$38K/yr"},
    {"title": "AI Governance Specialist", "category": "AI Specialists", "icon": "A", "available": 1, "utilization": 85, "savings": "$52K/yr"},
]

def render():
    track_page_view("Shared Services Marketplace")
    page_header("Shared Services Marketplace", "Share assets and expertise across jurisdictions")
    cat = st.selectbox("Category", ["All"] + sorted(set(i["category"] for i in ITEMS)))
    filtered = ITEMS if cat == "All" else [i for i in ITEMS if i["category"] == cat]
    cols = st.columns(3)
    for idx, item in enumerate(filtered):
        with cols[idx % 3]:
            st.markdown(f"""<div class="marketplace-card"><div class="card-img">{item['icon']}</div><div class="card-body"><h4>{item['title']}</h4><p>{item['category']} · {item['available']} available · {item['utilization']}% utilized</p><p>Est. savings: {item['savings']}</p></div></div>""", unsafe_allow_html=True)
            if st.button("Request Booking", key=f"book_{idx}"):
                st.success(f"Booking request sent for {item['title']}")
