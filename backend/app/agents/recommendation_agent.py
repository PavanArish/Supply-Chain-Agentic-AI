from typing import Dict, Any, List


def run(agent_outputs: Dict[str, Dict[str, Any]], query: str) -> Dict[str, Any]:
    recommendations: List[str] = []

    # Carry forward any recommendations agents already produced
    for name, output in agent_outputs.items():
        recommendations.extend(output.get("recommendations", []))

    risk_score = agent_outputs.get("risk", {}).get("risk_score")
    disrupted = agent_outputs.get("disruption", {}).get("disrupted_indices", [])

    if risk_score is not None and risk_score >= 60:
        recommendations.append(
            "Set up automated alerts for this dataset's key risk drivers so issues surface before they escalate."
        )
    if disrupted:
        recommendations.append(
            "Review the flagged disrupted records individually to confirm root causes before taking corrective action."
        )
    if not recommendations:
        recommendations.append(
            "No urgent action items identified from this query — the underlying data looks stable."
        )

    # De-duplicate while preserving order
    seen = set()
    unique = []
    for r in recommendations:
        if r not in seen:
            seen.add(r)
            unique.append(r)

    return {"insights": [], "charts": [], "recommendations": unique, "risk_alerts": []}
