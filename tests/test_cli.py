from smallcaged.__main__ import main

def test_cli_bass_flag():
    rc = main(["-r", "C", "-c", "m", "-b", "G#"])
    assert rc == 0

def test_cli_bass_flag_invalid_note():
    rc = main(["-r", "C", "-c", "m", "-b", "X"])
    assert rc == 1
