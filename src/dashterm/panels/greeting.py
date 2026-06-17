"""Greeting panel — a time-of-day greeting addressed to the user."""

from ..theme import C, BOLD, RESET
from ..render.box import box_row
from ..collectors import get_hour, get_username

def _greeting(hour: int) -> tuple:
    """(text, icon) for the time of day. Icons are East-Asian-Wide emoji."""
    if 5 <= hour <= 11:
        return "Good morning", "🌅"
    if 12 <= hour <= 17:
        return "Good afternoon", "🌞"
    if 18 <= hour <= 21:
        return "Good evening", "🌆"
    return "Good night", "🌙"

def build(cfg: dict, width: int) -> list:
    text, icon = _greeting(get_hour())
    line = f"{icon}  {C.ACCENT}{BOLD}{text}{RESET}{C.LABEL}, {get_username()}{RESET}"
    return [box_row(line, width)]
