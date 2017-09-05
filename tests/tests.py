import nose
import doctest


import neurokit as nk

def test_mad():
    nose.tools.assert_equals(nk.mad([1, 2, 3, 4, 5, 6, 7]), 2.0)

if __name__ == '__main__':
    doctest.testmod()