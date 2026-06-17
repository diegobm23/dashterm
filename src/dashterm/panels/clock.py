"""Clock panel — compact header time, or a big multi-line clock."""

from ..theme import C, BOLD, RESET
from ..render.box import box_row_two, box_row_center, box_divider
from ..render.clock import big_clock
from ..collectors import get_clock, get_date, get_meridiem

def build(cfg: dict, width: int) -> list:
    style = cfg.get("clock_style", "default")
    fmt   = cfg.get("time_format", "24h")
    clock = get_clock(fmt)
    date_str = get_date()
    meridiem = get_meridiem() if fmt == "12h" else ""

    if style in ("large", "ascii"):
        # Centered date, then a big multi-line clock spanning its own rows.
        rows = [box_row_center(f"{C.DATE}{BOLD}{date_str}{RESET}", width),
                box_divider(width)]
        for cline in big_clock(clock, style):
            rows.append(box_row_center(f"{C.CLOCK}{BOLD}{cline}{RESET}", width))
        # The big-clock font has no letters, so show AM/PM as a centered label.
        if meridiem:
            rows.append(box_row_center(f"{C.LABEL}{meridiem}{RESET}", width))
        return rows

    suffix     = f" {meridiem}" if meridiem else ""
    date_part  = f"{C.DATE}{BOLD}{date_str}{RESET}"
    clock_part = f"{C.CLOCK}{BOLD}{clock}{suffix}{RESET}  {C.LABEL}🕐{RESET}"
    return [box_row_two(date_part, clock_part, width)]
