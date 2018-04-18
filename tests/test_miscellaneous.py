import unittest
import neurokit as nk
import pandas as pd


class TestMiscellaneous(unittest.TestCase):

    def setUp(self):
        pass

    def test_find_following_duplicates(self):
        array = ["a","a","b","a","a","a","c","c","b","b"]
        first = nk.find_following_duplicates(array)[0]
        self.assertTrue(first)

    def test_Time(self):
        clock = nk.Time()
        time_passed = clock.get()
        self.assertIsInstance(time_passed, float)

    def test_find_closest_in_list(self):
        closest1 = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2], strictly=True)
        closest2 = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2], strictly=False)
        self.assertEqual(closest1, closest2)

    def tearDown(self):
        pass


