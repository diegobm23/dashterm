"""Config file location, defaults, and load/save helpers."""

import copy
import json
import pathlib

CONFIG_DIR  = pathlib.Path.home() / ".config" / "dashterm"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Panels shown (top-to-bottom) when the config doesn't specify an order.
DEFAULT_PANELS = ["clock", "weather", "countdowns", "system", "user"]

DEFAULT_CONFIG = {
    "city": "",
    "countdowns": [],
    "use_color": True,
    "show_weather": True,
    "weather_cache_minutes": 30,
    "clock_style": "default",   # "default" | "large" | "ascii"
    "theme": "default",          # see dashterm.theme.THEMES
    "panels": list(DEFAULT_PANELS),
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            # back-fill any missing keys from defaults (deep-copied so we never
            # alias the mutable lists/dicts inside DEFAULT_CONFIG)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, copy.deepcopy(v))
            return cfg
        except Exception:
            pass
    return copy.deepcopy(DEFAULT_CONFIG)

def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
