from __future__ import annotations

from smallcaged.shape import Shape


def rule_no_duplicate_frets(shape: Shape) -> bool:
    seen: set[int] = set()
    for fret in shape:
        if fret == -1 or fret == 0:
            continue
        if fret in seen:
            return False
        seen.add(fret)
    return True


WINDOWS = [(1, 4), (3, 6), (5, 8), (7, 10), (9, 12), (11, 14)]


def rule_fits_5_fret_window(shape: Shape) -> bool:
    fretted = [f for f in shape if f != -1 and f != 0]
    if not fretted:
        return True
    lo = min(fretted)
    hi = max(fretted)
    return any(lo >= w_lo and hi <= w_hi for w_lo, w_hi in WINDOWS)


FINGER_LABELS: dict[frozenset[int], str] = {
    frozenset({0, 2}): "w-y",
    frozenset({0, 2, 3}): "w-y-z",
    frozenset({1, 3}): "x-z",
    frozenset({1, 2}): "x-y",
    frozenset({0, 1, 3}): "w-x-z",
}

ALLOWED_FINGER_SETS: set[frozenset[int]] = set(FINGER_LABELS.keys())


def _find_finger_label(fretted: list[int]) -> str | None:
    if not fretted:
        return ""
    lo = min(fretted)
    hi = max(fretted)
    for w_lo, w_hi in WINDOWS:
        if lo >= w_lo and hi <= w_hi:
            used = frozenset(f - w_lo for f in fretted)
            if used in FINGER_LABELS:
                return FINGER_LABELS[used]
    return None


def rule_wxyz_finger_combo(shape: Shape) -> bool:
    fretted = [f for f in shape if f != -1 and f != 0]
    if not fretted:
        return True
    return _find_finger_label(fretted) is not None


def rule_no_muted_gaps(shape: Shape) -> bool:
    non_muted = [i for i, f in enumerate(shape) if f != -1]
    if not non_muted:
        return True
    for i in range(non_muted[0], non_muted[-1] + 1):
        if shape[i] == -1:
            return False
    return True


def find_section(shape: Shape) -> str | None:
    fretted = [f for f in shape if f != -1 and f != 0]
    if not fretted:
        return None
    lo = min(fretted)
    hi = max(fretted)
    for w_lo, w_hi in WINDOWS:
        if lo >= w_lo and hi <= w_hi:
            return f"{w_lo}-{w_hi}"
    return None


def is_valid_shape(shape: Shape) -> bool:
    return (
        rule_no_duplicate_frets(shape)
        and rule_fits_5_fret_window(shape)
        and rule_wxyz_finger_combo(shape)
        and rule_no_muted_gaps(shape)
    )
