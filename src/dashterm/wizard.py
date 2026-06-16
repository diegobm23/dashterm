"""Interactive setup wizard and the --config viewer."""

import datetime

from .config import CONFIG_FILE, DEFAULT_PANELS, load_config, save_config
from .theme import C, BOLD, RESET, THEMES
from .dashboard import render

def setup():
    cfg = load_config()
    print(f"\n{BOLD}{C.ACCENT}dashterm setup wizard{RESET}\n")

    # City
    current_city = cfg.get("city", "")
    prompt_city  = f"  City for weather [{current_city or 'none'}]: "
    city = input(prompt_city).strip()
    if city:
        cfg["city"] = city
    elif not current_city:
        cfg["show_weather"] = False

    # Weather cache period
    current_period = cfg.get("weather_cache_minutes", 30)
    period_in = input(
        f"  Weather refresh period in minutes [{current_period}]: "
    ).strip()
    if period_in:
        try:
            period = float(period_in)
            if period > 0:
                cfg["weather_cache_minutes"] = period
            else:
                print("  ⚠️  Must be greater than 0 — keeping current value.")
        except ValueError:
            print("  ⚠️  Not a number — keeping current value.")

    # Clock style
    styles = {"1": "default", "2": "large", "3": "ascii"}
    current_style = cfg.get("clock_style", "default")
    print(f"\n  {C.LABEL}Clock style:{RESET} [1] default  [2] large (block)  [3] ascii (digital)")
    style_in = input(f"  Choose [{current_style}]: ").strip()
    if style_in in styles:
        cfg["clock_style"] = styles[style_in]
    elif style_in in styles.values():
        cfg["clock_style"] = style_in
    elif style_in:
        print("  ⚠️  Unknown choice — keeping current value.")

    # Theme
    theme_names  = sorted(THEMES)
    current_theme = cfg.get("theme", "default")
    print(f"\n  {C.LABEL}Theme:{RESET} {', '.join(theme_names)}")
    theme_in = input(f"  Choose [{current_theme}]: ").strip().lower()
    if theme_in in THEMES:
        cfg["theme"] = theme_in
    elif theme_in:
        print("  ⚠️  Unknown theme — keeping current value.")

    # System stats panel toggle
    panels = list(cfg.get("panels") or DEFAULT_PANELS)
    has_system = "system" in panels
    sys_in = input(
        f"  Show system stats panel (load/disk/battery)? [{'Y/n' if has_system else 'y/N'}]: "
    ).strip().lower()
    want_system = has_system if not sys_in else sys_in == "y"
    if want_system and not has_system:
        # Insert before the user panel if present, else append.
        idx = panels.index("user") if "user" in panels else len(panels)
        panels.insert(idx, "system")
    elif not want_system and has_system:
        panels = [p for p in panels if p != "system"]
    cfg["panels"] = panels

    # Countdowns — snapshot the existing list as a copy so appends below don't
    # mutate it (and don't alias DEFAULT_CONFIG's list).
    existing = list(cfg.get("countdowns", []))
    cfg["countdowns"] = list(existing)
    print(f"\n  {C.LABEL}Current countdowns:{RESET}")
    if existing:
        for i, c in enumerate(existing, 1):
            print(f"    {i}. {c['label']} → {c['date']}")
    else:
        print(f"    {C.DIM}(none){RESET}")

    print(f"\n  {C.LABEL}Add up to {5 - len(existing)} more countdown(s). Leave label blank to stop.{RESET}\n")

    while len(cfg["countdowns"]) < 5:
        label = input("  Countdown label (or Enter to skip): ").strip()
        if not label:
            break
        while True:
            date_str = input(f"  Date for '{label}' (YYYY-MM-DD): ").strip()
            try:
                datetime.date.fromisoformat(date_str)
                break
            except ValueError:
                print("  ⚠️  Invalid date format, try again.")
        cfg["countdowns"].append({"label": label, "date": date_str})
        print(f"  {C.ACCENT}✓ Added{RESET}\n")

    added = len(cfg["countdowns"]) - len(existing)

    # If there were already countdowns AND new ones were added, ask whether to
    # keep the old ones alongside the new ones.
    if existing and added:
        ans = input("  Keep the previous countdowns too? [Y/n]: ").strip().lower()
        if ans == "n":
            cfg["countdowns"] = cfg["countdowns"][len(existing):]  # keep only the new ones
    # If there were countdowns but none were added, offer to clear them all.
    elif existing and not added:
        ans = input("  Clear all existing countdowns? [y/N]: ").strip().lower()
        if ans == "y":
            cfg["countdowns"] = []

    save_config(cfg)
    print(f"\n  {C.ACCENT}✓ Config saved to {CONFIG_FILE}{RESET}")
    print(f"  {C.LABEL}Run {C.VALUE}dashterm{RESET} {C.LABEL}to see your dashboard.{RESET}\n")

    # Preview
    ans = input("  Preview dashboard now? [Y/n]: ").strip().lower()
    if ans != "n":
        print()
        render(cfg)

def show_config():
    """Print the config file path and its contents."""
    print(f"\n  {C.LABEL}Config file:{RESET} {C.VALUE}{CONFIG_FILE}{RESET}\n")
    if not CONFIG_FILE.exists():
        print(f"  {C.DIM}(not created yet — run {C.VALUE}dashterm --setup{RESET}{C.DIM}){RESET}\n")
        return
    try:
        with open(CONFIG_FILE) as f:
            print(f.read().rstrip())
    except Exception as e:
        print(f"  {C.WARN}⚠️  Could not read config: {e}{RESET}")
    print()
