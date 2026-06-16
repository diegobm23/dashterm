"""On-disk cache for fetched weather, keyed by city with a freshness window."""

import json
import time

from .config import CONFIG_DIR

CACHE_FILE = CONFIG_DIR / "weather_cache.json"

def load_weather_cache(city: str, max_age_minutes: float):
    """Return cached (condition, temp) if fresh and for the same city, else None."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    except Exception:
        return None
    if cache.get("city") != city:
        return None
    age = time.time() - cache.get("fetched_at", 0)
    if age > max_age_minutes * 60:
        return None
    return cache.get("condition", ""), cache.get("temp", "")

def save_weather_cache(city: str, condition: str, temp: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "city": city,
        "condition": condition,
        "temp": temp,
        "fetched_at": time.time(),
    }
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass
