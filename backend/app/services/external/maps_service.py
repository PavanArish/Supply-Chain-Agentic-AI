"""
Maps / Route API stub. If MAPS_API_KEY is configured, this is the single
place to add a real call (e.g. Google Maps Directions/Distance Matrix,
Mapbox). Until then, it returns a placeholder shape.
"""
from app.core.config import settings


def get_route_info(origin: str, destination: str) -> dict:
    if not settings.maps_api_key:
        return {
            "origin": origin,
            "destination": destination,
            "status": "Maps/Route API not configured",
            "note": "Set MAPS_API_KEY in .env to enable live route/ETA lookups.",
        }
    # Real implementation would call the configured maps provider here.
    return {"origin": origin, "destination": destination, "status": "ok"}
