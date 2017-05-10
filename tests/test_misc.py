import unittest
import neurokit as nk



class Test(unittest.TestCase):


    def test_BMI(self):
        self.assertEqual(round(nk.BMI(182, 70, 27, "m")['BMI_old'], 2), 21.13)

if __name__ == '__main__':
    unittest.main()