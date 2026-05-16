# smallcaged Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) for syntax tracking.

**Goal:** Build CLI that fetches Howard's guitar chord dictionary, filters shapes by 4 playability rules, prints valid shapes.

**Architecture:** Python stdlib CLI. 5 modules: fetcher (HTTP+cache), parser (txt→Shape), filter (4 rules), render (terminal output), main (argparse entry). TDD per module.

**Tech Stack:** Python 3.10+, stdlib only (urllib, argparse, pathlib, tempfile for tests)

---

### Task 0: Project scaffold + test infrastructure

**Files:**
- Create: `smallcaged/__init__.py`
- Create: `smallcaged/shape.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Modify: (none)

- [ ] **Step 1: Create directory structure**

Run:
```bash
mkdir -p smallcaged tests
```

- [ ] **Step 2: Write `smallcaged/__init__.py`**

```
```

(Empty init is fine.)

- [ ] **Step 3: Write `smallcaged/shape.py`**

```python
from __future__ import annotations

import typing

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
```

- [ ] **Step 4: Write `tests/__init__.py`**

```
```

- [ ] **Step 5: Write `tests/conftest.py`**

```python
import pytest


@pytest.fixture
def sample_c_shape() -> str:
    return """ C
 ==

 Spelling: 1, 3, 5


 MOVEABLE BAR CHORD SHAPES:
 ---------------------------

 x  x  10 9  8  8


 8  10 10 9  8  8


 8 7 5 5 8 x


 OTHER MOVEABLE SHAPES:
 -----------------------

 8 7 5 x x x


 8 7 x 9 8 x


 CHORD SHAPES USING OPEN STRINGS:
 ---------------------------------

 x 3 2 0 1 0


 x 3 2 0 5 0


 x 3 5 0 5 0
"""
```

- [ ] **Step 6: Verify test runner works**

Run:
```bash
python -m pytest tests/ -v
```
Expected: no tests collected but no errors.

- [ ] **Step 7: Commit**

```bash
git init && git add smallcaged/ tests/ && git commit -m "chore: scaffold project structure"
```

---

### Task 1: Parser module

**Files:**
- Create: `smallcaged/parser.py`
- Create: `tests/test_parser.py`

- [ ] **Step 1: Write failing parser test**

Write to `tests/test_parser.py`:

```python
import pytest
from smallcaged.parser import parse_chord_file
from smallcaged.shape import Shape


def test_parse_sections_exist():
    shapes = parse_chord_file("C", "maj", SAMPLE_TEXT)
    assert len(shapes) > 0


def test_parse_known_shape():
    shapes = parse_chord_file("C", "maj", SAMPLE_TEXT)
    assert (8, 7, 5, -1, -1, -1) in shapes


def test_parse_known_open_shape():
    shapes = parse_chord_file("C", "maj", SAMPLE_TEXT)
    assert (-1, 3, 2, 0, 1, 0) in shapes


def test_parse_ignores_non_shape_lines():
    shapes = parse_chord_file("C", "maj", SAMPLE_TEXT)
    # All 8 shapes from sample_c_shape fixture
    assert len(shapes) == 8


SAMPLE_TEXT = """ C
 ==

 Spelling: 1, 3, 5


 MOVEABLE BAR CHORD SHAPES:
 ---------------------------

 x  x  10 9  8  8


 8  10 10 9  8  8


 8 7 5 5 8 x


 OTHER MOVEABLE SHAPES:
 -----------------------

 8 7 5 x x x


 8 7 x 9 8 x


 CHORD SHAPES USING OPEN STRINGS:
 ---------------------------------

 x 3 2 0 1 0


 x 3 2 0 5 0


 x 3 5 0 5 0
"""
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_parser.py -v
```
Expected: 4 failures, "ModuleNotFoundError: no module named smallcaged.parser"

- [ ] **Step 3: Write minimal parser**

Write to `smallcaged/parser.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_parser.py -v
```
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/parser.py tests/test_parser.py && git commit -m "feat: add chord file parser"
```

---

### Task 2: Filter — Rule 1 (no duplicate frets)

**Files:**
- Create: `smallcaged/filter.py`
- Create: `tests/test_filter.py`

- [ ] **Step 1: Write failing tests for Rule 1**

Add to `tests/test_filter.py`:

