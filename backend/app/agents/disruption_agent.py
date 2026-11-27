import pandas as pd
from typing import Dict, Any


def _find_col(roles: Dict[str, str], role: str):
    for col, r in roles.items():
        if r == role:
            return col
    return None


def run(df: pd.DataFrame, roles: Dict[str, str], query: str) -> Dict[str, Any]:
    insights, charts, risk_alerts = [], [], []

    delay_col = _find_col(roles, "delay")
    status_col = _find_col(roles, "status")

    disrupted = pd.DataFrame()

    if delay_col and pd.api.types.is_numeric_dtype(df[delay_col]):
        threshold = df[delay_col].mean() + df[delay_col].std() if df[delay_col].std() > 0 else 0
        disrupted = df[df[delay_col] > max(threshold, 0)]
        insights.append(
            f"{len(disrupted)} of {len(df)} records show above-average delay in '{delay_col}' "
            f"(threshold ≈ {threshold:.1f})."
        )
        charts.append({
            "type": "histogram", "title": f"Distribution of {delay_col}",
            "x": delay_col, "data": df[delay_col].dropna().tolist()[:500],
        })
    elif status_col:
        bad_statuses = [s for s in df[status_col].dropna().unique()
                         if any(k in str(s).lower() for k in ["delay", "late", "fail", "cancel", "disrupt"])]
        disrupted = df[df[status_col].isin(bad_statuses)]
        insights.append(
            f"{len(disrupted)} of {len(df)} records have a disrupted status "
            f"({', '.join(bad_statuses) if bad_statuses else 'none found'})."
        )
        charts.append({
            "type": "bar", "title": f"Record count by {status_col}",
            "x": status_col, "data": df[status_col].value_counts().to_dict(),
        })
    else:
        # Anomaly-detection fallback for datasets with no delay/status column
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            from sklearn.ensemble import IsolationForest
            sub = df[numeric_cols].dropna()
            if len(sub) >= 10:
                clf = IsolationForest(contamination=0.1, random_state=42)
                preds = clf.fit_predict(sub)
                disrupted = df.loc[sub.index[preds == -1]]
                insights.append(
                    f"No explicit delay/status column found — used anomaly detection on "
                    f"{', '.join(numeric_cols)} instead. Flagged {len(disrupted)} outlier record(s)."
                )
                charts.append({
                    "type": "scatter", "title": "Anomaly detection (numeric columns)",
                    "x": numeric_cols[0], "y": numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0],
                    "data": sub.assign(anomaly=(preds == -1)).to_dict(orient="records")[:300],
                })
            else:
                insights.append("Not enough numeric data to run anomaly detection (need at least 10 rows).")
        else:
            insights.append("No delay, status, or numeric columns found to assess disruption.")

    if len(disrupted) > 0 and len(df) > 0 and len(disrupted) / len(df) > 0.2:
        risk_alerts.append(
            f"Over 20% of records ({len(disrupted)}/{len(df)}) show signs of disruption — "
            f"this warrants immediate review."
        )

    return {
        "insights": insights, "charts": charts, "recommendations": [],
        "risk_alerts": risk_alerts, "disrupted_indices": disrupted.index.tolist(),
    }
