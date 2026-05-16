from __future__ import annotations

import pathlib
import urllib.error
import urllib.request

BASE_URL = "https://www.hakwright.co.uk/guitarchords/dictionary"

ROOT_TO_FILENAME: dict[str, str] = {
    "C": "C",
    "C#": "Csharp",
    "Db": "Csharp",
    "D": "D",
    "D#": "Dsharp",
    "Eb": "Dsharp",
    "E": "E",
    "F": "F",
    "F#": "Fsharp",
    "Gb": "Fsharp",
    "G": "G",
    "G#": "Gsharp",
    "Ab": "Gsharp",
    "A": "A",
    "A#": "Asharp",
    "Bb": "Asharp",
    "B": "B",
}

CHORD_TYPES: list[str] = [
    "", "m", "sus2", "sus4", "add2", "add9", "add4", "madd2", "madd9", "madd4",
    "add2add4", "madd2add4", "aug", "dim", "dim7", "5", "6", "m6", "6.9", "m6.9",
    "6.7", "m6.7", "maj6.7", "7", "m7", "maj7", "7sus4", "7sus2", "7add4", "m7add4",
    "9", "m9", "maj9", "9sus4", "11", "m11", "maj11", "13", "m13", "maj13", "13sus4",
    "mmaj7", "mmaj9", "7sharp9", "7b9", "7sharp5", "7b5", "m7sharp5", "m7b5",
    "maj7sharp5", "maj7b5", "9sharp5", "9b5",
]


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
