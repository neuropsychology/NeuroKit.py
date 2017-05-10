import unittest

import neurokit as nk




class TestMethods(unittest.TestCase):
    def test_BMI(self):
        self.assertEqual(round(nk.BMI(182, 70, 27, "m")["BFP"], 2), 15.37)


if __name__ == '__main__':
    unittest.main()