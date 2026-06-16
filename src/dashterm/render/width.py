"""Visible display-width math that accounts for ANSI codes and wide emoji."""

import re
import unicodedata

_ANSI_RE = re.compile(r"\033\[[^m]*m")

def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)

# Code points that render two columns wide but that `east_asian_width` reports
# as Narrow/Ambiguous — emoji whose *default* presentation is text yet which
# modern terminals still draw as full 2-col emoji.
_WIDE_RANGES = (
    (0x1100,  0x115F),    # Hangul Jamo
    (0x1F000, 0x1FAFF),   # Emoji & pictographs  (👤 🕐 🌧 🌫 🌡 …)
)
_WIDE_CHARS = {
    0x26C8,   # ⛈ thunder cloud (Ambiguous in EAW, but emoji-presented)
}

def _char_width(ch: str) -> int:
    o = ord(ch)
    # Zero-width: combining marks, ZWJ, and variation selectors (e.g. U+FE0F,
    # handled as a look-ahead promoter in _disp_width).
    if unicodedata.combining(ch) or ch == "‍" or 0xFE00 <= o <= 0xFE0F:
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    if o in _WIDE_CHARS or any(lo <= o <= hi for lo, hi in _WIDE_RANGES):
        return 2
    return 1

def _disp_width(s: str) -> int:
    """Visible display width of a string, accounting for wide/zero-width chars."""
    s = _strip_ansi(s)
    total = 0
    for i, ch in enumerate(s):
        w = _char_width(ch)
        # A trailing emoji variation selector (U+FE0F) promotes the preceding
        # text-presentation symbol to a 2-column emoji (e.g. ☀️ ☁️ ❄️ ⚠️).
        if w == 1 and i + 1 < len(s) and s[i + 1] == "️":
            w = 2
        total += w
    return total

def _pad_left(s: str, target: int) -> str:
    """Prepend spaces so the visible width of `s` is at least `target`."""
    return " " * max(0, target - _disp_width(s)) + s
