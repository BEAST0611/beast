"""Administration."""
import json
import streamlit as st
from components.ui import page_header, track_page_view
from utils.auth import ROLES, USERS, AUDIT_LOG_PATH, log_activity

def render():
    track_page_view("Administration")
    page_header("Administration", "User management, roles, and audit logging")
    tab1, tab2, tab3 = st.tabs(["Users & Roles", "Audit Log", "Session"])
    with tab1:
        st.markdown("**Demo Accounts** (change in production)")
        user_rows = [{"Username": k, "Name": v["name"], "Role": v["role"]} for k, v in USERS.items()]
        st.dataframe(user_rows, use_container_width=True, hide_index=True)
        st.multiselect("Available Roles", ROLES, default=ROLES)
    with tab2:
        if AUDIT_LOG_PATH.exists():
            logs = json.loads(AUDIT_LOG_PATH.read_text(encoding="utf-8"))
            st.dataframe(logs[-50:], use_container_width=True)
        else:
            st.info("No audit entries yet.")
        if st.session_state.get("audit_log"):
            st.dataframe(st.session_state.audit_log[-20:], use_container_width=True)
    with tab3:
        st.json({
            "user": st.session_state.get("username"),
            "role": st.session_state.get("user_role"),
            "login_time": st.session_state.get("login_time"),
        })
        if st.button("Log Test Event"):
            log_activity("TEST", "Administration test event")
            st.success("Event logged.")
