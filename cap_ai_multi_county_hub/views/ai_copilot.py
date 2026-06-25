"""AI Governance Copilot."""
import os
import streamlit as st
from components.ui import page_header, track_page_view
from utils.auth import log_activity

def _demo_summary(report_type):
    summaries = {
        "Executive Summary": "12 counties connected with $18.7M savings identified. 23 high-risk transactions flagged for review. Treasury health at 87.4% with improving compliance trends.",
        "Board Report": "The Multi-County Shared Services Hub has achieved 91.2% compliance maturity. Recommend board approval for expanded AI governance toolkit deployment across 4 additional jurisdictions.",
        "Audit Summary": "Round-tripping analysis detected 8 circular transfer patterns totaling $1.2M exposure. Bank charge verification identified $340 in overcharges. Signatory validation found 3 authority breaches.",
        "CFO Briefing": "Idle cash analysis reveals $4.2M in uninvested balances with estimated $189K annual opportunity cost. Sweep compliance at 68% — immediate action recommended for Franklin and Clayton counties.",
        "County Manager Report": "Shared services utilization at 78%. AI readiness index improved 12 points this quarter. Training participation at 76.8% with 4 certifications pending.",
    }
    return summaries.get(report_type, summaries["Executive Summary"])

def _openai_chat(message, context):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are CAP AI Governance Copilot for local government treasury and compliance."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {message}"},
            ],
            max_tokens=800,
        )
        return resp.choices[0].message.content
    except Exception:
        return None

def render():
    track_page_view("AI Governance Copilot")
    page_header("AI Governance Copilot", "OpenAI-powered executive intelligence and reporting")
    report_type = st.selectbox("Generate Report", ["Executive Summary", "Board Report", "Audit Summary", "CFO Briefing", "County Manager Report"])
    context_parts = []
    for key in ["round_trip_alerts", "bank_verification", "idle_cash", "signatory_issues"]:
        if key in st.session_state and st.session_state[key] is not None:
            context_parts.append(f"{key}: available")
    context = "; ".join(context_parts) if context_parts else "Demo governance data"
    if st.button("Generate Report"):
        log_activity("AI_REPORT", report_type)
        text = _openai_chat(f"Generate a {report_type} for local government shared services.", context)
        st.session_state.ai_report = text or _demo_summary(report_type)
    if st.session_state.get("ai_report"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write(st.session_state.ai_report)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Chat Assistant</div>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    prompt = st.chat_input("Ask about fraud, treasury, compliance, or savings...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        reply = _openai_chat(prompt, context) or f"Based on current CAP AI analytics: {prompt} — review the Executive Command Center for latest KPIs and flagged exceptions."
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
