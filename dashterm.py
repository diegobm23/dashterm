#!/usr/bin/env python3
"""
dashterm — Terminal dashboard for your shell startup.
Usage:
    dashterm            → static snapshot (for .bashrc / .zshrc)
    dashterm --live     → live updating clock (standalone mode)
    dashterm --setup    → interactive configuration wizard
    dashterm --help     → show usage
"""

import os
import sys
import json
import socket
import subprocess
import datetime
import time
import pathlib
import shutil
import urllib.request
import urllib.error

# ─── Config ──────────────────────────────────────────────────────────────────

CONFIG_DIR  = pathlib.Path.home() / ".config" / "dashterm"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "city": "",
    "countdowns": [],
    "use_color": True,
    "show_weather": True,
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            # back-fill any missing keys from defaults
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

# ─── ANSI colour helpers ──────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

def fg(r, g, b):     return f"\033[38;2;{r};{g};{b}m"
def bg(r, g, b):     return f"\033[48;2;{r};{g};{b}m"

# Palette
C_BORDER  = fg(80,  120, 180)   # soft blue
C_LABEL   = fg(120, 120, 140)   # muted grey
C_VALUE   = fg(220, 220, 235)   # near-white
C_ACCENT  = fg(100, 200, 160)   # mint green
C_WARN    = fg(220, 180,  80)   # amber
C_DIM     = fg(80,   80,  95)   # dark grey
C_CLOCK   = fg(255, 220, 100)   # warm yellow
C_DATE    = fg(180, 210, 255)   # light blue
C_WEATHER = fg(130, 195, 240)   # sky blue
C_CDOWN   = fg(200, 150, 255)   # lavender
C_USER    = fg(100, 220, 150)   # green

# ─── Box-drawing ──────────────────────────────────────────────────────────────

TL = "╭"; TR = "╮"; BL = "╰"; BR = "╯"
H  = "─"; V  = "│"; ML = "├"; MR = "┤"

def _term_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns

def box_top(width):
    return f"{C_BORDER}{TL}{H * (width - 2)}{TR}{RESET}"

def box_bottom(width):
    return f"{C_BORDER}{BL}{H * (width - 2)}{BR}{RESET}"

def box_divider(width):
    return f"{C_BORDER}{ML}{H * (width - 2)}{MR}{RESET}"

def box_row(content: str, width: int, pad: int = 2) -> str:
    """Wrap content in a box row, stripping ANSI for length calculation."""
    visible = _strip_ansi(content)
    space   = width - 2 - (pad * 2) - len(visible)
    if space < 0:
        space = 0
    return (
        f"{C_BORDER}{V}{RESET}"
        f"{' ' * pad}{content}{' ' * (space + pad)}"
        f"{C_BORDER}{V}{RESET}"
    )

def box_row_two(left: str, right: str, width: int, pad: int = 2) -> str:
    """Two-column row inside a box."""
    lv = _strip_ansi(left)
    rv = _strip_ansi(right)
    inner = width - 2 - pad * 2
    gap   = inner - len(lv) - len(rv)
    if gap < 1:
        gap = 1
    return (
        f"{C_BORDER}{V}{RESET}"
        f"{' ' * pad}{left}{' ' * gap}{right}{' ' * pad}"
        f"{C_BORDER}{V}{RESET}"
    )

def _strip_ansi(s: str) -> str:
    import re
    return re.sub(r"\033\[[^m]*m", "", s)

# ─── Data collectors ──────────────────────────────────────────────────────────

def get_clock() -> str:
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def get_date() -> str:
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")

