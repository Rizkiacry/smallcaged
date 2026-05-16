import pytest
from smallcaged.filter import (
    is_valid_shape,
    rule_fits_5_fret_window,
    rule_no_duplicate_frets,
    rule_no_muted_gaps,
    rule_wxyz_finger_combo,
)


def test_rule1_passes_distinct_frets():
    shape = (-1, 3, 2, 0, 1, 0)
    assert rule_no_duplicate_frets(shape) is True


def test_rule1_fails_duplicate_frets():
    shape = (-1, -1, 10, 9, 8, 8)
    assert rule_no_duplicate_frets(shape) is False


def test_rule1_open_strings_ignored():
    shape = (-1, 3, 2, 0, 1, 0)
    assert rule_no_duplicate_frets(shape) is True


def test_rule1_all_muted():
    shape = (-1, -1, -1, -1, -1, -1)
    assert rule_no_duplicate_frets(shape) is True


def test_rule1_mixed_duplicate():
    shape = (8, 7, 5, 5, -1, 8)
    assert rule_no_duplicate_frets(shape) is False


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
    shape = (-1, 6, 5, 3, 4, -1)  # frets 3,4,5,6 fit window 3-6
    assert rule_fits_5_fret_window(shape) is True


def test_rule3_w_y_z():
    shape = (8, 7, 5, -1, -1, -1)  # frets 5,7,8 in window 5-8 → w,y,z
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_w_y():
    shape = (-1, -1, 9, -1, 7, -1)  # frets 7,9 in window 7-10 → w,y
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_x_z():
    shape = (-1, -1, 8, -1, 6, -1)  # frets 6,8 in window 5-8 → x,z
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_x_y():
    shape = (-1, -1, 9, -1, 8, -1)  # frets 8,9 in window 7-10 → x,y
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_w_x_z():
    shape = (8, 6, 5, -1, -1, -1)  # frets 5,6,8 in window 5-8 → w,x,z
    assert rule_wxyz_finger_combo(shape) is True


def test_rule3_w_x_y_not_allowed():
    shape = (-1, 3, 2, 0, 1, 0)  # frets 1,2,3 in window 1-4 → w,x,y
    assert rule_wxyz_finger_combo(shape) is False


def test_rule3_w_x_y_z_not_allowed():
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


def test_composite_valid_shape():
    shape = (8, 7, 5, -1, -1, -1)
    assert is_valid_shape(shape) is True


def test_composite_invalid_rule1():
    shape = (-1, -1, 10, 9, 8, 8)
    assert is_valid_shape(shape) is False


def test_composite_invalid_rule2():
    shape = (-1, 3, 2, 0, 5, 0)
    assert is_valid_shape(shape) is False


def test_composite_invalid_rule3():
    shape = (-1, 3, 2, 0, 1, 0)
    assert is_valid_shape(shape) is False


def test_composite_invalid_rule4():
    shape = (8, 7, 5, 0, -1, 0)
    assert is_valid_shape(shape) is False
