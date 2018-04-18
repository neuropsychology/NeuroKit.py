import unittest
import neurokit as nk
import pandas as pd


class TestComplexity(unittest.TestCase):

    def setUp(self):
        self.signal = nk.ecg_simulate(duration=10, sampling_rate=100, bpm=60, noise=0)

    def test_complexity_entropy_shannon(self):
        shannon = nk.complexity_entropy_shannon(self.signal)
        self.assertAlmostEqual(shannon, 8.81, places=2)

    def test_entropy_multiscale(self):
        mse = nk.complexity_entropy_multiscale(self.signal)
        self.assertAlmostEqual(mse["MSE_AUC"], 6.83, places=1)

    def tearDown(self):
        pass
