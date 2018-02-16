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
    assert round(nk.compute_BMI(182, 25, 27, "f")['BMI_old'], 2) == 7.55

def test_compute_interoceptive_accuracy():
    assert nk.compute_interoceptive_accuracy(5, 3) == 0.5
    assert list(nk.compute_interoceptive_accuracy([5,3], [3, 5])) == [0.5, 0.5]
def test_staircase():
    staircase = nk.staircase()
    for trial in range(200):
        signal = staircase.predict_next_value()
        if signal > 50:
            response = 1
        else:
            response = 0
        staircase.add_response(response=response, value=signal)
    treshold = staircase.get_treshold()
    assert 49 <= treshold <= 51

    data = staircase.get_data()
    assert len(data) == 200

    data_fig = staircase.diagnostic_plot()
    assert len(data_fig) == 200

#==============================================================================
# Plots
#==============================================================================
def test_plot_polarbar():
    fig = nk.plot_polarbar([1, 2, 3],
                           labels=["A", "B", "C"],
                           distribution_means=[1.5, 1.5, 1.5],
                           distribution_sds=[0.5, 0.25, 0.65])
    assert isinstance(fig, matplotlib.figure.Figure)




if __name__ == '__main__':
    pytest.main()
    doctest.testmod()




