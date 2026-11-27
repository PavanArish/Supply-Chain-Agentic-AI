"""
Query-understanding logic for the AI Orchestrator: decides which
specialized agents a user's query needs, and turns agent output into
natural-language insight bullets.

Supports three optional LLM providers, tried in this order:
  1. Google Gemini (GEMINI_API_KEY) - free tier, gemini-1.5-flash
  2. Groq (GROQ_API_KEY) - groq.com's fast-inference API (Llama/Mixtral),
     via its OpenAI-compatible endpoint at https://api.groq.com/openai/v1.
     NOT the same company/service as "Grok" below - easy to mix up.
  3. Grok / xAI (GROK_API_KEY) - via xAI's OpenAI-compatible endpoint,
     using the `openai` SDK pointed at https://api.x.ai/v1 (this is NOT
     the OpenAI API — just the same client library talking to xAI).

If none are configured, or a call fails for any reason, everything
falls back to deterministic rule-based/heuristic logic, so the app always
works end-to-end with zero API keys.

IMPORTANT design decision: raw spreadsheet rows are NEVER sent to the LLM.
Only small, pre-computed JSON summaries (counts, aggregates, top-N lists)
are passed in.
"""
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

AGENT_NAMES = [
    "disruption", "root_cause", "forecast", "inventory", "risk", "recommendation",
]

_KEYWORD_TO_AGENT = {
    "disruption": ["delay", "delayed", "disrupt", "late", "problem", "issue"],
    "root_cause": ["why", "cause", "caus", "reason", "root"],
    "forecast": ["forecast", "predict", "trend", "future", "next month", "next week", "upcoming"],
    "inventory": ["inventory", "stock", "reorder", "shortage", "overstock", "out of stock"],
    "risk": ["risk", "alert", "danger", "exposure", "vulnerab"],
    "recommendation": ["recommend", "should", "advice", "suggest", "action", "what to do"],
}

# --- Provider setup (lazy, best-effort) -------------------------------

_gemini_model = None
if settings.gemini_api_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        _gemini_model = genai.GenerativeModel(settings.gemini_model)
    except Exception:
        _gemini_model = None

_grok_client = None
if settings.grok_api_key:
    try:
        from openai import OpenAI
        _grok_client = OpenAI(api_key=settings.grok_api_key, base_url=settings.grok_base_url)
    except Exception:
        _grok_client = None

_groq_client = None
if settings.groq_api_key:
    try:
        from openai import OpenAI
        _groq_client = OpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url)
    except Exception:
        _groq_client = None

ACTIVE_PROVIDER = (
    "gemini" if _gemini_model else
    "groq" if _groq_client else
    "grok" if _grok_client else
    "none"
)


def _call_llm(prompt: str) -> Optional[str]:
    """Send prompt to whichever provider is configured
    (Gemini first, then Groq, then Grok). Returns None if no provider is
    available or all configured calls fail."""
    if _gemini_model:
        try:
            resp = _gemini_model.generate_content(prompt)
            return resp.text or None
        except Exception:
            pass  # try the next configured provider, else fall through

    if _groq_client:
        try:
            resp = _groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content or None
        except Exception:
            pass

    if _grok_client:
        try:
            resp = _grok_client.chat.completions.create(
                model=settings.grok_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content or None
        except Exception:
            pass

    return None


# --- Rule-based fallback -----------------------------------------------

def _rule_based_agents(user_query: str) -> List[str]:
    q = user_query.lower()
    matched = [agent for agent, kws in _KEYWORD_TO_AGENT.items() if any(kw in q for kw in kws)]
    if not matched:
        matched = ["disruption", "root_cause"]
    if "recommendation" not in matched:
        matched.append("recommendation")
    return matched


# --- Public API ----------------------------------------------------------

def select_agents(user_query: str, column_roles: Dict[str, str] = None) -> List[str]:
    """Plan & select required agent(s) — the AI Orchestrator's core job."""
    prompt = (
        "You are the orchestrator of a supply-chain analytics system. "
        "Given a user's natural-language query and the available data columns "
        "(never raw rows), decide which of these specialized agents should run: "
        f"{', '.join(AGENT_NAMES)}. Usually 1-3 agents are enough. Always include "
        "'recommendation' if the user seems to want action guidance.\n\n"
        f"Query: {user_query}\n"
        f"Available column roles: {json.dumps(column_roles or {})}\n\n"
        "Respond with ONLY a JSON array of agent name strings from the list above, "
        'e.g. ["disruption", "root_cause", "recommendation"]. No other text.'
    )
    text = _call_llm(prompt)
    if text:
        try:
            cleaned = text.strip().strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
            agents = json.loads(cleaned)
            agents = [a for a in agents if a in AGENT_NAMES]
            if agents:
                if "recommendation" not in agents:
                    agents.append("recommendation")
                return agents
        except Exception:
            pass  # fall through to rule-based fallback

    return _rule_based_agents(user_query)


def summarize_with_llm(user_query: str, agent_outputs: Dict[str, Any]) -> List[str]:
    """Turn agent JSON outputs into natural-language insight bullets."""
    prompt = (
        "You are a supply-chain analyst. Given structured JSON output from "
        "specialized agents, write 3-6 short, concrete insight bullets answering "
        "the user's query. No preamble, just the bullets, one per line, no bullet "
        "characters.\n\n"
        f"User query: {user_query}\n"
        f"Agent outputs (JSON): {json.dumps(agent_outputs, default=str)}"
    )
    text = _call_llm(prompt)
    if text:
        lines = [l.strip("-• ").strip() for l in text.splitlines() if l.strip()]
        if lines:
            return lines

    # Rule-based fallback: flatten each agent's own "insights" list
    insights = []
    for agent_name, output in agent_outputs.items():
        for item in output.get("insights", []):
            insights.append(f"[{agent_name}] {item}")
    return insights or ["No notable insights could be generated from this dataset for this query."]
