from __future__ import annotations

# 6 strings: low E (idx 0) to high E (idx 5)
# Values: 0-24 for frets, -1 for muted (x)
Shape = tuple[int, int, int, int, int, int]


def parse_fret(token: str) -> int:
    if token == "x":
        return -1
    return int(token)


def format_fret(fret: int) -> str:
    if fret == -1:
        return "x"
    return str(fret)


def format_shape(shape: Shape) -> str:
    return " ".join(format_fret(f) for f in shape)
