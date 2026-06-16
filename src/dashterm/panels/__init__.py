"""Panel registry.

Each panel module exposes ``build(cfg, width) -> list[str]`` returning the box
rows for that section (or ``[]`` to skip it). To add a feature, drop a new
module here, give it a ``build`` function, and register it below.
"""

from . import clock, weather, countdowns, system, user

PANELS = {
    "clock": clock.build,
    "weather": weather.build,
    "countdowns": countdowns.build,
    "system": system.build,
    "user": user.build,
}
