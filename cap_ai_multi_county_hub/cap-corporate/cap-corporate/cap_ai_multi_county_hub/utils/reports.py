"""PDF and Excel report generation with CAP AI branding."""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.theme import LOGO_PATH

EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"


def generate_executive_pdf(
    title: str,
    summary: str,
    findings: list[str],
    recommendations: list[str],
    kpis: dict | None = None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CAPTitle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#2046C9"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    subtitle_style = ParagraphStyle(
        "CAPSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#0D1B5E"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    body = styles["Normal"]

    story = []
    if LOGO_PATH.exists():
        story.append(Image(str(LOGO_PATH), width=1.8 * inch, height=1.8 * inch))
        story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("CAP AI", title_style))
    story.append(Paragraph("Multi-County Shared Services Hub™", subtitle_style))
    story.append(Paragraph(title, styles["Heading2"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}", body))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading3"]))
    story.append(Paragraph(summary, body))
    story.append(Spacer(1, 0.2 * inch))

    if kpis:
        kpi_data = [["Metric", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in kpis.items()]
        t = Table(kpi_data, colWidths=[3 * inch, 2 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2046C9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#E8F4FD")]),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("<b>Key Findings</b>", styles["Heading3"]))
    for f in findings:
        story.append(Paragraph(f"• {f}", body))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Recommendations</b>", styles["Heading3"]))
    for r in recommendations:
        story.append(Paragraph(f"• {r}", body))

    doc.build(story)
    return buffer.getvalue()


def generate_audit_workbook(data: dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet, frame in data.items():
            frame.to_excel(writer, sheet_name=sheet[:31], index=False)
            ws = writer.sheets[sheet[:31]]
            ws.set_column(0, max(len(frame.columns) - 1, 0), 18)
    return buffer.getvalue()


def save_export(filename: str, content: bytes) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / filename
    path.write_bytes(content)
    return path
