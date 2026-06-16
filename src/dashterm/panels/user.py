"""User panel — user@host and system uptime."""

from ..theme import C, BOLD, RESET
from ..render.box import box_row_two
from ..collectors import get_user_host, get_uptime

def build(cfg: dict, width: int) -> list:
    user_part   = f"👤  {C.USER}{BOLD}{get_user_host()}{RESET}"
    uptime_part = f"{C.LABEL}⏱  {RESET}{C.ACCENT}{get_uptime()}{RESET}"
    return [box_row_two(user_part, uptime_part, width)]
