import unittest

from ..neurokit import *




class Test(unittest.TestCase):
    def test_BMI(self):
        self.assertEqual(round(BMI(182, 70, 27, "m")["BFP"], 2), 15.37)


if __name__ == '__main__':
    unittest.main()