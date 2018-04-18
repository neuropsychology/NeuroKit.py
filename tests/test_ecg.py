import unittest
import neurokit as nk
import pandas as pd


class TestEcg(unittest.TestCase):

    def setUp(self):
        self.ecg = nk.ecg_simulate(duration=60, sampling_rate=1000, bpm=60, noise=0.01)

    def test_ecg_simulate(self):
        self.assertEqual(len(self.ecg), 60000)

    def test_ecg_process(self):
        ecg_processed = nk.ecg_process(self.ecg, rsp=None, sampling_rate=1000, quality_model=None)
        self.assertAlmostEqual(ecg_processed["df"]["Heart_Rate"].mean(), 60.0, places=1)

    def tearDown(self):
        pass