def get_uptime() -> str:
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        days  = int(secs // 86400);  secs %= 86400
        hours = int(secs // 3600);   secs %= 3600
        mins  = int(secs // 60)
        parts = []
        if days:  parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        parts.append(f"{mins}m")
        return "up " + " ".join(parts)
    except Exception:
        pass
    # macOS / BSD fallback
    try:
        out = subprocess.check_output(["uptime"], text=True)
        # grab the "up X days, X:XX" portion
        import re
        m = re.search(r"up\s+(.+?),\s+\d+ user", out)
        if m:
            return "up " + m.group(1).strip()
        return out.split(",")[0].strip()
    except Exception:
        return "n/a"

def get_user_host() -> str:
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown"
    try:
        host = socket.gethostname().split(".")[0]
    except Exception:
        host = "localhost"
    return f"{user}@{host}"

def get_weather(city: str) -> str:
    """Fetch weather from wttr.in (no API key needed)."""
    if not city:
        return ""
    try:
        url     = f"http://wttr.in/{urllib.parse.quote(city)}?format=%C+%t+%h+humidity"
        req     = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = resp.read().decode().strip()
        # raw is like: "Partly cloudy +24°C 72% humidity"
        return raw
    except Exception:
        return "unavailable"

def get_weather_short(city: str) -> tuple[str, str]:
    """Returns (condition, temp_string) or ('', '') on failure."""
    if not city:
        return "", ""
    try:
        import urllib.parse
        url = f"http://wttr.in/{urllib.parse.quote(city)}?format=%C|%t"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = resp.read().decode().strip()
        parts = raw.split("|")
        condition = parts[0].strip() if parts else "?"
        temp      = parts[1].strip() if len(parts) > 1 else "?"
        return condition, temp
    except Exception:
        return "unavailable", ""

def get_countdowns(countdowns: list) -> list[tuple[str, int]]:
    """Returns list of (label, days_remaining)."""
    today = datetime.date.today()
    results = []
    for c in countdowns:
        try:
            target = datetime.date.fromisoformat(c["date"])
            delta  = (target - today).days
            results.append((c["label"], delta))
        except Exception:
            continue
    return results

# ─── Renderer ─────────────────────────────────────────────────────────────────

def countdown_bar(days: int, max_days: int = 365, width: int = 10) -> str:
    if days <= 0:
        filled = width
    else:
        filled = max(0, width - int((days / max_days) * width))
    bar = "█" * filled + "░" * (width - filled)
    if days <= 7:
        colour = fg(220, 80, 80)    # red — imminent
    elif days <= 30:
        colour = C_WARN             # amber — soon
    else:
        colour = C_CDOWN            # lavender — distant
    return f"{colour}{bar}{RESET}"

def days_label(days: int) -> str:
    if days < 0:
        return f"{C_DIM}{abs(days)}d ago{RESET}"
    if days == 0:
        return f"{fg(255,100,100)}{BOLD}TODAY!{RESET}"
    if days == 1:
        return f"{C_WARN}{BOLD}tomorrow{RESET}"
    return f"{C_VALUE}{days}{RESET}{C_LABEL} days{RESET}"

def weather_icon(condition: str) -> str:
    c = condition.lower()
    if "sun"   in c or "clear" in c:  return "☀️ "
    if "cloud" in c and "part" in c:  return "⛅ "
    if "cloud" in c or "overcast" in c: return "☁️ "
    if "rain"  in c or "drizzle" in c: return "🌧 "
    if "storm" in c or "thunder" in c: return "⛈ "
    if "snow"  in c:                  return "❄️ "
    if "fog"   in c or "mist"  in c:  return "🌫 "
    return "🌡 "

def render(cfg: dict):
    width = min(_term_width(), 72)

    # ── collect data ──
    clock     = get_clock()
    date_str  = get_date()
    user_host = get_user_host()
    uptime    = get_uptime()
    countdowns = get_countdowns(cfg.get("countdowns", []))

    weather_condition, weather_temp = "", ""
    if cfg.get("show_weather") and cfg.get("city"):
        weather_condition, weather_temp = get_weather_short(cfg["city"])

    # ── build output lines ──
    lines = []
    lines.append(box_top(width))

    # Row 1: Date  |  Clock
    date_part  = f"{C_DATE}{BOLD}{date_str}{RESET}"
    clock_part = f"{C_CLOCK}{BOLD}{clock}{RESET}  {C_LABEL}🕐{RESET}"
    lines.append(box_row_two(date_part, clock_part, width))

    lines.append(box_divider(width))

    # Row 2: Weather
    if cfg.get("show_weather") and cfg.get("city"):
        city_name = cfg["city"]
        if weather_condition and weather_condition != "unavailable":
            icon = weather_icon(weather_condition)
            weather_line = (
                f"{icon} {C_WEATHER}{BOLD}{city_name}{RESET}  "
                f"{C_VALUE}{weather_temp}{RESET}  "
                f"{C_LABEL}{weather_condition}{RESET}"
            )
        elif weather_condition == "unavailable":
            weather_line = f"🌡  {C_LABEL}{city_name}  (weather unavailable){RESET}"
        else:
            weather_line = f"🌡  {C_LABEL}fetching weather…{RESET}"
        lines.append(box_row(weather_line, width))
        lines.append(box_divider(width))

    # Rows 3+: Countdowns
    if countdowns:
        for label, days in countdowns:
            bar   = countdown_bar(days, width=12)
            dlbl  = days_label(days)
            left  = f"{C_CDOWN}⏳{RESET}  {C_VALUE}{label}{RESET}"
            right = f"{bar}  {dlbl}"
            lines.append(box_row_two(left, right, width))
        lines.append(box_divider(width))

    # Last row: user@host  |  uptime
    user_part   = f"👤  {C_USER}{BOLD}{user_host}{RESET}"
    uptime_part = f"{C_LABEL}⏱  {RESET}{C_ACCENT}{uptime}{RESET}"
    lines.append(box_row_two(user_part, uptime_part, width))

    lines.append(box_bottom(width))

    print("\n".join(lines))

# ─── Setup wizard ─────────────────────────────────────────────────────────────

def setup():
    cfg = load_config()
    print(f"\n{BOLD}{C_ACCENT}dashterm setup wizard{RESET}\n")

    # City
    current_city = cfg.get("city", "")
    prompt_city  = f"  City for weather [{current_city or 'none'}]: "
    city = input(prompt_city).strip()
    if city:
        cfg["city"] = city
    elif not current_city:
        cfg["show_weather"] = False

    # Countdowns
    existing = cfg.get("countdowns", [])
    print(f"\n  {C_LABEL}Current countdowns:{RESET}")
    if existing:
        for i, c in enumerate(existing, 1):
            print(f"    {i}. {c['label']} → {c['date']}")
    else:
        print(f"    {C_DIM}(none){RESET}")

    print(f"\n  {C_LABEL}Add up to {5 - len(existing)} more countdown(s). Leave label blank to stop.{RESET}\n")

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
        print(f"  {C_ACCENT}✓ Added{RESET}\n")

    # Remove old countdowns?
    if existing and len(cfg["countdowns"]) > len(existing):
        pass  # already added, keep existing
    elif existing:
        ans = input(f"\n  Clear existing countdowns and keep only new ones? [y/N]: ").strip().lower()
        if ans == "y":
            cfg["countdowns"] = cfg["countdowns"][len(existing):]

    save_config(cfg)
    print(f"\n  {C_ACCENT}✓ Config saved to {CONFIG_FILE}{RESET}")
    print(f"  {C_LABEL}Run {C_VALUE}dashterm{RESET} {C_LABEL}to see your dashboard.{RESET}\n")

    # Preview
    ans = input("  Preview dashboard now? [Y/n]: ").strip().lower()
    if ans != "n":
        print()
        render(cfg)

# ─── Live mode ────────────────────────────────────────────────────────────────

def live(cfg: dict):
    """Live-updating mode: refreshes the clock every second."""
    try:
        while True:
            # Move cursor to top-left and clear
            print("\033[H\033[J", end="")
            render(cfg)
            print(f"\n  {C_DIM}Press Ctrl+C to exit{RESET}")
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{C_DIM}  Goodbye.{RESET}\n")

# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--setup" in args:
        setup()
        return

    cfg = load_config()

    if not cfg["city"] and not cfg["countdowns"]:
        # First run — nudge the user
        print(f"\n  {C_ACCENT}{BOLD}dashterm{RESET}  {C_LABEL}— run {C_VALUE}dashterm --setup{RESET}{C_LABEL} to configure weather & countdowns{RESET}\n")

    if "--live" in args:
        live(cfg)
    else:
        render(cfg)

if __name__ == "__main__":
    main()
