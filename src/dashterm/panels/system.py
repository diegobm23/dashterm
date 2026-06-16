"""System panel — load average, free disk, and battery."""

from ..theme import C, RESET
from ..render.box import box_row, box_row_two
from ..collectors import get_loadavg, get_disk, get_battery

def build(cfg: dict, width: int) -> list:
    load, disk, batt = get_loadavg(), get_disk(), get_battery()
    left_bits, right_bits = [], []
    if load:
        left_bits.append(f"📈  {C.VALUE}{load}{RESET}")
    if disk:
        right_bits.append(f"💾  {C.VALUE}{disk}{RESET}")
    if batt:
        right_bits.append(f"🔋  {C.VALUE}{batt}{RESET}")
    left, right = "   ".join(left_bits), "   ".join(right_bits)
    if left and right:
        return [box_row_two(left, right, width)]
    if left or right:
        return [box_row(left or right, width)]
    return []
