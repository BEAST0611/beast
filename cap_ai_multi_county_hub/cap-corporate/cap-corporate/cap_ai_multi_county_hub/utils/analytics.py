"""Financial analytics engines for CAP AI modules."""

from __future__ import annotations

from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd


def detect_round_tripping(
    df: pd.DataFrame,
    window_days: int = 7,
    amount_tolerance: float = 0.01,
) -> pd.DataFrame:
    required = ["Date", "Account", "Counterparty", "Amount", "Reference", "Transaction Type", "County"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    work = df.copy()
    work["Date"] = pd.to_datetime(work["Date"])
    work["Amount"] = pd.to_numeric(work["Amount"], errors="coerce")
    work = work.dropna(subset=["Date", "Account", "Counterparty", "Amount"])

    alerts = []
    seen_pairs: set[tuple] = set()

    for _, row in work.iterrows():
        mask = (
            (work["Account"] == row["Counterparty"])
            & (work["Counterparty"] == row["Account"])
            & (work["Date"] > row["Date"])
            & (work["Date"] <= row["Date"] + pd.Timedelta(days=window_days))
        )
        matches = work[mask]
        for _, ret in matches.iterrows():
            amt_diff = abs(ret["Amount"] - row["Amount"]) / max(row["Amount"], 1)
            if amt_diff <= amount_tolerance:
                key = tuple(sorted([str(row.name), str(ret.name)]))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                risk = min(99, 60 + int(amt_diff * 100) + (5 if row["Reference"] == ret["Reference"] else 20))
                alerts.append(
                    {
                        "Transaction ID": row.get("Transaction ID", f"TX-{row.name}"),
                        "Risk Score": risk,
                        "Confidence Score": min(98, risk + 5),
                        "Amount": row["Amount"],
                        "Accounts": f"{row['Account']} ↔ {row['Counterparty']}",
                        "Pattern": "Same-Amount Return" if row["Reference"] != ret["Reference"] else "Circular Transfer",
                        "Alert Level": "High" if risk >= 80 else "Medium" if risk >= 60 else "Low",
                        "Exposure Amount": row["Amount"] + ret["Amount"],
                        "County": row.get("County", ""),
                        "Days Between": (ret["Date"] - row["Date"]).days,
                    }
                )

    # Multi-account loops via networkx
    g = nx.DiGraph()
    for _, r in work.iterrows():
        g.add_edge(str(r["Account"]), str(r["Counterparty"]), weight=float(r["Amount"]), ref=r.get("Reference", ""))

    for cycle in nx.simple_cycles(g):
        if 2 <= len(cycle) <= 5:
            cycle_key = tuple(sorted(cycle))
            if cycle_key in seen_pairs:
                continue
            seen_pairs.add(cycle_key)
            exposure = sum(g[cycle[i]][cycle[(i + 1) % len(cycle)]]["weight"] for i in range(len(cycle)))
            alerts.append(
                {
                    "Transaction ID": f"LOOP-{'-'.join(cycle[:3])}",
                    "Risk Score": min(95, 70 + len(cycle) * 5),
                    "Confidence Score": 75 + len(cycle) * 3,
                    "Amount": exposure / len(cycle),
                    "Accounts": " → ".join(cycle + [cycle[0]]),
                    "Pattern": "Multi-Account Loop",
                    "Alert Level": "High",
                    "Exposure Amount": exposure,
                    "County": "",
                    "Days Between": window_days,
                }
            )

    if not alerts:
        return pd.DataFrame(
            columns=[
                "Transaction ID", "Risk Score", "Confidence Score", "Amount", "Accounts",
                "Pattern", "Alert Level", "Exposure Amount", "County", "Days Between",
            ]
        )
    return pd.DataFrame(alerts).sort_values("Risk Score", ascending=False).reset_index(drop=True)


def verify_bank_charges(statements: pd.DataFrame, terms: pd.DataFrame) -> pd.DataFrame:
    merged = statements.merge(terms, on=["Account", "Charge Type"], how="outer", suffixes=("_actual", "_expected"))
    merged["Actual"] = merged.get("Actual", merged.get("Actual_actual", 0)).fillna(0)
    merged["Expected"] = merged.get("Expected", merged.get("Expected_expected", 0)).fillna(0)
    merged["Variance"] = merged["Actual"] - merged["Expected"]
    merged["Impact"] = merged["Variance"].abs()
    merged["Risk"] = np.where(
        merged["Variance"].abs() > merged["Expected"].abs() * 0.1,
        "High",
        np.where(merged["Variance"].abs() > 0, "Medium", "Low"),
    )
    merged["Flag"] = np.select(
        [
            merged["Variance"] > 0,
            merged["Variance"] < 0,
            merged["Variance"] == 0,
        ],
        ["Overcharge", "Undercharge", "Matched"],
        default="Review",
    )
    return merged[["Account", "Charge Type", "Expected", "Actual", "Variance", "Impact", "Risk", "Flag"]]


def analyze_idle_cash(df: pd.DataFrame, rate: float = 0.045) -> tuple[pd.DataFrame, dict]:
    work = df.copy()
    work["Date"] = pd.to_datetime(work["Date"])
    work["Balance"] = pd.to_numeric(work["Balance"], errors="coerce")
    work["Operating Threshold"] = pd.to_numeric(work["Operating Threshold"], errors="coerce")
    work["Excess Cash"] = (work["Balance"] - work["Operating Threshold"]).clip(lower=0)
    work["Idle"] = work["Excess Cash"] > 0
    work["Daily Lost Interest"] = work["Excess Cash"] * (rate / 365)

    summary = {
        "idle_cash": float(work["Excess Cash"].sum()),
        "potential_earnings": float(work["Daily Lost Interest"].sum()),
        "sweep_compliance": round(100 - (work["Idle"].mean() * 100), 1),
        "investment_opportunity": float(work.groupby("County")["Excess Cash"].mean().max() or 0),
    }
    return work, summary


def validate_signatories(master: pd.DataFrame, approvals: pd.DataFrame) -> pd.DataFrame:
    master = master.copy()
    approvals = approvals.copy()
    master["Expiry"] = pd.to_datetime(master["Expiry"])
    issues = []

    auth_map = {row["Signatory"]: row for _, row in master.iterrows()}

    for _, txn in approvals.iterrows():
        approver = txn["Approver"]
        amount = float(txn["Amount"])
        if approver not in auth_map:
            issues.append(
                {
                    "Transaction": txn["Transaction"],
                    "Approver": approver,
                    "Issue": "Unauthorized approval",
                    "Severity": "Critical",
                    "Recommendation": "Reject payment and investigate approver credentials",
                }
            )
            continue

        sig = auth_map[approver]
        if sig["Status"] == "Expired" or sig["Expiry"] < pd.Timestamp.now():
            issues.append(
                {
                    "Transaction": txn["Transaction"],
                    "Approver": approver,
                    "Issue": "Expired mandate",
                    "Severity": "High",
                    "Recommendation": "Renew signatory mandate before processing",
                }
            )
        if amount > float(sig["Limit"]):
            issues.append(
                {
                    "Transaction": txn["Transaction"],
                    "Approver": approver,
                    "Issue": "Exceeded authority limit",
                    "Severity": "High",
                    "Recommendation": f"Requires secondary approval above ${sig['Limit']:,.0f}",
                }
            )

    return pd.DataFrame(issues)


def county_benchmark_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "County": ["Jefferson", "Madison", "Franklin", "Hamilton", "Clayton", "Washington", "Lincoln"],
            "Treasury Score": [88, 92, 76, 85, 79, 91, 83],
            "Compliance Score": [90, 87, 72, 88, 81, 93, 86],
            "AI Readiness": [78, 85, 65, 80, 70, 88, 74],
            "Savings ($M)": [2.4, 3.1, 1.2, 2.8, 1.5, 3.4, 2.0],
            "Lat": [38.25, 38.45, 38.15, 38.35, 38.55, 38.05, 38.65],
            "Lon": [-85.75, -85.55, -85.95, -85.65, -85.45, -86.05, -85.35],
        }
    )


def dashboard_kpis() -> dict:
    return {
        "counties_connected": 12,
        "shared_assets": 847,
        "ai_tools_shared": 34,
        "savings_identified": 18_700_000,
        "high_risk_transactions": 23,
        "treasury_health": 87.4,
        "compliance_score": 91.2,
        "training_participation": 76.8,
    }
