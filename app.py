"""CAP AI — Multi-County Shared Services Hub."""
import sys
import time
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import particle_background, render_logo
from utils.auth import authenticate, init_session, logout, session_token
from utils.theme import COLORS, inject_theme, LOGO_PATH

st.set_page_config(
    page_title="CAP AI | Multi-County Shared Services Hub",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()
init_session()
particle_background()

MENU_ITEMS = [
    "Dashboard", "Data Import", "Round-Tripping Detection", "Bank Charges Verification",
    "Idle Cash Monitoring", "Signatory Validation", "AI Insights",
    "Shared Services Marketplace", "Training & AI Adoption", "Reports", "Administration",
]
MENU_ICONS = ["house", "cloud-upload", "arrow-repeat", "bank", "cash-stack", "pen", "robot", "shop", "mortarboard", "bar-chart", "gear"]

PAGE_MAP = {
    "Dashboard": "pages.dashboard",
    "Data Import": "pages.data_import",
    "Round-Tripping Detection": "pages.round_tripping",
    "Bank Charges Verification": "pages.bank_verification",
    "Idle Cash Monitoring": "pages.idle_cash",
    "Signatory Validation": "pages.signatory_validation",
    "AI Insights": "pages.ai_copilot",
    "Shared Services Marketplace": "pages.marketplace",
    "Training & AI Adoption": "pages.training_hub",
    "Reports": "pages.reporting",
    "Administration": "pages.administration",
}


def show_splash():
    if st.session_state.get("show_splash"):
        logo_html = ""
        if LOGO_PATH.exists():
            import base64
            logo_html = f'<img src="data:image/png;base64,{base64.b64encode(LOGO_PATH.read_bytes()).decode()}" width="120"/>'
        st.markdown(f"""<div class="splash-screen">{logo_html}<div class="splash-title">CAP AI</div><div class="splash-sub">Multi-County Shared Services Hub™</div></div>""", unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.show_splash = False
        st.rerun()


def show_login():
    st.markdown("""<div class="landing-hero"><h1>CAP AI</h1><div class="tagline">Multi-County Shared Services Hub™</div><p style="color:rgba(255,255,255,0.8);margin:1rem 0;">Helping Small Jurisdictions Share Services, Strengthen Governance, Reduce Costs, and Accelerate AI Adoption.</p><div class="pillars"><div class="landing-pillar">Share Services.</div><div class="landing-pillar">Reduce Costs.</div><div class="landing-pillar">Strengthen Controls.</div><div class="landing-pillar">Enable AI.</div></div></div>""", unsafe_allow_html=True)
    render_logo(140, centered=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### Secure Sign In")
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Administrator", "County Manager", "Treasury Officer", "Auditor", "Viewer"])
        if st.button("Sign In to CAP AI", use_container_width=True):
            if authenticate(username, password):
                st.session_state.user_role = role
                st.rerun()
            else:
                st.error("Invalid credentials. Try demo: admin / admin123")
        with st.expander("Demo Credentials"):
            st.code("admin / admin123\nmanager / manager123\ntreasury / treasury123\nauditor / auditor123\nviewer / viewer123")
        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        render_logo(100)
        st.markdown("**CAP AI**\nMulti-County Shared Services Hub™")
        st.caption(f"Session: {session_token()}")
        st.caption(f"Role: {st.session_state.get('user_role', 'N/A')}")
        selected = option_menu(
            menu_title=None,
            options=MENU_ITEMS,
            icons=MENU_ICONS,
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "nav-link": {"font-size": "14px", "color": "#fff", "margin": "2px 0"},
                "nav-link-selected": {"background-color": COLORS["royal_blue"], "color": "#fff"},
            },
        )
        st.markdown("---")
        st.toggle("Dark Mode", value=st.session_state.get("dark_mode", True), key="dark_mode_toggle")
        if st.button("Sign Out", use_container_width=True):
            logout()
            st.rerun()
        return selected


def main():
    if st.session_state.get("show_splash") and st.session_state.get("authenticated"):
        show_splash()
        return
    if not st.session_state.get("authenticated"):
        show_login()
        return
    selected = render_sidebar()
    module = __import__(PAGE_MAP[selected], fromlist=["render"])
    module.render()


main()
