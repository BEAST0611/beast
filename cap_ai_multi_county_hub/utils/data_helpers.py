"""Data loading, quality scoring, and sample datasets."""

from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st


def load_uploaded_file(uploaded_file) -> pd.DataFrame | None:
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        if name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Failed to load file: {exc}")
    return None


def compute_quality_metrics(df: pd.DataFrame) -> dict[str, Any]:
    rows, cols = df.shape
    duplicates = int(df.duplicated().sum())
    missing = int(df.isna().sum().sum())
    total_cells = max(rows * cols, 1)
    missing_pct = missing / total_cells
    dup_pct = duplicates / max(rows, 1)
    quality_score = max(0, min(100, round(100 - (missing_pct * 60 + dup_pct * 40) * 100, 1)))
    return {
        "rows": rows,
        "columns": cols,
        "duplicates": duplicates,
        "missing_values": missing,
        "quality_score": quality_score,
    }


def sample_transactions() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    counties = ["Jefferson", "Madison", "Franklin", "Hamilton", "Clayton"]
    accounts = [f"ACC-{i:04d}" for i in range(1, 21)]
    types = ["Transfer", "Payment", "Deposit", "Withdrawal"]
    rows = []
    for i in range(120):
        amount = round(rng.uniform(5000, 250000), 2)
        rows.append(
            {
                "Transaction ID": f"TXN-{1000 + i}",
                "Date": pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 180))),
                "Account": rng.choice(accounts),
                "Counterparty": rng.choice(accounts),
                "Amount": amount,
                "Reference": f"REF-{rng.integers(10000, 99999)}",
                "Transaction Type": rng.choice(types),
                "County": rng.choice(counties),
            }
        )
    # Inject round-trip patterns
    for j in range(8):
        amt = round(rng.uniform(25000, 100000), 2)
        d = pd.Timestamp("2025-03-01") + pd.Timedelta(days=j * 3)
        a, b = accounts[j], accounts[j + 1]
        rows.append(
            {
                "Transaction ID": f"TXN-RT-{j}A",
                "Date": d,
                "Account": a,
                "Counterparty": b,
                "Amount": amt,
                "Reference": f"LOOP-{j}",
                "Transaction Type": "Transfer",
                "County": counties[j % len(counties)],
            }
        )
        rows.append(
            {
                "Transaction ID": f"TXN-RT-{j}B",
                "Date": d + pd.Timedelta(days=2),
                "Account": b,
                "Counterparty": a,
                "Amount": amt,
                "Reference": f"LOOP-{j}",
                "Transaction Type": "Transfer",
                "County": counties[j % len(counties)],
            }
        )
    return pd.DataFrame(rows)


def sample_bank_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    statements = pd.DataFrame(
        {
            "Account": ["MAIN-001", "MAIN-001", "SWEEP-002", "SWEEP-002"],
            "Charge Type": ["Monthly Fee", "Wire Fee", "Interest Credit", "Maintenance"],
            "Actual": [125.0, 35.0, 842.5, 45.0],
            "Period": ["2025-Q1", "2025-Q1", "2025-Q1", "2025-Q1"],
        }
    )
    terms = pd.DataFrame(
        {
            "Account": ["MAIN-001", "MAIN-001", "SWEEP-002", "SWEEP-002"],
            "Charge Type": ["Monthly Fee", "Wire Fee", "Interest Credit", "Maintenance"],
            "Expected": [100.0, 25.0, 920.0, 30.0],
            "Rate": [0.042, 0.038, 0.045, 0.0],
        }
    )
    return statements, terms


def sample_cash_balances() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    counties = ["Jefferson", "Madison", "Franklin", "Hamilton", "Clayton"]
    rows = []
    for day in range(30):
        for county in counties:
            balance = round(rng.uniform(800000, 4500000), 2)
            threshold = 500000
            rows.append(
                {
                    "Date": pd.Timestamp("2025-01-01") + pd.Timedelta(days=day),
                    "Account": f"{county[:3].upper()}-OPS",
                    "Balance": balance,
                    "Operating Threshold": threshold,
                    "County": county,
                }
            )
    return pd.DataFrame(rows)


def sample_signatory_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    master = pd.DataFrame(
        {
            "Signatory": ["J. Smith", "A. Johnson", "R. Davis", "M. Wilson"],
            "Role": ["CFO", "Treasurer", "Deputy Treasurer", "Clerk"],
            "Limit": [500000, 250000, 100000, 50000],
            "Expiry": ["2026-12-31", "2026-06-30", "2025-12-31", "2025-03-01"],
            "Status": ["Active", "Active", "Active", "Expired"],
        }
    )
    approvals = pd.DataFrame(
        {
            "Transaction": ["PAY-1001", "PAY-1002", "PAY-1003", "PAY-1004", "PAY-1005"],
            "Amount": [120000, 320000, 85000, 450000, 42000],
            "Approver": ["J. Smith", "R. Davis", "M. Wilson", "A. Johnson", "Unknown User"],
            "Date": ["2025-02-01", "2025-02-05", "2025-02-10", "2025-02-15", "2025-02-20"],
        }
    )
    return master, approvals


def df_to_excel_bytes(df_dict: dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet, frame in df_dict.items():
            frame.to_excel(writer, sheet_name=sheet[:31], index=False)
    return buffer.getvalue()
