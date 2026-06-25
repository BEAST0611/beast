"""Role-based authentication and audit logging."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROLES = ["Administrator", "County Manager", "Treasury Officer", "Auditor", "Viewer"]

USERS: dict[str, dict[str, str]] = {
    "admin": {"password": "admin123", "role": "Administrator", "name": "System Administrator"},
    "manager": {"password": "manager123", "role": "County Manager", "name": "County Manager"},
    "treasury": {"password": "treasury123", "role": "Treasury Officer", "name": "Treasury Officer"},
    "auditor": {"password": "auditor123", "role": "Auditor", "name": "Lead Auditor"},
    "viewer": {"password": "viewer123", "role": "Viewer", "name": "Read-Only Viewer"},
}

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent / "reports" / "audit_log.json"


def init_session() -> None:
    defaults = {
        "authenticated": False,
        "username": None,
        "user_role": None,
        "user_name": None,
        "login_time": None,
        "dark_mode": True,
        "audit_log": [],
        "show_splash": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def authenticate(username: str, password: str) -> bool:
    user = USERS.get(username.lower())
    if user and user["password"] == password:
        st.session_state.authenticated = True
        st.session_state.username = username.lower()
        st.session_state.user_role = user["role"]
        st.session_state.user_name = user["name"]
        st.session_state.login_time = datetime.now().isoformat()
        log_activity("LOGIN", f"User {username} authenticated as {user['role']}")
        return True
    log_activity("LOGIN_FAILED", f"Failed login attempt for {username}")
    return False


def logout() -> None:
    if st.session_state.get("username"):
        log_activity("LOGOUT", f"User {st.session_state.username} logged out")
    for key in ["authenticated", "username", "user_role", "user_name", "login_time"]:
        st.session_state[key] = None if key != "authenticated" else False


def has_permission(required_roles: list[str] | None = None) -> bool:
    if not st.session_state.get("authenticated"):
        return False
    if required_roles is None:
        return True
    return st.session_state.get("user_role") in required_roles


def log_activity(action: str, detail: str) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": st.session_state.get("username", "anonymous"),
        "role": st.session_state.get("user_role", "none"),
        "action": action,
        "detail": detail,
    }
    st.session_state.audit_log.append(entry)
    _persist_audit(entry)


def _persist_audit(entry: dict[str, Any]) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logs: list[dict[str, Any]] = []
    if AUDIT_LOG_PATH.exists():
        try:
            logs = json.loads(AUDIT_LOG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logs = []
    logs.append(entry)
    AUDIT_LOG_PATH.write_text(json.dumps(logs[-500:], indent=2), encoding="utf-8")


def session_token() -> str:
    raw = f"{st.session_state.get('username')}:{st.session_state.get('login_time')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
