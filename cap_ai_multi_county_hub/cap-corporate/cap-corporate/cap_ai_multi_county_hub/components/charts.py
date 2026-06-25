"""Chart helpers using Plotly and Altair."""

from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import COLORS


def treasury_heatmap(county_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=go.Heatmap(
            z=[county_df["Treasury Score"], county_df["Compliance Score"], county_df["AI Readiness"]],
            x=county_df["County"],
            y=["Treasury", "Compliance", "AI Readiness"],
            colorscale=[[0, COLORS["deep_navy"]], [0.5, COLORS["royal_blue"]], [1, COLORS["teal"]]],
            text=[[f"{v:.0f}" for v in county_df["Treasury Score"]],
                  [f"{v:.0f}" for v in county_df["Compliance Score"]],
                  [f"{v:.0f}" for v in county_df["AI Readiness"]]],
            texttemplate="%{text}",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig


def county_map(county_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        county_df,
        x="Lon",
        y="Lat",
        size="Savings ($M)",
        color="Treasury Score",
        hover_name="County",
        hover_data=["Compliance Score", "AI Readiness"],
        color_continuous_scale=[COLORS["deep_navy"], COLORS["azure"], COLORS["teal"]],
        size_max=40,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
        title="County Performance Map",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    return fig


def compliance_trend() -> go.Figure:
    months = pd.date_range("2024-07", periods=12, freq="ME")
    scores = 85 + np.cumsum(np.random.default_rng(1).normal(0, 1.5, 12))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=months,
            y=scores,
            mode="lines+markers",
            line=dict(color=COLORS["teal"], width=3),
            fill="tozeroy",
            fillcolor="rgba(0, 210, 198, 0.15)",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=30, b=20),
        height=280,
        yaxis=dict(range=[80, 100]),
    )
    return fig


def savings_forecast() -> go.Figure:
    years = ["2024", "2025", "2026", "2027", "2028"]
    values = [8.2, 12.5, 18.7, 26.3, 34.1]
    fig = go.Figure(go.Bar(x=years, y=values, marker_color=COLORS["royal_blue"]))
    fig.add_trace(
        go.Scatter(x=years, y=values, mode="lines+markers", line=dict(color=COLORS["teal"], width=2))
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=30, b=20),
        height=280,
        title="Shared Services Savings Forecast ($M)",
    )
    return fig


def ai_adoption_index() -> alt.Chart:
    data = pd.DataFrame(
        {
            "Quarter": ["Q1", "Q2", "Q3", "Q4", "Q1", "Q2"],
            "Index": [42, 48, 55, 62, 71, 78],
            "Target": [45, 50, 58, 65, 72, 80],
        }
    )
    base = alt.Chart(data).encode(x=alt.X("Quarter", title=None))
    line = base.mark_line(strokeWidth=3, color=COLORS["azure"]).encode(y="Index")
    target = base.mark_line(strokeDash=[4, 4], color=COLORS["purple"]).encode(y="Target")
    return (line + target).properties(height=260)


def fraud_radar(alerts_df: pd.DataFrame) -> go.Figure:
    if alerts_df.empty:
        categories = ["Circular", "Same Amount", "Multi-Loop", "Related Party", "Structured"]
        values = [0, 0, 0, 0, 0]
    else:
        categories = ["Circular", "Same Amount", "Multi-Loop", "Related Party", "Structured"]
        pattern_map = {
            "Circular Transfer": 0,
            "Same-Amount Return": 1,
            "Multi-Account Loop": 2,
        }
        values = [0, 0, 0, 2, 1]
        for _, row in alerts_df.iterrows():
            idx = pattern_map.get(row.get("Pattern", ""), 0)
            values[idx] += 1

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(0, 210, 198, 0.3)",
            line=dict(color=COLORS["teal"]),
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.2)"), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def sankey_flow(df: pd.DataFrame) -> go.Figure:
    if df.empty or len(df) < 2:
        accounts = ["ACC-001", "ACC-002", "ACC-003", "ACC-004"]
        sources = [0, 1, 2]
        targets = [1, 2, 3]
        values = [50000, 75000, 100000]
    else:
        top = df.head(10)
        accounts = list(set(top["Accounts"].astype(str).str.split(" ↔ ").explode().tolist()))[:8]
        if len(accounts) < 2:
            accounts = ["A", "B", "C"]
        acc_idx = {a: i for i, a in enumerate(accounts)}
        sources, targets, values = [], [], []
        for _, row in top.iterrows():
            parts = str(row["Accounts"]).replace("→", "↔").split("↔")
            if len(parts) >= 2:
                s, t = parts[0].strip(), parts[1].strip()
                if s in acc_idx and t in acc_idx:
                    sources.append(acc_idx[s])
                    targets.append(acc_idx[t])
                    values.append(float(row.get("Amount", 10000)))

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(pad=15, thickness=20, line=dict(color="white", width=0.5), label=accounts,
                          color=COLORS["royal_blue"]),
                link=dict(source=sources, target=targets, value=values, color="rgba(86,199,242,0.4)"),
            )
        ]
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=400, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def charge_waterfall(variance_df: pd.DataFrame) -> go.Figure:
    if variance_df.empty:
        return go.Figure()
    fig = go.Figure(
        go.Waterfall(
            x=variance_df["Charge Type"],
            y=variance_df["Variance"],
            connector=dict(line=dict(color=COLORS["azure"])),
            increasing=dict(marker=dict(color=COLORS["danger"])),
            decreasing=dict(marker=dict(color=COLORS["teal"])),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=320,
        title="Charge Variance Waterfall",
    )
    return fig


def idle_cash_trend(cash_df: pd.DataFrame) -> go.Figure:
    daily = cash_df.groupby("Date")["Excess Cash"].sum().reset_index()
    fig = px.area(daily, x="Date", y="Excess Cash", color_discrete_sequence=[COLORS["purple"]])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=300,
        title="Idle Balance Trends",
    )
    return fig


def county_ranking(cash_df: pd.DataFrame) -> go.Figure:
    ranked = cash_df.groupby("County")["Excess Cash"].sum().sort_values(ascending=True).reset_index()
    fig = px.bar(ranked, x="Excess Cash", y="County", orientation="h", color_discrete_sequence=[COLORS["teal"]])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=300,
        title="County Idle Cash Ranking",
    )
    return fig


def ai_maturity_curve() -> go.Figure:
    stages = ["Awareness", "Experiment", "Operational", "Optimized", "Transformative"]
    scores = [100, 85, 68, 45, 22]
    fig = go.Figure(go.Funnel(y=stages, x=scores, marker=dict(color=[COLORS["azure"], COLORS["royal_blue"], COLORS["purple"], COLORS["teal"], COLORS["deep_navy"]])))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=320, title="AI Maturity Curve")
    return fig


def resource_utilization() -> go.Figure:
    categories = ["Vehicles", "Equipment", "Buildings", "Software", "Personnel"]
    utilized = [78, 65, 82, 91, 73]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Utilized", x=categories, y=utilized, marker_color=COLORS["royal_blue"]))
    fig.add_trace(go.Bar(name="Available", x=categories, y=[100 - u for u in utilized], marker_color="rgba(255,255,255,0.15)"))
    fig.update_layout(barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=280)
    return fig
