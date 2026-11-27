"""
AI Orchestrator (Agent Manager).
1. Understand user request (LLM, or rule-based fallback) — see llm_service.select_agents
2. Plan & select required agent(s)
3. Run them against pre-computed DataFrame summaries (never raw rows to the LLM)
4. Merge outputs and produce a final natural-language summary
"""
import pandas as pd
from typing import Dict, Any, List

from app.services.llm_service import select_agents, summarize_with_llm
from app.agents import (
    disruption_agent, root_cause_agent, forecast_agent,
    inventory_agent, risk_agent, recommendation_agent,
)


def run_query(df: pd.DataFrame, roles: Dict[str, str], query: str) -> Dict[str, Any]:
    selected: List[str] = select_agents(query, roles)

    outputs: Dict[str, Dict[str, Any]] = {}

    # Disruption runs first if selected (or if root_cause/risk need its output)
    needs_disruption_context = any(a in selected for a in ("root_cause", "risk")) or "disruption" in selected
    disrupted_indices = []
    if needs_disruption_context:
        result = disruption_agent.run(df, roles, query)
        disrupted_indices = result.get("disrupted_indices", [])
        if "disruption" in selected:
            outputs["disruption"] = result

    if "root_cause" in selected:
        outputs["root_cause"] = root_cause_agent.run(df, roles, query, disrupted_indices=disrupted_indices)

    if "forecast" in selected:
        outputs["forecast"] = forecast_agent.run(df, roles, query)

    if "inventory" in selected:
        outputs["inventory"] = inventory_agent.run(df, roles, query)

    if "risk" in selected:
        outputs["risk"] = risk_agent.run(df, roles, query, disrupted_indices=disrupted_indices)

    # Recommendation agent always runs last, synthesizing everything above
    outputs["recommendation"] = recommendation_agent.run(outputs, query)
    if "recommendation" not in selected:
        selected.append("recommendation")

    # Merge
    insights = summarize_with_llm(query, outputs)
    charts = [c for o in outputs.values() for c in o.get("charts", [])]
    recommendations = [r for o in outputs.values() for r in o.get("recommendations", [])]
    risk_alerts = [r for o in outputs.values() for r in o.get("risk_alerts", [])]

    return {
        "agents_used": selected,
        "insights": insights,
        "charts": charts,
        "recommendations": list(dict.fromkeys(recommendations)),
        "risk_alerts": list(dict.fromkeys(risk_alerts)),
        "raw_agent_outputs": outputs,
    }
