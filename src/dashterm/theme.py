"""ANSI colour helpers, named themes, and the active palette.

The active palette is the single shared object ``C``; ``apply_theme`` mutates it
in place so every module that did ``from .theme import C`` sees colour changes.
"""

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"

def fg(r, g, b):    return f"\033[38;2;{r};{g};{b}m"
def bg(r, g, b):    return f"\033[48;2;{r};{g};{b}m"

# Each theme maps semantic roles to (r, g, b) tuples.
THEMES = {
    "default": {
        "BORDER": (80, 120, 180), "LABEL": (120, 120, 140), "VALUE": (220, 220, 235),
        "ACCENT": (100, 200, 160), "WARN": (220, 180, 80), "DIM": (80, 80, 95),
        "CLOCK": (255, 220, 100), "DATE": (180, 210, 255), "WEATHER": (130, 195, 240),
        "CDOWN": (200, 150, 255), "USER": (100, 220, 150),
    },
    "mono": {
        "BORDER": (130, 130, 130), "LABEL": (110, 110, 110), "VALUE": (235, 235, 235),
        "ACCENT": (200, 200, 200), "WARN": (180, 180, 180), "DIM": (80, 80, 80),
        "CLOCK": (255, 255, 255), "DATE": (200, 200, 200), "WEATHER": (170, 170, 170),
        "CDOWN": (190, 190, 190), "USER": (210, 210, 210),
    },
    "nord": {
        "BORDER": (136, 192, 208), "LABEL": (118, 128, 150), "VALUE": (236, 239, 244),
        "ACCENT": (163, 190, 140), "WARN": (235, 203, 139), "DIM": (76, 86, 106),
        "CLOCK": (235, 203, 139), "DATE": (129, 161, 193), "WEATHER": (136, 192, 208),
        "CDOWN": (180, 142, 173), "USER": (163, 190, 140),
    },
    "solarized": {
        "BORDER": (38, 139, 210), "LABEL": (88, 110, 117), "VALUE": (147, 161, 161),
        "ACCENT": (42, 161, 152), "WARN": (181, 137, 0), "DIM": (88, 110, 117),
        "CLOCK": (181, 137, 0), "DATE": (38, 139, 210), "WEATHER": (42, 161, 152),
        "CDOWN": (108, 113, 196), "USER": (133, 153, 0),
    },
}

_ROLES = tuple(THEMES["default"].keys())

class Palette:
    """Holds the active foreground colour for each semantic role."""
    __slots__ = _ROLES

    def __init__(self):
        for role in _ROLES:
            setattr(self, role, "")

# Shared, mutated in place by apply_theme so importers stay in sync.
C = Palette()

def apply_theme(name: str):
    """Set the active palette ``C`` from a named theme (falls back to default)."""
    pal = THEMES.get(name, THEMES["default"])
    for role, rgb in pal.items():
        setattr(C, role, fg(*rgb))

apply_theme("default")
