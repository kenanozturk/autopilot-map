from os import path


def test_dummy():
    assert path.isfile("sampledata/dummy.txt")