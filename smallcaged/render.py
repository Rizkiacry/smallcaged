from __future__ import annotations

from smallcaged.filter import _find_finger_label
from smallcaged.shape import Shape, format_shape


def shape_to_finger_label(shape: Shape) -> str:
    fretted = [f for f in shape if f != -1 and f != 0]
    label = _find_finger_label(fretted)
    if label is None:
        return "?"
    return label if label else ""


def render_chord_group(root: str, chord_type: str, shapes: list[Shape]) -> str:
    display_type = chord_type if chord_type else "maj"
    lines: list[str] = [
        f"=== {root} {display_type} ===",
        f"{'Shape':<24} {'Fingers':<10}",
        f"{'-'*24} {'-'*10}",
    ]
    for shape in shapes:
        label = shape_to_finger_label(shape)
        lines.append(f"{format_shape(shape):<24} {label:<10}")
    lines.append("")
    return "\n".join(lines)
