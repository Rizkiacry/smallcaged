from __future__ import annotations

import re
import typing

from smallcaged.shape import Shape, parse_fret

SHAPE_LINE_RE = re.compile(
    r"^\s*(?:x|\d+)\s+(?:x|\d+)\s+(?:x|\d+)\s+(?:x|\d+)\s+(?:x|\d+)\s+(?:x|\d+)\s*$"
)


def parse_chord_file(root: str, chord_type: str, text: str) -> list[Shape]:
    shapes: list[Shape] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip header lines
        if not SHAPE_LINE_RE.match(stripped):
            continue
        tokens = stripped.split()
        if len(tokens) != 6:
            continue
        frets = tuple(parse_fret(t) for t in tokens)
        shapes.append(typing.cast(Shape, frets))
    return shapes
