import pathlib
import tempfile

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
    assert "" in CHORD_TYPES
    assert "m" in CHORD_TYPES
    assert "7" in CHORD_TYPES
    assert "maj7" in CHORD_TYPES
