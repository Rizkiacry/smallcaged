import pathlib
import tempfile

import pytest
from smallcaged.fetcher import (
    BASS_NOTES,
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
    assert "" in CHORD_TYPES
    assert "m" in CHORD_TYPES
    assert "7" in CHORD_TYPES
    assert "maj7" in CHORD_TYPES


def test_bass_notes_list():
    assert "A" in BASS_NOTES
    assert "G#" in BASS_NOTES
    assert "C" not in BASS_NOTES
    assert len(BASS_NOTES) == 11


def test_build_url_with_bass():
    assert build_url("C", "", bass="G#").endswith("C.Gsharp.txt")
    assert build_url("C", "m", bass="A").endswith("Cm.A.txt")
    assert build_url("C", "m").endswith("Cm.txt")


def test_get_cache_path_with_bass(tmp_path):
    assert get_cache_path("C", "", bass="A", cache_dir=tmp_path).name == "C.A.txt"


def test_fetch_chord_file_accepts_bass(tmp_path):
    r = fetch_chord_file("C", "m", bass="A", cache_dir=tmp_path)
    assert r is None or isinstance(r, str)
