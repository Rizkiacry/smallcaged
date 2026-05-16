# Slash Chord / Bass Flag Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--bass`/`-b` flag to smallcaged CLI for slash chord support (e.g. `C/G`, `C#m/G#`)

**Architecture:** Optional `bass` param flows through fetcher → render pipeline. CLI passes `-b` value to URL construction and display header. Filter and parser unchanged.

**Tech Stack:** Python 3.10+, argparse, urllib

---

### Task 1: Add BASS_NOTES and bass param to fetcher.py

**Files:**
- Modify: `smallcaged/fetcher.py`
- Modify: `tests/test_fetcher.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_fetcher.py — append

from smallcaged.fetcher import BASS_NOTES, build_url, get_cache_path, fetch_chord_file

def test_bass_notes_list():
    assert "A" in BASS_NOTES
    assert "G#" in BASS_NOTES
    assert "C" not in BASS_NOTES
    assert len(BASS_NOTES) == 11

def test_build_url_with_bass():
    assert build_url("C", "", bass="G#").endswith("Csharp.Gsharp.txt")
    assert build_url("C", "m", bass="A").endswith("Cm.A.txt")
    assert build_url("C", "m").endswith("Cm.txt")

def test_get_cache_path_with_bass(tmp_path):
    assert get_cache_path("C", "", bass="A", cache_dir=tmp_path).name == "C.A.txt"

def test_fetch_chord_file_accepts_bass():
    r = fetch_chord_file("C", "m", bass="A")
    assert r is None or isinstance(r, str)
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_fetcher.py -v 2>&1 | head -30
```

- [ ] **Step 3: Add BASS_NOTES, update build_url, get_cache_path, fetch_chord_file**

```python
# smallcaged/fetcher.py — after CHORD_TYPES
BASS_NOTES: list[str] = [
    "A", "A#", "B", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
]

# Replace build_url
def build_url(root: str, chord_type: str, bass: str | None = None) -> str:
    root_part = ROOT_TO_FILENAME[root]
    filename = f"{root_part}{chord_type}" if chord_type else root_part
    if bass:
        filename = f"{filename}.{ROOT_TO_FILENAME[bass]}"
    filename += ".txt"
    return f"{BASE_URL}/{filename}"

# Replace get_cache_path — same URL logic
def get_cache_path(
    root: str, chord_type: str, cache_dir: pathlib.Path | None = None,
    bass: str | None = None,
) -> pathlib.Path:
    if cache_dir is None:
        cache_dir = pathlib.Path.home() / ".cache" / "smallcaged"
    cache_dir.mkdir(parents=True, exist_ok=True)
    root_part = ROOT_TO_FILENAME[root]
    filename = f"{root_part}{chord_type}" if chord_type else root_part
    if bass:
        filename = f"{filename}.{ROOT_TO_FILENAME[bass]}"
    filename += ".txt"
    return cache_dir / filename

# fetch_chord_file — add bass param, pass through
def fetch_chord_file(
    root: str, chord_type: str, cache_dir: pathlib.Path | None = None,
    force: bool = False, bass: str | None = None,
) -> str | None:
    cache_path = get_cache_path(root, chord_type, cache_dir, bass=bass)
    if cache_path.exists() and not force:
        return cache_path.read_text()
    url = build_url(root, chord_type, bass=bass)
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

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_fetcher.py -v 2>&1 | tail -20
```

- [ ] **Step 5: Commit**

```bash
git add smallcaged/fetcher.py tests/test_fetcher.py
git commit -m "feat: add BASS_NOTES + bass param to fetcher"
```

---

### Task 2: Add bass param to render.py

**Files:**
- Modify: `smallcaged/render.py`
- Modify: `tests/test_render.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_render.py — append

def test_render_header_with_bass():
    shapes = [(8, 7, 5, -1, -1, -1)]
    out = render_chord_group("C", "", shapes, bass="G#")
    assert "=== C/G# ===" in out

def test_render_header_with_bass_and_minor():
    shapes = [(8, 6, 5, -1, -1, -1)]
    out = render_chord_group("C", "m", shapes, bass="A")
    assert "=== C m/A ===" in out

def test_render_no_bass_still_works():
    shapes = [(8, 7, 5, -1, -1, -1)]
    out = render_chord_group("C", "", shapes)
    assert "=== C maj ===" in out
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_render.py -v 2>&1 | tail -20
```

- [ ] **Step 3: Update render_chord_group signature and header**

`render_chord_group` currently builds its header in two places: the `group_header` var before the `header`/`sep` lines, then used in the header/sep variables. The actual header line is `f"=== {root} {display_type} ==="`.

