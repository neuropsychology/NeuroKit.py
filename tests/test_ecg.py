import unittest
import neurokit as nk

class TestEcg(unittest.TestCase):

    def setUp(self):
        ecg = nk.ecg_simulate(duration=10, sampling_rate=1000, bpm=60, noise=0.01)

    def test_(self):
        pass

    def test_attack(self):
        pass

    def tearDown(self):
        pass