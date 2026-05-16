from __future__ import annotations

from smallcaged.filter import _find_finger_label, find_section
from smallcaged.shape import Shape, format_shape

_DOT_DIGITS = frozenset({"3", "5", "7", "9"})


def _dotted_fret(fret: str) -> str:
    return "".join(d + "\u0307" if d in _DOT_DIGITS else d for d in fret)


def _format_dotted(shape: Shape) -> str:
    parts: list[str] = []
    for f in shape:
        if f == -1:
            parts.append("x")
        else:
            parts.append(_dotted_fret(str(f)))
    return " ".join(parts)


def shape_to_finger_label(shape: Shape) -> str:
    fretted = [f for f in shape if f != -1 and f != 0]
    label = _find_finger_label(fretted)
    if label is None:
        return "?"
    return label if label else ""


def render_chord_group(
    root: str, chord_type: str, shapes: list[Shape], *, dotted: bool = False, show_section: bool = True,
) -> str:
    display_type = chord_type if chord_type else "maj"
    fmt = _format_dotted if dotted else format_shape

    if show_section:
        header = f"{'Shape':<24} {'Section':<8} {'Fingers':<10}"
        sep = f"{'-'*24} {'-'*8} {'-'*10}"
    else:
        header = f"{'Shape':<24} {'Fingers':<10}"
        sep = f"{'-'*24} {'-'*10}"

    lines: list[str] = [
        f"=== {root} {display_type} ===",
        header,
        sep,
    ]
    for shape in shapes:
        label = shape_to_finger_label(shape)
        section = find_section(shape) or ""
        if show_section:
            lines.append(f"{fmt(shape):<24} {section:<8} {label:<10}")
        else:
            lines.append(f"{fmt(shape):<24} {label:<10}")
    lines.append("")
    return "\n".join(lines)