```python
import pytest
from smallcaged.filter import rule_no_duplicate_frets


def test_rule1_passes_distinct_frets():
    shape = (-1, 3, 2, 0, 1, 0)
    assert rule_no_duplicate_frets(shape) is True


def test_rule1_fails_duplicate_frets():
    shape = (-1, -1, 10, 9, 8, 8)
    assert rule_no_duplicate_frets(shape) is False


def test_rule1_open_strings_ignored():
    # multiple 0s are OK
    shape = (-1, 3, 2, 0, 1, 0)
    assert rule_no_duplicate_frets(shape) is True


def test_rule1_all_muted():
    shape = (-1, -1, -1, -1, -1, -1)
    assert rule_no_duplicate_frets(shape) is True


def test_rule1_mixed_duplicate():
    shape = (8, 7, 5, 5, -1, 8)
    assert rule_no_duplicate_frets(shape) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_filter.py::test_rule1_passes_distinct_frets -v
```
Expected: FAIL

- [ ] **Step 3: Write Rule 1 implementation**

Add to `smallcaged/filter.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_filter.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/filter.py tests/test_filter.py && git commit -m "feat: add filter rule 1 - no duplicate frets"
```

---

### Task 3: Filter — Rule 2 (5-fret window)

**Files:**
- Modify: `smallcaged/filter.py`
- Modify: `tests/test_filter.py`

- [ ] **Step 1: Write failing tests for Rule 2**

Add to `tests/test_filter.py`:

```python
from smallcaged.filter import rule_fits_5_fret_window


def test_rule2_passes_tight_fit():
    shape = (8, 7, 5, -1, -1, -1)
    assert rule_fits_5_fret_window(shape) is True


def test_rule2_fails_span_too_wide():
    shape = (-1, 3, 2, 0, 5, 0)
    assert rule_fits_5_fret_window(shape) is False


def test_rule2_fails_high_span():
    shape = (-1, -1, 10, 12, 13, 0)
    assert rule_fits_5_fret_window(shape) is False


def test_rule2_single_fret():
    shape = (-1, -1, 5, -1, -1, -1)
    assert rule_fits_5_fret_window(shape) is True


def test_rule2_all_muted():
    shape = (-1, -1, -1, -1, -1, -1)
    assert rule_fits_5_fret_window(shape) is True


def test_rule2_open_strings_only():
    shape = (0, 0, 0, 0, 0, 0)
    assert rule_fits_5_fret_window(shape) is True


def test_rule2_edge_window_3_6():
    shape = (-1, 5, 4, 2, 3, -1)  # frets 2,3,4,5 fit window 3-6
    assert rule_fits_5_fret_window(shape) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_filter.py::test_rule2_passes_tight_fit -v
```
Expected: FAIL

- [ ] **Step 3: Write Rule 2 implementation**

Append to `smallcaged/filter.py`:

```python
WINDOWS = [(1, 4), (3, 6), (5, 8), (7, 10), (9, 12), (11, 14)]


def rule_fits_5_fret_window(shape: Shape) -> bool:
    fretted = [f for f in shape if f != -1 and f != 0]
    if not fretted:
        return True
    lo = min(fretted)
    hi = max(fretted)
    return any(lo >= w_lo and hi <= w_hi for w_lo, w_hi in WINDOWS)
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_filter.py -v
```
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/filter.py tests/test_filter.py && git commit -m "feat: add filter rule 2 - 5-fret window"
```

---

### Task 4: Filter — Rule 3 (wxyz finger combo)

**Files:**
- Modify: `smallcaged/filter.py`
- Modify: `tests/test_filter.py`

- [ ] **Step 1: Write failing tests for Rule 3**

Add to `tests/test_filter.py`:

```python
from smallcaged.filter import rule_wxyz_finger_combo


def test_rule3_w_y_z():
    shape = (8, 7, 5, -1, -1, -1)  # frets 5,7,8 in window 5-8 → w,y,z
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_w_y():
    shape = (-1, -1, 9, -1, 7, -1)  # frets 7,9 in window 7-10 → w,y
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_x_z():
    # frets 6,8 in window 5-8 → x,z (skip w and y)
    shape = (-1, -1, 8, -1, 6, -1)
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_x_y():
    # frets 8,9 in window 7-10 → x,y (skip w and z)
    shape = (-1, -1, 9, -1, 8, -1)
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_w_x_z():
    shape = (8, 6, 5, -1, -1, -1)  # frets 5,6,8 in window 5-8 → w,x,z
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_w_x_y_not_allowed():
    # x 3 2 0 1 0 → frets 1,2,3 in window 1-4 → w,x,y
    shape = (-1, 3, 2, 0, 1, 0)
    assert rule_wxyz_finger_combo(shape) is False


