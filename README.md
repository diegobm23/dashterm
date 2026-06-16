# dashterm

A lightweight terminal dashboard — displays clock, date, weather, countdowns, uptime, and user info every time you open a terminal.

```
╭──────────────────────────────────────────────────────────────────────╮
│  Tuesday, June 16, 2026                              09:41:22  🕐    │
├──────────────────────────────────────────────────────────────────────┤
│  ☀️  São Paulo  +24°C  Sunny                                         │
├──────────────────────────────────────────────────────────────────────┤
│  ⏳  New Year          ░░░░░░░░░░██   199 days                       │
│  ⏳  Project Launch    ░░░░░░░░████    91 days                       │
├──────────────────────────────────────────────────────────────────────┤
│  👤  alex@macbook-pro                          ⏱  up 3d 4h 22m      │
╰──────────────────────────────────────────────────────────────────────╯
```

## Requirements

- Python 3.8+
- Internet connection (for weather — uses [wttr.in](https://wttr.in), no API key needed)

## Install

```bash
bash install.sh
```

The installer will:
1. Copy `dashterm` to `~/.local/bin/`
2. Optionally add it to your `.bashrc` or `.zshrc`
3. Run the setup wizard

## Manual install

```bash
cp dashterm.py ~/.local/bin/dashterm
chmod +x ~/.local/bin/dashterm
dashterm --setup
```

## Usage

| Command | Description |
|---|---|
| `dashterm` | Static snapshot — instant render |
| `dashterm --live` | Live clock, updates every second |
| `dashterm --setup` | Configure city & countdowns |
| `dashterm --config` | Print the config file path & contents |
| `dashterm --help` | Show help |

## Shell startup

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# dashterm — terminal dashboard
dashterm
```

## Config

Stored at `~/.config/dashterm/config.json`:

```json
{
  "city": "São Paulo",
  "show_weather": true,
  "weather_cache_minutes": 30,
  "countdowns": [
    { "label": "New Year",       "date": "2027-01-01" },
    { "label": "Project Launch", "date": "2026-09-15" }
  ]
}
```

You can edit it directly or run `dashterm --setup` again.

- `weather_cache_minutes` — how long a fetched forecast is reused before hitting the API again (default `30`). Weather is cached at `~/.config/dashterm/weather_cache.json`, so opening a new terminal won't re-fetch until the cache expires.

## Notes

- Weather uses [wttr.in](https://wttr.in) — no account or API key required
- Uptime works on Linux and macOS
- Colors use 24-bit ANSI — works in any modern terminal emulator
