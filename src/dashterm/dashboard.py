"""Assemble the configured panels into the framed dashboard and print it."""

from .config import DEFAULT_PANELS
from .theme import apply_theme
from .render.box import box_top, box_bottom, box_divider, _term_width
from .render.width import _strip_ansi
from .panels import PANELS

def render(cfg: dict):
    apply_theme(cfg.get("theme", "default"))
    width = min(_term_width(), 72)

    # Build each configured panel; keep only the non-empty ones.
    blocks = []
    for name in (cfg.get("panels") or DEFAULT_PANELS):
        build = PANELS.get(name)
        if build:
            rows = build(cfg, width)
            if rows:
                blocks.append(rows)

    # Frame them, inserting a divider between adjacent panels.
    lines = [box_top(width)]
    for i, block in enumerate(blocks):
        lines.extend(block)
        if i < len(blocks) - 1:
            lines.append(box_divider(width))
    lines.append(box_bottom(width))

    output = "\n".join(lines)
    if not cfg.get("use_color", True):
        output = _strip_ansi(output)
    print(output)
