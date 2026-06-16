"""Weather panel — current conditions for the configured city."""

from ..theme import C, BOLD, RESET
from ..render.box import box_row
from ..collectors import get_weather_short

def weather_icon(condition: str) -> str:
    # Use plain emoji only — no U+FE0F variation selectors, which some
    # terminals (e.g. VS Code's) render at an inconsistent width and break
    # the box alignment.
    c = condition.lower()
    if "sun"   in c or "clear" in c:  return "🌞"
    if "cloud" in c and "part" in c:  return "⛅"
    if "cloud" in c or "overcast" in c: return "🌥"
    if "rain"  in c or "drizzle" in c: return "🌧"
    if "storm" in c or "thunder" in c: return "🌩"
    if "snow"  in c:                  return "🌨"
    if "fog"   in c or "mist"  in c:  return "🌫"
    return "🌡"

def build(cfg: dict, width: int) -> list:
    if not (cfg.get("show_weather") and cfg.get("city")):
        return []
    city_name = cfg["city"]
    condition, temp = get_weather_short(city_name, cfg.get("weather_cache_minutes", 30))

    if condition and condition != "unavailable":
        icon = weather_icon(condition)
        line = (f"{icon}  {C.WEATHER}{BOLD}{city_name}{RESET}  "
                f"{C.VALUE}{temp}{RESET}  "
                f"{C.LABEL}{condition}{RESET}")
    elif condition == "unavailable":
        line = f"🌡  {C.LABEL}{city_name}  (weather unavailable){RESET}"
    else:
        line = f"🌡  {C.LABEL}fetching weather…{RESET}"
    return [box_row(line, width)]
