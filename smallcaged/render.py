from __future__ import annotations
import unicodedata

from smallcaged.filter import _find_finger_label, find_section
from smallcaged.shape import Shape, format_shape

_DOT_DIGITS = frozenset({"3", "5", "7", "9"})


def _vis_len(s: str) -> int:
    return sum(1 for c in s if unicodedata.combining(c) == 0)

def _ljust_vis(s: str, width: int) -> str:
    pad = width - _vis_len(s)
    return s + " " * max(0, pad)

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
    root: str, chord_type: str, shapes: list[Shape], *,
    dotted: bool = False, show_section: bool = True, bass: str | None = None,
    reorder: bool = False,
) -> str:
    display_type = chord_type if chord_type else "maj"
    fmt = _format_dotted if dotted else format_shape

    if bass:
        if chord_type:
            group_header = f"=== {root} {chord_type}/{bass} ==="
        else:
            group_header = f"=== {root}/{bass} ==="
    else:
        group_header = f"=== {root} {display_type} ==="

    if reorder:
        if show_section:
            header = f"{'Fingers':<10} {'Section':<8} {'Shape':<24}"
            sep = f"{'-'*10} {'-'*8} {'-'*24}"
        else:
            header = f"{'Fingers':<10} {'Shape':<24}"
            sep = f"{'-'*10} {'-'*24}"
    else:
        if show_section:
            header = f"{'Shape':<24} {'Section':<8} {'Fingers':<10}"
            sep = f"{'-'*24} {'-'*8} {'-'*10}"
        else:
            header = f"{'Shape':<24} {'Fingers':<10}"
            sep = f"{'-'*24} {'-'*10}"

    lines: list[str] = [
        group_header,
        header,
        sep,
    ]
    for shape in shapes:
        label = shape_to_finger_label(shape)
        section = find_section(shape) or ""
        shape_str = _ljust_vis(fmt(shape), 24)
        if show_section:
            if reorder:
                lines.append(f"{label:<10} {section:<8} {shape_str}")
            else:
                lines.append(f"{shape_str} {section:<8} {label:<10}")
        else:
            if reorder:
                lines.append(f"{label:<10} {shape_str}")
            else:
                lines.append(f"{shape_str} {label:<10}")
    lines.append("")
    return "\n".join(lines)
