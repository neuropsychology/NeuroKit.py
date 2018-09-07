import unittest
import neurokit as nk
import pandas as pd
import numpy as np


class TestStatistics(unittest.TestCase):

    def setUp(self):
        pass

    #==============================================================================
    # STATISTICS
    #==============================================================================
    def test_mad(self):
        self.assertEqual(nk.mad([1, 2, 3, 4, 5, 6, 7]), 2.0)

    def test_z_score(self):
        raw_scores = [1, 1, 5, 2, 1]
        z = nk.z_score(raw_scores)
        self.assertEqual(int(z.values[3]), 0)

    def test_find_outliers(self):
        outliers = nk.find_outliers([1, 2, 1, 5, 666, 4, 1 ,3, 5])
        self.assertTrue(outliers[4])

    def test_normal_range(self):
        bottom, top = nk.normal_range(mean=100, sd=15, treshold=2)
        self.assertEqual(bottom, 70)

    #==============================================================================
    # ROUTINES
    #==============================================================================
    def test_compute_dprime(self):
        parameters = nk.compute_dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)
        self.assertEqual(np.round(parameters["bppd"], 2), -0.27)

    def test_compute_BMI(self):
        self.assertEqual(round(nk.compute_BMI(182, 70, 27, "m")['BMI_old'], 2), 21.13)
        self.assertEqual(round(nk.compute_BMI(182, 25, 27, "f")['BMI_old'], 2), 7.55)

    def test_compute_interoceptive_accuracy(self):
        self.assertEqual(nk.compute_interoceptive_accuracy(5, 3), 0.5)
        self.assertEqual(list(nk.compute_interoceptive_accuracy([5,3], [3, 5])), [0.5, 0.5])

    def test_staircase(self):
        staircase = nk.staircase()
        for trial in range(200):
            signal = staircase.predict_next_value()
            if signal > 50:
                response = 1
            else:
                response = 0
            staircase.add_response(response=response, value=signal)
        treshold = staircase.get_treshold()
        self.assertTrue(49 <= treshold <= 51)

        data = staircase.get_data()
        self.assertEqual(len(data), 200)

    def tearDown(self):
        pass



