"""
News / Events API stub. If NEWS_API_KEY is configured, this is the single
place to add a real call (e.g. NewsAPI.org, GDELT). Until then, it returns
a clearly-labeled placeholder so the rest of the pipeline (Risk Agent) has
a stable shape to consume.
"""
from app.core.config import settings


def get_relevant_events(keywords: list) -> list:
    if not settings.news_api_key:
        return [
            {
                "headline": "News/Events API not configured",
                "source": "stub",
                "note": "Set NEWS_API_KEY in .env to enable live disruption-news lookups "
                        "(port strikes, weather events, geopolitical disruptions, etc.).",
            }
        ]
    # Real implementation would call the configured news provider here, e.g.:
    # resp = requests.get("https://newsapi.org/v2/everything",
    #                      params={"q": " OR ".join(keywords), "apiKey": settings.news_api_key})
    # return resp.json().get("articles", [])
    return []
