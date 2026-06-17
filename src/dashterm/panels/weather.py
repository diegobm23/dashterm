"""Weather panel — current conditions for the configured city."""

from ..theme import C, BOLD, RESET
from ..render.box import box_row
from ..collectors import get_weather_short

def weather_icon(condition: str) -> str:
    # Use only East-Asian-"Wide" emoji (and no U+FE0F variation selectors).
    # Every terminal renders Wide emoji as two columns, so the box stays
    # aligned; Narrow emoji like 🌫/🌧 render as one column in some terminals
    # (e.g. VS Code's) and break the right border.
    c = condition.lower()
    if "sun"   in c or "clear" in c:    return "🌞"
    if "rain"  in c or "drizzle" in c:  return "☔"
    if "storm" in c or "thunder" in c:  return "⚡"
    if "snow"  in c or "blizzard" in c or "sleet" in c:  return "⛄"
    if "fog"   in c or "mist"  in c:    return "🌁"
    if "cloud" in c or "overcast" in c: return "⛅"
    return "⛅"

def build(cfg: dict, width: int) -> list:
    if not (cfg.get("show_weather") and cfg.get("city")):
        return []
    city_name = cfg["city"]
    condition, temp = get_weather_short(
        city_name, cfg.get("weather_cache_minutes", 30), cfg.get("temp_unit", "C")
    )

    if condition and condition != "unavailable":
        icon = weather_icon(condition)
        line = (f"{icon}  {C.WEATHER}{BOLD}{city_name}{RESET}  "
                f"{C.VALUE}{temp}{RESET}  "
                f"{C.LABEL}{condition}{RESET}")
    elif condition == "unavailable":
        line = f"⛅  {C.LABEL}{city_name}  (weather unavailable){RESET}"
    else:
        line = f"⏳  {C.LABEL}fetching weather…{RESET}"
    return [box_row(line, width)]
