import os
import uuid
import pandas as pd
from typing import Dict, Any
from app.core.config import settings


def _base_frame(result: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for section, items in (
        ("Insight", result.get("insights", [])),
        ("Recommendation", result.get("recommendations", [])),
        ("Risk Alert", result.get("risk_alerts", [])),
    ):
        for item in items:
            rows.append({"Section": section, "Detail": item})
    if not rows:
        rows = [{"Section": "Info", "Detail": "No content generated for this query."}]
    return pd.DataFrame(rows)


def generate_csv(result: Dict[str, Any]) -> str:
    df = _base_frame(result)
    path = os.path.join(settings.report_dir, f"report_{uuid.uuid4().hex}.csv")
    df.to_csv(path, index=False)
    return path


def generate_excel(result: Dict[str, Any]) -> str:
    df = _base_frame(result)
    path = os.path.join(settings.report_dir, f"report_{uuid.uuid4().hex}.xlsx")
    df.to_excel(path, index=False)
    return path


def generate_pdf(result: Dict[str, Any], query_text: str = "") -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

    path = os.path.join(settings.report_dir, f"report_{uuid.uuid4().hex}.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Supply Chain Agent — Query Report", styles["Title"]), Spacer(1, 12)]

    if query_text:
        story.append(Paragraph(f"<b>Query:</b> {query_text}", styles["Normal"]))
        story.append(Spacer(1, 12))

    for title, key in (("Insights", "insights"), ("Recommendations", "recommendations"), ("Risk Alerts", "risk_alerts")):
        items = result.get(key, [])
        story.append(Paragraph(title, styles["Heading2"]))
        if items:
            story.append(ListFlowable([ListItem(Paragraph(i, styles["Normal"])) for i in items], bulletType="bullet"))
        else:
            story.append(Paragraph("None.", styles["Normal"]))
        story.append(Spacer(1, 12))

    doc.build(story)
    return path
