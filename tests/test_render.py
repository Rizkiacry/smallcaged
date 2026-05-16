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