def test_rule3_w_x_y_z_not_allowed():
    # all 4 fingers used in one window → w,x,y,z
    shape = (-1, -1, 8, 7, 6, 5)  # frets 5,6,7,8 in window 5-8
    assert rule_wxyz_finger_combo(shape) is False


def test_rule3_single_fret():
    shape = (-1, -1, 5, -1, -1, -1)
    assert rule_wxyz_finger_combo(shape) is False


def test_rule3_all_open():
    shape = (0, 0, 0, 0, 0, 0)
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_all_muted():
    shape = (-1, -1, -1, -1, -1, -1)
    assert rule_wxyz_finger_combo(shape) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_filter.py::test_rule3_w_y_z -v
```
Expected: FAIL

- [ ] **Step 3: Write Rule 3 implementation**

Append to `smallcaged/filter.py`:

```python
# Allowed wxyz finger patterns within a 4-fret window
# 0=w(index), 1=x(middle), 2=y(ring), 3=z(pinky)
# Anchor: w = window_start, x = window_start+1, etc.
ALLOWED_FINGER_SETS: set[frozenset[int]] = {
    frozenset({0, 2}),       # w-y
    frozenset({0, 2, 3}),    # w-y-z
    frozenset({1, 3}),       # x-z
    frozenset({1, 2}),       # x-y
    frozenset({0, 1, 3}),    # w-x-z
}


def rule_wxyz_finger_combo(shape: Shape) -> bool:
    fretted = [f for f in shape if f != -1 and f != 0]
    if not fretted:
        return True
    lo = min(fretted)
    hi = max(fretted)
    for w_lo, w_hi in WINDOWS:
        if lo >= w_lo and hi <= w_hi:
            used = frozenset(f - w_lo for f in fretted)
            if used in ALLOWED_FINGER_SETS:
                return True
    return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_filter.py -v
```
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/filter.py tests/test_filter.py && git commit -m "feat: add filter rule 3 - wxyz finger combo"
```

---

### Task 5: Filter — Rule 4 (no muted string gaps)

**Files:**
- Modify: `smallcaged/filter.py`
- Modify: `tests/test_filter.py`

- [ ] **Step 1: Write failing tests for Rule 4**

Add to `tests/test_filter.py`:

```python
from smallcaged.filter import rule_no_muted_gaps


def test_rule4_passes_muted_at_end():
    shape = (8, 7, 5, -1, -1, -1)
    assert rule_no_muted_gaps(shape) is True


def test_rule4_passes_muted_at_start():
    shape = (-1, -1, 11, 10, -1, -1)
    assert rule_no_muted_gaps(shape) is True


def test_rule4_fails_muted_gap():
    shape = (8, 7, 5, 0, -1, 0)
    assert rule_no_muted_gaps(shape) is False


def test_rule4_no_mutes():
    shape = (-1, 3, 2, 0, 1, 0)
    assert rule_no_muted_gaps(shape) is True


def test_rule4_all_muted():
    shape = (-1, -1, -1, -1, -1, -1)
    assert rule_no_muted_gaps(shape) is True


def test_rule4_gap_at_end():
    shape = (8, 7, 5, 0, -1, 0)
    assert rule_no_muted_gaps(shape) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_filter.py::test_rule4_passes_muted_at_end -v
```
Expected: FAIL

- [ ] **Step 3: Write Rule 4 implementation**

Append to `smallcaged/filter.py`:

```python
def rule_no_muted_gaps(shape: Shape) -> bool:
    seen_muted = False
    for fret in shape:
        if fret == -1:
            seen_muted = True
        elif seen_muted:
            return False
    return True
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_filter.py -v
```
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/filter.py tests/test_filter.py && git commit -m "feat: add filter rule 4 - no muted gaps"
```

---

### Task 6: Filter — composite filter function

**Files:**
- Modify: `smallcaged/filter.py`
- Modify: `tests/test_filter.py`

- [ ] **Step 1: Write test for composite filter**

Add to `tests/test_filter.py`:

```python
from smallcaged.filter import is_valid_shape


