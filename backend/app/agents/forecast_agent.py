import pandas as pd
import numpy as np
from typing import Dict, Any


def _find_col(roles: Dict[str, str], role: str):
    for col, r in roles.items():
        if r == role:
            return col
    return None


def run(df: pd.DataFrame, roles: Dict[str, str], query: str) -> Dict[str, Any]:
    insights, charts, risk_alerts = [], [], []

    date_col = _find_col(roles, "date")
    target_col = (
        _find_col(roles, "delay") or _find_col(roles, "quantity")
        or _find_col(roles, "cost") or None
    )
    if target_col is None:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        target_col = numeric_cols[0] if numeric_cols else None

    if not date_col or not target_col:
        insights.append("No date + numeric column pair found — cannot build a time-based forecast.")
        return {"insights": insights, "charts": charts, "recommendations": [], "risk_alerts": risk_alerts}

    sub = df[[date_col, target_col]].dropna()
    sub = sub.sort_values(date_col)
    if len(sub) < 5:
        insights.append(f"Not enough data points ({len(sub)}) to forecast '{target_col}' reliably.")
        return {"insights": insights, "charts": charts, "recommendations": [], "risk_alerts": risk_alerts}

    daily = sub.groupby(sub[date_col].dt.date)[target_col].mean().reset_index()
    daily.columns = ["date", "value"]
    daily["t"] = np.arange(len(daily))

    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(daily[["t"]], daily["value"])

    horizon = min(7, max(3, len(daily) // 4))
    future_t = pd.DataFrame({"t": np.arange(len(daily), len(daily) + horizon)})
    preds = model.predict(future_t)

    trend = "increasing" if model.coef_[0] > 0 else "decreasing" if model.coef_[0] < 0 else "flat"
    insights.append(
        f"'{target_col}' shows a {trend} trend over time (slope ≈ {model.coef_[0]:.3f} per period). "
        f"Projected next-{horizon}-period average: {preds.mean():.2f}."
    )

    charts.append({
        "type": "line", "title": f"{target_col} trend & {horizon}-period forecast",
        "x": "date",
        "data": {
            "actual": daily["value"].round(2).tolist(),
            "forecast": [round(p, 2) for p in preds.tolist()],
        },
    })

    if trend == "increasing" and target_col.lower().find("delay") != -1 if isinstance(target_col, str) else False:
        risk_alerts.append(f"'{target_col}' is trending upward — delays may worsen if unaddressed.")

    return {"insights": insights, "charts": charts, "recommendations": [], "risk_alerts": risk_alerts}
