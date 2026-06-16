"""Box-drawing helpers that keep every row a uniform display width."""

import shutil

from ..theme import C, RESET
from .width import _disp_width

TL = "╭"; TR = "╮"; BL = "╰"; BR = "╯"
H  = "─"; V  = "│"; ML = "├"; MR = "┤"

def _term_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns

def box_top(width):
    return f"{C.BORDER}{TL}{H * (width - 2)}{TR}{RESET}"

def box_bottom(width):
    return f"{C.BORDER}{BL}{H * (width - 2)}{BR}{RESET}"

def box_divider(width):
    return f"{C.BORDER}{ML}{H * (width - 2)}{MR}{RESET}"

def box_row(content: str, width: int, pad: int = 2) -> str:
    """Wrap content in a box row, stripping ANSI for length calculation."""
    space = width - 2 - (pad * 2) - _disp_width(content)
    if space < 0:
        space = 0
    return (
        f"{C.BORDER}{V}{RESET}"
        f"{' ' * pad}{content}{' ' * (space + pad)}"
        f"{C.BORDER}{V}{RESET}"
    )

def box_row_two(left: str, right: str, width: int, pad: int = 2) -> str:
    """Two-column row inside a box."""
    inner = width - 2 - pad * 2
    gap   = inner - _disp_width(left) - _disp_width(right)
    if gap < 1:
        gap = 1
    return (
        f"{C.BORDER}{V}{RESET}"
        f"{' ' * pad}{left}{' ' * gap}{right}{' ' * pad}"
        f"{C.BORDER}{V}{RESET}"
    )

def box_row_center(content: str, width: int) -> str:
    """Center content horizontally inside a box row."""
    inner = width - 2
    extra = inner - _disp_width(content)
    if extra < 0:
        extra = 0
    left  = extra // 2
    right = extra - left
    return (
        f"{C.BORDER}{V}{RESET}"
        f"{' ' * left}{content}{' ' * right}"
        f"{C.BORDER}{V}{RESET}"
    )