Change:
```python
# In render_chord_group, replace the line:
display_type = chord_type if chord_type else "maj"
# And the header usage "=== {root} {display_type} ==="

# With header logic:
if bass:
    group_header = f"=== {root} {chord_type}/{bass} ===" if chord_type else f"=== {root}/{bass} ==="
else:
    display_type = chord_type if chord_type else "maj"
    group_header = f"=== {root} {display_type} ==="
```

The function signature gets `bass: str | None = None` added to the keyword args.

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_render.py -v 2>&1 | tail -20
```

- [ ] **Step 5: Commit**

```bash
git add smallcaged/render.py tests/test_render.py
git commit -m "feat: add bass param to render_chord_group"
```

---

### Task 3: Add CLI --bass/-b flag

**Files:**
- Modify: `smallcaged/__main__.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_cli.py — new file

from smallcaged.__main__ import main

def test_cli_bass_flag():
    rc = main(["-r", "C", "-c", "m", "-b", "G#"])
    assert rc == 0

def test_cli_bass_flag_invalid_note():
    rc = main(["-r", "C", "-c", "m", "-b", "X"])
    assert rc == 1
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_cli.py -v 2>&1 | tail -20
```

- [ ] **Step 3: Add --bass arg, validate, wire through**

```python
# In smallcaged/__main__.py — add to argparse
parser.add_argument(
    "--bass", "-b",
    default=None,
    help="Bass note for slash chords (e.g. 'A', 'G#').",
)

# After root validation, add bass validation
if args.bass:
    # normalize: uppercase first letter, keep rest (handles "g#" → "G#")
    args.bass = args.bass[0].upper() + args.bass[1:] if len(args.bass) > 1 else args.bass.upper()
    if args.bass not in ROOT_TO_FILENAME:
        print(f"error: unknown bass note '{args.bass}'.", file=sys.stderr)
        return 1

# Pass bass to fetch and render calls
for root in roots:
    for chord_type in chord_types:
        text = fetch_chord_file(root, chord_type, force=args.refresh, bass=args.bass)
        if text is None:
            continue
        shapes = parse_chord_file(root, chord_type, text)
        valid = [s for s in shapes if is_valid_shape(s)]
        if valid:
            output_lines.append(
                render_chord_group(root, chord_type, valid, bass=args.bass)
            )
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_cli.py -v 2>&1 | tail -20
```

- [ ] **Step 5: Commit**

```bash
git add smallcaged/__main__.py tests/test_cli.py
git commit -m "feat: add --bass/-b CLI flag"
```

---

### Task 4: Regenerate output files with slash chords

**Files:**
- Regenerate: `all_shapes.txt`, `all_shapes_dotted.txt`, `all_major_minor_shapes.txt`, `all_major_minor_shapes_dotted.txt`

- [ ] **Step 1: Write and run generation script**

```bash
python -c "
from smallcaged.fetcher import CHORD_TYPES, BASS_NOTES, fetch_chord_file
from smallcaged.filter import is_valid_shape
from smallcaged.parser import parse_chord_file
from smallcaged.render import render_chord_group

ROOTS = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def gen(types, dotted, bass_notes=None):
    out = []
    for root in ROOTS:
        for ct in types:
            if bass_notes:
                for bn in bass_notes:
                    text = fetch_chord_file(root, ct, bass=bn)
                    if text:
                        shapes = parse_chord_file(root, ct, text)
                        valid = [s for s in shapes if is_valid_shape(s)]
                        if valid:
                            out.append(render_chord_group(root, ct, valid, dotted=dotted, bass=bn))
            else:
                text = fetch_chord_file(root, ct)
                if text:
                    shapes = parse_chord_file(root, ct, text)
                    valid = [s for s in shapes if is_valid_shape(s)]
                    if valid:
                        out.append(render_chord_group(root, ct, valid, dotted=dotted))
    return '\n'.join(out)

open('all_shapes.txt', 'w').write(gen(CHORD_TYPES, dotted=False) + '\n' + gen(['', 'm'], dotted=False, bass_notes=BASS_NOTES))
open('all_shapes_dotted.txt', 'w').write(gen(CHORD_TYPES, dotted=True) + '\n' + gen(['', 'm'], dotted=True, bass_notes=BASS_NOTES))
open('all_major_minor_shapes.txt', 'w').write(gen(['', 'm'], dotted=False) + '\n' + gen(['', 'm'], dotted=False, bass_notes=BASS_NOTES))
open('all_major_minor_shapes_dotted.txt', 'w').write(gen(['', 'm'], dotted=True) + '\n' + gen(['', 'm'], dotted=True, bass_notes=BASS_NOTES))
print('done')
" 2>&1
```

- [ ] **Step 2: Run tests — expect PASS**

```bash
python -m pytest tests/ -q
```

- [ ] **Step 3: Commit**

```bash
git add all_shapes.txt all_shapes_dotted.txt all_major_minor_shapes.txt all_major_minor_shapes_dotted.txt
git commit -m "feat: regenerate with slash chords"
git push
```
