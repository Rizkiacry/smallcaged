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
    def fake_fetch(root, chord_type, cache_dir=None, force=False, bass=None):
        if root == "C" and chord_type == "":
            return SAMPLE_CHORD_FILE
        return None

    monkeypatch.setattr("smallcaged.__main__.fetch_chord_file", fake_fetch)


def test_cli_runs_and_filters_properly(mock_fetcher, capsys):
    exit_code = main(["--root", "C"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "8 7 5 x x x" in captured.out
    assert "x x 10 9 8 8" not in captured.out
    assert "x 3 2 0 1 0" not in captured.out
    assert "x 3 2 0 5 0" not in captured.out


def test_cli_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()
