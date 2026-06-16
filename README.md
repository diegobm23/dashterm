# dashterm

A lightweight terminal dashboard — displays clock, date, weather, countdowns, uptime, and user info every time you open a terminal.
<img width="751" height="446" alt="dashterm-print" src="https://github.com/user-attachments/assets/7d71075a-331e-4820-9d3d-64dd945e3b6e" />

## Requirements

- Python 3.9+ (uses standard-library generics like `tuple[...]`)
- No third-party dependencies — pure Python standard library, nothing to `pip install`
- A Unicode/emoji-capable terminal with 24-bit (truecolor) support, for correct icons and alignment
- Internet connection (for weather — uses [wttr.in](https://wttr.in), no API key needed)

## Install

```bash
bash install.sh
```

The installer will:
1. Copy `dashterm` to `~/.local/bin/`
2. Optionally add it to your `.bashrc` or `.zshrc`
3. Run the setup wizard (city, weather refresh period & countdowns)

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
| `dashterm --version` | Show version |
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
  "use_color": true,
  "weather_cache_minutes": 30,
  "countdowns": [
    { "label": "New Year",       "date": "2027-01-01" },
    { "label": "Project Launch", "date": "2026-09-15" }
  ]
}
```

You can edit it directly or run `dashterm --setup` again.

- `city` — location used for the weather lookup.
- `show_weather` — set to `false` to hide the weather row entirely.
- `use_color` — set to `false` for plain, ANSI-free output (useful for logs or color-less terminals).
- `weather_cache_minutes` — how long a fetched forecast is reused before hitting the API again (default `30`). Weather is cached at `~/.config/dashterm/weather_cache.json`, so opening a new terminal won't re-fetch until the cache expires.
- `countdowns` — list of `{ "label", "date" }` entries (date as `YYYY-MM-DD`), up to 5.

## Notes

- Weather uses [wttr.in](https://wttr.in) — no account or API key required
- Uptime works on Linux and macOS
- Colors use 24-bit ANSI — works in any modern terminal emulator

## Uninstall

```bash
# Remove the executable
rm -f ~/.local/bin/dashterm

# Remove your config & cache
rm -rf ~/.config/dashterm
```

Also delete the `dashterm` startup line from your `~/.bashrc` or `~/.zshrc` if you added one.

## License

[MIT](LICENSE)
