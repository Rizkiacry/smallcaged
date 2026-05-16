from __future__ import annotations

from smallcaged.filter import WINDOWS
from smallcaged.shape import Shape, format_shape

_FINGER_LABELS: dict[frozenset[int], str] = {
    frozenset({0, 2}): "w-y",
    frozenset({0, 2, 3}): "w-y-z",
    frozenset({1, 3}): "x-z",
    frozenset({1, 2}): "x-y",
    frozenset({0, 1, 3}): "w-x-z",
}


def _find_finger_pattern(fretted: list[int]) -> str | None:
    if not fretted:
        return ""
    lo = min(fretted)
    hi = max(fretted)
    for w_lo, w_hi in WINDOWS:
        if lo >= w_lo and hi <= w_hi:
            used = frozenset(f - w_lo for f in fretted)
            if used in _FINGER_LABELS:
                return _FINGER_LABELS[used]
    return None


def shape_to_finger_label(shape: Shape) -> str:
    fretted = [f for f in shape if f != -1 and f != 0]
    label = _find_finger_pattern(fretted)
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
