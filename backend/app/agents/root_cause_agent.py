import pandas as pd
from typing import Dict, Any


def _find_col(roles: Dict[str, str], role: str):
    for col, r in roles.items():
        if r == role:
            return col
    return None


def run(df: pd.DataFrame, roles: Dict[str, str], query: str, disrupted_indices=None) -> Dict[str, Any]:
    insights, charts, recommendations = [], [], []

    disrupted = df.loc[df.index.intersection(disrupted_indices)] if disrupted_indices else pd.DataFrame()
    if disrupted.empty:
        disrupted = df  # fall back to whole dataset if disruption agent found nothing specific

    candidate_dims = []
    for role in ("supplier", "location", "product", "id"):
        col = _find_col(roles, role)
        if col:
            candidate_dims.append((role, col))

    if not candidate_dims or disrupted.empty:
        insights.append("Not enough categorical context (supplier/location/product) to isolate a root cause.")
        return {"insights": insights, "charts": charts, "recommendations": recommendations, "risk_alerts": []}

    for role, col in candidate_dims:
        counts = disrupted[col].value_counts()
        if counts.empty:
            continue
        top = counts.head(5)
        share = top.iloc[0] / len(disrupted) * 100 if len(disrupted) else 0
        insights.append(
            f"Top {role} contributing to disruptions: '{top.index[0]}' "
            f"({top.iloc[0]} of {len(disrupted)} disrupted records, {share:.0f}%)."
        )
        charts.append({
            "type": "bar", "title": f"Disrupted records by {col}",
            "x": col, "data": top.to_dict(),
        })
        if share > 30:
            recommendations.append(
                f"Investigate '{top.index[0]}' ({role}) directly — it accounts for {share:.0f}% "
                f"of disrupted records, the largest single contributor."
            )

    return {"insights": insights, "charts": charts, "recommendations": recommendations, "risk_alerts": []}
