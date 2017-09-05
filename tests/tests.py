import nose
import matplotlib


def test_mad():
    nose.tools.assert_equals(nk.mad([1, 2, 3, 4, 5, 6, 7]), 2.0)