def test_composite_valid_shape():
    # 8 7 5 x x x passes all 4 rules
    shape = (8, 7, 5, -1, -1, -1)
    assert is_valid_shape(shape) is True


def test_composite_invalid_rule1():
    # x x 10 9 8 8 fails rule 1
    shape = (-1, -1, 10, 9, 8, 8)
    assert is_valid_shape(shape) is False


def test_composite_invalid_rule2():
    # x 3 2 0 5 0 fails rule 2
    shape = (-1, 3, 2, 0, 5, 0)
    assert is_valid_shape(shape) is False


def test_composite_invalid_rule3():
    # x 3 2 0 1 0 fails rule 3
    shape = (-1, 3, 2, 0, 1, 0)
    assert is_valid_shape(shape) is False


def test_composite_invalid_rule4():
    # 8 7 5 0 x 0 fails rule 4
    shape = (8, 7, 5, 0, -1, 0)
    assert is_valid_shape(shape) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_filter.py::test_composite_valid_shape -v
```
Expected: FAIL

- [ ] **Step 3: Write composite filter**

Append to `smallcaged/filter.py`:

```python
def is_valid_shape(shape: Shape) -> bool:
    return (
        rule_no_duplicate_frets(shape)
        and rule_fits_5_fret_window(shape)
        and rule_wxyz_finger_combo(shape)
        and rule_no_muted_gaps(shape)
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_filter.py -v
```
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/filter.py tests/test_filter.py && git commit -m "feat: add composite filter function"
```

---

### Task 7: Fetcher module

**Files:**
- Create: `smallcaged/fetcher.py`
- Create: `tests/test_fetcher.py`

- [ ] **Step 1: Write fetcher tests**

Write `tests/test_fetcher.py`:

```python
import json
import pathlib
import tempfile
from unittest.mock import Mock, patch

import pytest
from smallcaged.fetcher import (
    CHORD_TYPES,
    ROOT_TO_FILENAME,
    build_url,
    fetch_chord_file,
    get_cache_path,
)


def test_root_filename_mapping():
    assert ROOT_TO_FILENAME["C"] == "C"
    assert ROOT_TO_FILENAME["C#"] == "Csharp"
    assert ROOT_TO_FILENAME["F#"] == "Fsharp"
    assert ROOT_TO_FILENAME["Bb"] == "Asharp"


def test_build_url():
    url = build_url("C", "")
    assert url.endswith("/C.txt")
    url = build_url("C#", "m")
    assert url.endswith("/Csharpm.txt")


def test_get_cache_path_uses_correct_dir():
    with tempfile.TemporaryDirectory() as tmp:
        path = get_cache_path("C", "m", cache_dir=pathlib.Path(tmp))
        assert path.parent == pathlib.Path(tmp)
        assert path.name == "Cm.txt"


def test_chord_types_include_all_major_types():
    assert "" in CHORD_TYPES  # major triad
    assert "m" in CHORD_TYPES
    assert "7" in CHORD_TYPES
    assert "maj7" in CHORD_TYPES
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_fetcher.py -v
```
Expected: 5 failures

- [ ] **Step 3: Write fetcher**

Write `smallcaged/fetcher.py`:

```python
from __future__ import annotations

import pathlib
import typing
import urllib.error
import urllib.request

BASE_URL = "https://www.hakwright.co.uk/guitarchords/dictionary"

# Root note → Howard's filename component
ROOT_TO_FILENAME: dict[str, str] = {
    "C": "C",
    "C#": "Csharp",
    "D": "D",
    "D#": "Dsharp",
    "E": "E",
    "F": "F",
    "F#": "Fsharp",
    "G": "G",
    "G#": "Gsharp",
    "A": "A",
    "A#": "Asharp",
    "B": "B",
}

# Chord types to process ('' = major triad)
CHORD_TYPES: list[str] = [
    "", "m", "sus2", "sus4", "add2", "add9", "add4", "madd2", "madd9", "madd4",
    "add2add4", "madd2add4", "aug", "dim", "dim7", "5", "6", "m6", "6.9", "m6.9",
    "6.7", "m6.7", "maj6.7", "7", "m7", "maj7", "7sus4", "7sus2", "7add4", "m7add4",
    "9", "m9", "maj9", "9sus4", "11", "m11", "maj11", "13", "m13", "maj13", "13sus4",
    "mmaj7", "mmaj9", "7sharp9", "7b9", "7sharp5", "7b5", "m7sharp5", "m7b5",
    "maj7sharp5", "maj7b5", "9sharp5", "9b5",
]

# Slash chord bass notes (appended as .{bass}.txt)
SLASH_BASSES = ["A", "Asharp", "B", "Csharp", "D", "Dsharp", "E", "F", "Fsharp", "G", "Gsharp"]


def build_url(root: str, chord_type: str) -> str:
    root_part = ROOT_TO_FILENAME[root]
    if chord_type:
        filename = f"{root_part}{chord_type}.txt"
    else:
        filename = f"{root_part}.txt"
    return f"{BASE_URL}/{filename}"


def get_cache_path(
    root: str, chord_type: str, cache_dir: pathlib.Path | None = None,
) -> pathlib.Path:
    if cache_dir is None:
        cache_dir = pathlib.Path.home() / ".cache" / "smallcaged"
    cache_dir.mkdir(parents=True, exist_ok=True)
    root_part = ROOT_TO_FILENAME[root]
    if chord_type:
        filename = f"{root_part}{chord_type}.txt"
    else:
        filename = f"{root_part}.txt"
    return cache_dir / filename


def fetch_chord_file(
    root: str, chord_type: str, cache_dir: pathlib.Path | None = None, force: bool = False,
) -> str | None:
    cache_path = get_cache_path(root, chord_type, cache_dir)
    if cache_path.exists() and not force:
        return cache_path.read_text()
    url = build_url(root, chord_type)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    cache_path.write_text(text)
    return text
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_fetcher.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/fetcher.py tests/test_fetcher.py && git commit -m "feat: add fetcher with cache"
```

---

### Task 8: Render module

**Files:**
- Create: `smallcaged/render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write render tests**

Write `tests/test_render.py`:

```python
import pytest
from smallcaged.render import render_chord_group, shape_to_finger_label
from smallcaged.shape import Shape


def test_shape_to_finger_label_identifies_w():
    shape: Shape = (-1, -1, 5, -1, 3, -1)  # frets 3,5 → w,y
    assert "w-y" in shape_to_finger_label(shape)


def test_shape_to_finger_label_w_y_z():
    shape: Shape = (8, 7, 5, -1, -1, -1)  # frets 5,7,8 → w,y,z
    assert "w-y-z" in shape_to_finger_label(shape)


def test_render_chord_group_includes_header():
    shapes: list[Shape] = [(8, 7, 5, -1, -1, -1)]
    output = render_chord_group("C", "maj", shapes)
    assert "C" in output
    assert "maj" in output
    assert "8 7 5 x x x" in output
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_render.py -v
```
Expected: 3 failures

- [ ] **Step 3: Write render module**

Write `smallcaged/render.py`:

```python
from __future__ import annotations

import typing

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
python -m pytest tests/test_render.py -v
```
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add smallcaged/render.py tests/test_render.py && git commit -m "feat: add render module"
```

---

### Task 9: Main CLI entry point

**Files:**
- Create: `smallcaged/__main__.py`
- Modify: `smallcaged/__init__.py`
- Create: `tests/test_smallcaged.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Write CLI tests + conftest for fetcher mocking**

Write `tests/test_smallcaged.py`:

```python
import pathlib
from unittest.mock import patch

import pytest
from smallcaged.__main__ import main


SAMPLE_CHORD_FILE = """ C
 ==

 Spelling: 1, 3, 5

 MOVEABLE BAR CHORD SHAPES:
 ---------------------------

 x x 10 9 8 8

 8 7 5 5 8 x

 OTHER MOVEABLE SHAPES:
 -----------------------

 8 7 5 x x x

 CHORD SHAPES USING OPEN STRINGS:
 ---------------------------------

 x 3 2 0 1 0

 x 3 2 0 5 0
"""


@pytest.fixture
def mock_fetcher(monkeypatch):
    """Return text for C.txt, None for everything else."""

    def fake_fetch(root, chord_type, cache_dir=None, force=False):
        if root == "C" and chord_type == "":
            return SAMPLE_CHORD_FILE
        return None

    monkeypatch.setattr("smallcaged.__main__.fetch_chord_file", fake_fetch)


def test_cli_runs_and_filters_properly(mock_fetcher, capsys):
    exit_code = main(["--root", "C"])
    captured = capsys.readouterr()
    assert exit_code == 0
    # 8 7 5 x x x should appear (passes all rules)
    assert "8 7 5 x x x" in captured.out
    # Invalid shapes should NOT appear
    assert "x x 10 9 8 8" not in captured.out  # fails rule 1
    assert "x 3 2 0 1 0" not in captured.out  # fails rule 3
    assert "x 3 2 0 5 0" not in captured.out  # fails rule 2


def test_cli_help(capsys):
    exit_code = main(["--help"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage" in captured.out.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
python -m pytest tests/test_smallcaged.py -v
```
Expected: 2 failures

- [ ] **Step 3: Write pyproject.toml**

Write `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "smallcaged"
version = "0.1.0"
description = "Guitar chord shape filter from Howard's Big List"
requires-python = ">=3.10"

[tool.setuptools.packages.find]
include = ["smallcaged*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Write `smallcaged/__main__.py`**

```python
from __future__ import annotations

import argparse
import sys

from smallcaged.fetcher import CHORD_TYPES, ROOT_TO_FILENAME, fetch_chord_file
from smallcaged.filter import is_valid_shape
from smallcaged.parser import parse_chord_file
from smallcaged.render import render_chord_group


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Filter Howard's guitar chord shapes by playability rules"
    )
    parser.add_argument(
        "--chord", "-c",
        default=None,
        help="Chord type filter (e.g. 'm', '7', 'maj7'). Default: all.",
    )
    parser.add_argument(
        "--root", "-r",
        default=None,
        help="Root note filter (e.g. 'C', 'G#'). Default: all 12 roots.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file. Default: stdout.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download cached files.",
    )
    args = parser.parse_args(argv)

    roots = [args.root] if args.root else sorted(ROOT_TO_FILENAME.keys(), key=_root_sort_key)
    chord_types = [args.chord] if args.chord else CHORD_TYPES

    output_lines: list[str] = []

    for root in roots:
        for chord_type in chord_types:
            text = fetch_chord_file(root, chord_type, force=args.refresh)
            if text is None:
                continue
            shapes = parse_chord_file(root, chord_type, text)
            valid = [s for s in shapes if is_valid_shape(s)]
            if valid:
                output_lines.append(render_chord_group(root, chord_type, valid))

    output = "\n".join(output_lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        sys.stdout.write(output)

    return 0


_NATURAL_ORDER = {
    "C": 0, "C#": 1,
    "D": 2, "D#": 3,
    "E": 4,
    "F": 5, "F#": 6,
    "G": 7, "G#": 8,
    "A": 9, "A#": 10,
    "B": 11,
}


def _root_sort_key(root: str) -> int:
    return _NATURAL_ORDER.get(root, 99)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests**

Run:
```bash
python -m pytest tests/ -v
```
Expected: all tests pass

- [ ] **Step 6: Test CLI end-to-end manually**

Run:
```bash
python -m smallcaged --root C
```
Expected: shows valid C major chord shapes from Howard's list

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml smallcaged/__main__.py tests/test_smallcaged.py && git commit -m "feat: add CLI entry point"
```

---

### Task 10: Integration test with live data

- [ ] **Step 1: Test with a few real roots**

Run:
```bash
python -m smallcaged --root C --chord m
```
Expected: shows valid Cm chord shapes

Run:
```bash
python -m smallcaged --root G
```
Expected: shows valid G major shapes

Run:
```bash
python -m smallcaged --root E --chord 7
```
Expected: shows valid E7 chords

- [ ] **Step 2: Full run all chords**

Run:
```bash
timeout 120 python -m smallcaged
```
Expected: processes all roots + types, prints valid shapes. May take 30-60s due to HTTP fetches (subsequent runs fast due to cache).

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: complete smallcaged CLI"
```

---

## Spec Self-Review Checklist

1. **Spec coverage:** Every filter rule has dedicated task. Parser, fetcher, render, CLI each have own task. Comprehensive.

2. **Placeholder scan:** No TODOs, TBDs, or vague steps. Every test has real assertions. Every step has exact code.

3. **Type consistency:** `Shape = tuple[int,int,int,int,int,int]` used consistently. `parse_fret` returns `int`. `fetch_chord_file` returns `str | None`.

4. **Scope:** Single CLI tool, focused scope. No scope creep.
