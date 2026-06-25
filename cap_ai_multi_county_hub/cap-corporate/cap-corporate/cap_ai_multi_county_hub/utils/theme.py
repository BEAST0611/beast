"""CAP AI theme constants and CSS injection."""

from pathlib import Path

COLORS = {
    "royal_blue": "#2046C9",
    "azure": "#56C7F2",
    "deep_navy": "#0D1B5E",
    "teal": "#00D2C6",
    "purple": "#6C63FF",
    "gradient_start": "#081B4B",
    "gradient_mid": "#1A4FB7",
    "gradient_end": "#56C7F2",
    "glass_bg": "rgba(255, 255, 255, 0.08)",
    "glass_border": "rgba(255, 255, 255, 0.18)",
    "text_primary": "#FFFFFF",
    "text_muted": "rgba(255, 255, 255, 0.72)",
    "success": "#00D2C6",
    "warning": "#FFB347",
    "danger": "#FF6B6B",
}

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "cap_ai_logo.png"
CSS_PATH = ASSETS_DIR / "custom.css"


def inject_theme() -> None:
    import streamlit as st

    css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else _fallback_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _fallback_css() -> str:
    return f"""
    .stApp {{
        background: linear-gradient(135deg, {COLORS['gradient_start']} 0%, {COLORS['gradient_mid']} 50%, {COLORS['gradient_end']} 100%);
        background-attachment: fixed;
    }}
    """
