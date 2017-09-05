import unittest
import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib

class TestStatistics(unittest.TestCase):

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
        self.assertEqual(outliers[4], True)

    def test_normal_range(self):
        bottom, top = nk.normal_range(mean=100, sd=15, treshold=2)
        self.assertEqual(bottom, 70)

#==============================================================================
# ROUTINES
#==============================================================================
    def test_compute_dprime(self):
        parameters = nk.compute_dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)
        self.assertEqual(np.round(parameters["bppd"], 2), -0.5)

    def test_compute_BMI(self):
        self.assertEqual(round(nk.compute_BMI(182, 70, 27, "m")['BMI_old'], 2), 21.13)

    def test_compute_interoceptive_accuracy(self):
        self.assertEqual(nk.compute_interoceptive_accuracy(5, 3), 0.5)

#==============================================================================
# Plots
#==============================================================================
#    def test_plot_polarbar(self):
#        fig = nk.plot_polarbar([1, 2, 3])
#        self.assertIsInstance(fig, matplotlib.figure.Figure)

if __name__ == '__main__':
    unittest.main()