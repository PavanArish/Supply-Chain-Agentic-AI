import pandas as pd
from typing import Dict, Any
from app.services.external.news_service import get_relevant_events


def _find_col(roles: Dict[str, str], role: str):
    for col, r in roles.items():
        if r == role:
            return col
    return None


def run(df: pd.DataFrame, roles: Dict[str, str], query: str, disrupted_indices=None) -> Dict[str, Any]:
    insights, charts, risk_alerts = [], [], []

    disrupted_count = len(disrupted_indices) if disrupted_indices else 0
    total = len(df)
    disruption_rate = (disrupted_count / total * 100) if total else 0

    supplier_col = _find_col(roles, "supplier")
    location_col = _find_col(roles, "location")

    risk_score = min(100, round(disruption_rate * 1.5))
    insights.append(f"Overall risk score: {risk_score}/100, based on a {disruption_rate:.0f}% disruption rate.")

    if risk_score >= 60:
        risk_alerts.append(f"High overall risk exposure ({risk_score}/100) — recommend proactive mitigation.")
    elif risk_score >= 30:
        risk_alerts.append(f"Moderate risk exposure ({risk_score}/100) — monitor closely.")

    concentration_dim = supplier_col or location_col
    if concentration_dim and total:
        counts = df[concentration_dim].value_counts(normalize=True)
        if not counts.empty and counts.iloc[0] > 0.4:
            risk_alerts.append(
                f"Supply concentration risk: '{counts.index[0]}' represents "
                f"{counts.iloc[0]*100:.0f}% of all records in '{concentration_dim}' — a single point of failure."
            )
            charts.append({
                "type": "pie", "title": f"Concentration by {concentration_dim}",
                "data": (counts.head(6) * 100).round(1).to_dict(),
            })

    keywords = [str(v) for v in (df[supplier_col].dropna().unique()[:5].tolist() if supplier_col else [])]
    events = get_relevant_events(keywords)
    for e in events:
        insights.append(f"External signal: {e.get('headline')} ({e.get('source')})")

    return {"insights": insights, "charts": charts, "recommendations": [], "risk_alerts": risk_alerts,
            "risk_score": risk_score}
