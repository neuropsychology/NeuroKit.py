import pytest
import doctest
import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib



run_tests_in_local = False


#==============================================================================
# STATISTICS
#==============================================================================
def test_mad():
    assert nk.mad([1, 2, 3, 4, 5, 6, 7]) == 2.0

def test_z_score():
    raw_scores = [1, 1, 5, 2, 1]
    z = nk.z_score(raw_scores)
    assert int(z.values[3]) == 0

def test_find_outliers():
    outliers = nk.find_outliers([1, 2, 1, 5, 666, 4, 1 ,3, 5])
    assert outliers[4] == True

def test_normal_range():
    bottom, top = nk.normal_range(mean=100, sd=15, treshold=2)
    assert bottom == 70

#==============================================================================
# ROUTINES
#==============================================================================
def test_compute_dprime():
    parameters = nk.compute_dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)
    assert np.round(parameters["bppd"], 2) == -0.5

def test_compute_BMI():
    assert round(nk.compute_BMI(182, 70, 27, "m")['BMI_old'], 2) == 21.13

def test_compute_interoceptive_accuracy():
    assert nk.compute_interoceptive_accuracy(5, 3) == 0.5

#==============================================================================
# Plots
#==============================================================================
#def test_plot_polarbar():
#    fig = nk.plot_polarbar([1, 2, 3])
#    nose.tools.assert_is_instance(fig, matplotlib.figure.Figure)



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
    closest = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2])
    assert closest ==  2



if __name__ == '__main__':
    pytest.main()
    doctest.testmod()
