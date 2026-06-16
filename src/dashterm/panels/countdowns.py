"""Countdowns panel — progress bars and days remaining."""

from ..theme import C, BOLD, RESET, fg
from ..render.box import box_row_two
from ..render.width import _disp_width, _pad_left
from ..collectors import get_countdowns

def countdown_bar(days: int, max_days: int = 365, width: int = 10) -> str:
    if days <= 0:
        filled = width
    else:
        filled = max(0, width - int((days / max_days) * width))
    bar = "█" * filled + "░" * (width - filled)
    if days <= 7:
        colour = fg(220, 80, 80)    # red — imminent
    elif days <= 30:
        colour = C.WARN             # amber — soon
    else:
        colour = C.CDOWN            # lavender — distant
    return f"{colour}{bar}{RESET}"

def days_label(days: int) -> str:
    if days < 0:
        return f"{C.DIM}{abs(days)}d ago{RESET}"
    if days == 0:
        return f"{fg(255, 100, 100)}{BOLD}TODAY!{RESET}"
    if days == 1:
        return f"{C.WARN}{BOLD}tomorrow{RESET}"
    return f"{C.VALUE}{days}{RESET}{C.LABEL} days{RESET}"

def build(cfg: dict, width: int) -> list:
    countdowns = get_countdowns(cfg.get("countdowns", []))
    if not countdowns:
        return []
    # Right-align the labels to a common width so the bars line up regardless
    # of how many digits each has.
    data   = [(label, countdown_bar(days, width=12), days_label(days))
              for label, days in countdowns]
    dlbl_w = max(_disp_width(dlbl) for _, _, dlbl in data)
    out = []
    for label, bar, dlbl in data:
        left  = f"{C.CDOWN}⏳{RESET}  {C.VALUE}{label}{RESET}"
        right = f"{bar}  {_pad_left(dlbl, dlbl_w)}"
        out.append(box_row_two(left, right, width))
    return out
