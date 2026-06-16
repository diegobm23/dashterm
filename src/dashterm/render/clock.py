"""Big multi-line clock fonts for the 'large' and 'ascii' clock styles."""

# "large" — chunky block digits drawn with █ (5 rows tall).
_BLOCK_FONT = {
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": ["  █", "  █", "  █", "  █", "  █"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", "  █", "  █", "  █"],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    ":": [" ", "█", " ", "█", " "],
}

# "ascii" — seven-segment style digital digits drawn with _ and | (3 rows tall).
_ASCII_FONT = {
    "0": [" _ ", "| |", "|_|"],
    "1": ["   ", "  |", "  |"],
    "2": [" _ ", " _|", "|_ "],
    "3": [" _ ", " _|", " _|"],
    "4": ["   ", "|_|", "  |"],
    "5": [" _ ", "|_ ", " _|"],
    "6": [" _ ", "|_ ", "|_|"],
    "7": [" _ ", "  |", "  |"],
    "8": [" _ ", "|_|", "|_|"],
    "9": [" _ ", "|_|", " _|"],
    ":": [" ", ".", "."],
}

def big_clock(time_str: str, style: str) -> list:
    """Render HH:MM:SS as a list of equal-height text rows in the given style."""
    font = _ASCII_FONT if style == "ascii" else _BLOCK_FONT
    rows = len(next(iter(font.values())))
    out  = []
    for r in range(rows):
        out.append("  ".join(font[ch][r] for ch in time_str if ch in font))
    return out
