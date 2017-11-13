import pytest
import doctest
import numpy as np
import pandas as pd
import neurokit as nk
import os

run_tests_in_local = False




#==============================================================================
# data
#==============================================================================

def test_save_nk():
    obj = [1, 2]
    nk.save_nk_object(obj, filename="myobject")
    obj = nk.read_nk_object("myobject.nk")


def test_get_creation_date():

    if run_tests_in_local is False:
        data_path = os.getcwd() + r"/tests/data/test_bio_data.acq"  # If running from travis
    else:
        data_path = "data/test_bio_data.acq"  # If running in local

    creation_date = nk.find_creation_date(data_path)
    assert isinstance(creation_date, float)

#==============================================================================
# miscellaenous
#==============================================================================
def test_find_following_duplicates():
    array = ["a","a","b","a","a","a","c","c","b","b"]
    first = nk.find_following_duplicates(array)[0]
    assert first == True

def test_Time():
    clock = nk.Time()
    time_passed = clock.get()
    assert isinstance(time_passed, float)

def test_find_closest_in_list():
    closest1 = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2], strictly=True)
    closest2 = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2], strictly=False)
    assert closest1 ==  closest2





if __name__ == '__main__':

    doctest.testmod()
    pytest.main()
