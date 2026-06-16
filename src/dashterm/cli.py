"""Command-line entry point and argument dispatch."""

import sys
import time

from . import __version__
from .config import load_config
from .theme import C, BOLD, RESET
from .dashboard import render
from .wizard import setup, show_config

USAGE = """\
dashterm — Terminal dashboard for your shell startup.
Usage:
    dashterm            → static snapshot (for .bashrc / .zshrc)
    dashterm --live     → live updating clock (standalone mode)
    dashterm --setup    → interactive configuration wizard
    dashterm --config   → print the config file path and contents
    dashterm --version  → show version
    dashterm --help     → show usage\
"""

def live(cfg: dict):
    """Live-updating mode: refreshes the clock every second."""
    try:
        while True:
            # Move cursor to top-left and clear
            print("\033[H\033[J", end="")
            render(cfg)
            print(f"\n  {C.DIM}Press Ctrl+C to exit{RESET}")
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{C.DIM}  Goodbye.{RESET}\n")

def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(USAGE)
        return

    if "--version" in args or "-v" in args:
        print(f"dashterm {__version__}")
        return

    if "--setup" in args:
        setup()
        return

    if "--config" in args:
        show_config()
        return

    cfg = load_config()

    if not cfg["city"] and not cfg["countdowns"]:
        # First run — nudge the user
        print(f"\n  {C.ACCENT}{BOLD}dashterm{RESET}  {C.LABEL}— run {C.VALUE}dashterm --setup{RESET}{C.LABEL} to configure weather & countdowns{RESET}\n")

    if "--live" in args:
        live(cfg)
    else:
        render(cfg)

if __name__ == "__main__":
    main()
