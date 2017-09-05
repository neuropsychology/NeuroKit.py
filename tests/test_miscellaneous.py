import unittest
import numpy as np
import pandas as pd
import neurokit as nk
import os

run_tests_in_local = False


class TestMiscellaenous(unittest.TestCase):

#==============================================================================
# data
#==============================================================================

    def test_save_nk(self):
        obj = [1, 2]
        nk.save_nk_object(obj, filename="myobject")
        obj = nk.read_nk_object("myobject.nk")


    def test_get_creation_date(self):

        if run_tests_in_local is False:
            data_path = os.getcwd() + r"/tests/data/test_bio_data.acq"  # If running from travis
        else:
            data_path = "data/test_bio_data.acq"  # If running in local

        creation_date = nk.get_creation_date(data_path)
        self.assertEqual(isinstance(creation_date, float))

#==============================================================================
# miscellaenous
#==============================================================================
    def test_find_following_duplicates(self):
        array = ["a","a","b","a","a","a","c","c","b","b"]
        first = nk.find_following_duplicates(array)[0]
        self.assertEqual(first, True)

    def test_Time(self):
        clock = nk.Time()
        time_passed = clock.get()
        self.assertEqual(isinstance(time_passed, float))

    def test_find_closest_in_list(self):
        closest = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2])
        self.assertEqual(closest, 2)