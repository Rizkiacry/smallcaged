# smallcaged — Guitar Chord Shape Filter CLI

## Problem

Howard Wright's Big List of Guitar Chords contains thousands of chord shapes, but many are impractical for actual guitar playing. This CLI filters them by 4 physical-playability criteria, outputting only the shapes that a human hand can reasonably form.

## Data Source

- Base URL: `https://www.hakwright.co.uk/guitarchords/dictionary/`
- File naming: `{root}{chord_type}.txt`
  - Root notes: `C`, `Csharp`, `D`, `Dsharp`, `E`, `F`, `Fsharp`, `G`, `Gsharp`, `A`, `Asharp`, `B`
  - Chord types: ``, `m`, `sus2`, `sus4`, `add2`, `add9`, `add4`, `madd2`, `madd9`, `madd4`, `add2add4`, `madd2add4`, `aug`, `dim`, `dim7`, `5`, `6`, `m6`, `6.9`, `m6.9`, `6.7`, `m6.7`, `maj6.7`, `7`, `m7`, `maj7`, `7sus4`, `7sus2`, `7add4`, `m7add4`, `9`, `m9`, `maj9`, `9sus4`, `11`, `m11`, `maj11`, `13`, `m13`, `maj13`, `13sus4`, `mmaj7`, `mmaj9`, `7sharp9`, `7b9`, `7sharp5`, `7b5`, `m7sharp5`, `m7b5`, `maj7sharp5`, `maj7b5`, `9sharp5`, `9b5`
  - Slash chords: `{root_filename}.{bass_filename}.txt` and `{root_filename}m.{bass_filename}.txt` for all 11 bass notes
  - Bass notes: A, A#, B, C#, D, D#, E, F, F#, G, G# (natural/sharp only, input accepts `#`)
  - URL construction with bass: `{root_filename}{chord_type}.{bass_filename}.txt`
  - Example: `C#` root + `""` chord + `G#` bass → `Csharp.Gsharp.txt` (C# major / G# bass)
  - Example: `C` root + `m` chord + `A` bass → `Cm.A.txt` (C minor / A bass)
- File format: Sections labeled `MOVEABLE BAR CHORD SHAPES`, `OTHER MOVEABLE SHAPES`, `CHORD SHAPES USING OPEN STRINGS`. Each shape is one line with 6 space-separated tokens (numbers or `x`), representing strings 6 (low E) to 1 (high E).

## Filter Rules

### Rule 1: No duplicate frets

No two non-muted strings may share the same fret number. Open strings (0) are excluded from this check.

- PASS: `x 3 2 0 1 0` (frets 3,2,1 are all distinct)
- FAIL: `x x 10 9 8 8` (strings 1 and 2 both on fret 8)

### Rule 2: 5-fret section

All non-muted, non-open frets must fit entirely within at least one of these 5-section (4-fret span) windows:

`(1,4), (3,6), (5,8), (7,10), (9,12), (11,14)`

- PASS: `8 7 5 x x x` (frets 5,7,8 all within window 5-8)
- FAIL: `x 3 2 0 5 0` (fret 2 outside window 3-6, fret 5 outside window 1-4)

### Rule 3: wxyz finger combination

Map the 4 fretting fingers to a 4-fret block: `w = min fret`, `x = w+1`, `y = w+2`, `z = w+3`. The set of used fingers (any fret position occupied) must match exactly one of:

`{w-y, w-y-z, x-z, x-y, w-x-z}`

- PASS: `8 7 5 x x x` → frets 5,7,8 → w=5,x=6,y=7,z=8 → used: w,y,z → w-y-z ✓
- FAIL: `x 3 2 0 1 0` → frets 1,2,3 → w=1,x=2,y=3,z=4 → used: w,x,y → w-x-y ✗

### Rule 4: No muted string gaps

When scanning strings 6→1 (left to right), if an `x` appears, all subsequent strings must also be `x`. No re-entrant muted strings.

- PASS: `x x 11 10 x x` (muted contiguous from string 4)
- PASS: `8 7 5 x x x` (muted strings are at the end)
- FAIL: `8 7 5 0 x 0` (string 2 is x, string 1 is 0)

## Architecture

```
smallcaged/
├── smallcaged.py     — CLI entry point (argparse)
├── fetcher.py        — download + cache Howard's .txt files
├── parser.py         — parse .txt format to list[Shape]
├── filter.py         — apply 4 rules, return valid shapes
├── render.py         — format shapes for terminal output
└── tests/            — unit tests
```

### Data flow

```
URL (root+chord_type+[bass]) → fetcher.py → cache (~/.cache/smallcaged/)
                        ↓
                  parser.py → list[Shape]
                        ↓
                  filter.py → list[Shape] (filtered)
                        ↓
                  render.py → stdout (with bass in header)
```

### Shape type

```python
# 6 elements: one per string, low E (idx 0) to high E (idx 5)
# Values: 0-24 (fret number) or -1 (muted/x)
Shape = tuple[int, int, int, int, int, int]
```

## CLI Interface

```
smallcaged [--chord CHORD] [--root ROOT] [--bass BASS] [--output FILE] [--refresh]
```

- `--chord CHORD` — filter by chord type (e.g. `m`, `7`, `maj7`). Default: all.
- `--root ROOT` — filter by root note (e.g. `C`, `G#`). Default: all 12.
- `--bass BASS` — bass note for slash chords (e.g. `A`, `G#`). Default: none (no slash).
- `--output FILE` — save to file. Default: stdout.
- `--refresh` — bypass cache, re-download.

When `-b` is provided, URL becomes `{root_filename}{chord_type}.{bass_filename}.txt`.
Display header shows slash notation: `=== C#/G# ===` for major slash, `=== C m/A ===` for minor slash.

Output: one section per chord, each shape on its own line labeled with fret positions and a finger-pattern annotation.

## Caching

Cache directory: `~/.cache/smallcaged/`. Each `.txt` file stored with original name. Cache is simple — if file exists, skip download. Use `--refresh` to force re-download. 404s (missing chord files) are silently skipped per root+type combination — not all chord types exist for all roots.

## Output Generation

The `all_shapes*.txt` files are generated by iterating all roots × all chord types. With bass support, also iterate bass notes for chord types `""` and `m` (major and minor slash chords):

```python
BASS_NOTES = ["A", "A#", "B", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
```

Each (root, chord_type, bass) combination generates a URL and fetches/parses/filters independently. Missing files (404) are silently skipped.

## Future Considerations

- Separate `--bass BASS` flag for CLI query; for bulk generation, a BASS_NOTES list drives iteration
- `--fret-range` to filter by position on neck
- Interactive browser companion for fretboard visualization
