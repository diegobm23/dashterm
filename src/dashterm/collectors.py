"""Functions that gather the raw data the dashboard displays."""

import datetime
import os
import pathlib
import re
import shutil
import socket
import subprocess
import urllib.parse
import urllib.request

from .cache import load_weather_cache, save_weather_cache

def get_clock(time_format: str = "24h") -> str:
    """HH:MM:SS digits (12-hour, no AM/PM, when time_format == '12h')."""
    now = datetime.datetime.now()
    return now.strftime("%I:%M:%S" if time_format == "12h" else "%H:%M:%S")

def get_meridiem() -> str:
    """'AM' or 'PM' for the current time."""
    return datetime.datetime.now().strftime("%p")

def get_hour() -> int:
    return datetime.datetime.now().hour

def get_date() -> str:
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")

def get_username() -> str:
    return os.environ.get("USER") or os.environ.get("LOGNAME") or "there"

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

def get_loadavg() -> str:
    """1/5/15-minute load average, or '' if unavailable (e.g. Windows)."""
    try:
        a, b, c = os.getloadavg()
        return f"{a:.2f} {b:.2f} {c:.2f}"
    except (OSError, AttributeError):
        return ""

def _human_bytes(n: float) -> str:
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024 or unit == "T":
            return f"{n:.0f}{unit}" if unit in ("B", "K") else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}T"

def get_disk(path: str = "/") -> str:
    """Disk usage of the filesystem holding `path`, e.g. '63% · 120.4G free'."""
    try:
        total, used, free = shutil.disk_usage(path)
        pct = int(round(used / total * 100)) if total else 0
        return f"{pct}% · {_human_bytes(free)} free"
    except Exception:
        return ""

def get_battery() -> str:
    """Battery as 'NN% charging|discharging|charged', or '' if no battery."""
    # Linux: /sys/class/power_supply
    try:
        base = pathlib.Path("/sys/class/power_supply")
        for bat in sorted(base.glob("BAT*")):
            cap = (bat / "capacity").read_text().strip()
            status = (bat / "status").read_text().strip().lower()
            return f"{cap}% {status}"
    except Exception:
        pass
    # macOS: pmset -g batt
    try:
        out = subprocess.check_output(["pmset", "-g", "batt"], text=True, timeout=2)
        m = re.search(r"(\d+)%; (\w[\w\s]*?);", out)
        if m:
            pct, state = m.group(1), m.group(2).strip().lower()
            return f"{pct}% {state}"
    except Exception:
        pass
    return ""

def get_weather(city: str) -> str:
    """Fetch verbose weather from wttr.in (no API key needed). Unused by the
    default UI, but handy for callers that want the long form."""
    if not city:
        return ""
    try:
        url = f"http://wttr.in/{urllib.parse.quote(city)}?format=%C+%t+%h+humidity"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = resp.read().decode().strip()
        # raw is like: "Partly cloudy +24°C 72% humidity"
        return raw
    except Exception:
        return "unavailable"

def get_weather_short(city: str, cache_minutes: float = 30, unit: str = "C") -> tuple[str, str]:
    """Returns (condition, temp_string) or ('', '') on failure.

    `unit` is "C" (metric) or "F" (USCS); it controls the wttr.in units and is
    part of the cache key. Results are cached and reused for up to
    `cache_minutes` to avoid hitting the API on every shell startup.
    """
    if not city:
        return "", ""

    cached = load_weather_cache(city, cache_minutes, unit)
    if cached is not None:
        return cached

    try:
        flag = "u" if unit == "F" else "m"   # wttr.in: u=USCS/°F, m=metric/°C
        url = f"http://wttr.in/{urllib.parse.quote(city)}?format=%C|%t&{flag}"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = resp.read().decode().strip()
        parts = raw.split("|")
        condition = parts[0].strip() if parts else "?"
        temp      = parts[1].strip() if len(parts) > 1 else "?"
        save_weather_cache(city, condition, temp, unit)
        return condition, temp
    except Exception:
        # On failure, fall back to any stale cache rather than showing nothing.
        stale = load_weather_cache(city, float("inf"), unit)
        if stale is not None:
            return stale
        return "unavailable", ""

def get_countdowns(countdowns: list) -> list:
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
