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
