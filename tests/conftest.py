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
