import pytest
import doctest
import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib
import os

run_tests_in_local = True


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

#==============================================================================
# Plots
#==============================================================================
def test_plot_polarbar():
    fig = nk.plot_polarbar([1, 2, 3])
    assert isinstance(fig, matplotlib.figure.Figure)

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






#==============================================================================
# BIO
#==============================================================================
def test_read_acqknowledge():

    if run_tests_in_local is False:
        data_path = os.getcwd() + r"/tests/data/test_bio_data.acq"  # If running from travis
    else:
        data_path = "data/test_bio_data.acq"  # If running in local

    # Read data
    df, sampling_rate = nk.read_acqknowledge(data_path, return_sampling_rate=True)
    # Resample to 100Hz
    df = df.resample("10L").mean()
    df.columns = ['ECG', 'EDA', 'PPG', 'Photosensor', 'RSP']
    # Check length
    assert len(df) == 35645
    return(df)

# ---------------
def test_bio_process():

    df = test_read_acqknowledge()

    if run_tests_in_local is False:  # If travis
        ecg_quality_model = os.getcwd() + r"/neurokit/materials/heartbeat_classification.model"
    else:  # If local
        ecg_quality_model = "default"

    bio = nk.bio_process(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"], sampling_rate=100, add=df["Photosensor"], ecg_quality_model=ecg_quality_model, age=24, sex="m", position="supine")

    assert len(bio) == 4
    return(bio)



if __name__ == '__main__':
    pytest.main()
    doctest.testmod()








#class TestStatistics(unittest.TestCase):
#
##==============================================================================
## STATISTICS
##==============================================================================
#    def test_mad(self):
#        self.assertEqual(nk.mad([1, 2, 3, 4, 5, 6, 7]), 2.0)
#
#    def test_z_score(self):
#        raw_scores = [1, 1, 5, 2, 1]
#        z = nk.z_score(raw_scores)
#        self.assertEqual(int(z.values[3]), 0)
#
#    def test_find_outliers(self):
#        outliers = nk.find_outliers([1, 2, 1, 5, 666, 4, 1 ,3, 5])
#        self.assertEqual(outliers[4], True)
#
#    def test_normal_range(self):
#        bottom, top = nk.normal_range(mean=100, sd=15, treshold=2)
#        self.assertEqual(bottom, 70)
#
##==============================================================================
## ROUTINES
##==============================================================================
#    def test_compute_dprime(self):
#        parameters = nk.compute_dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)
#        self.assertEqual(np.round(parameters["bppd"], 2), -0.5)
#
#    def test_compute_BMI(self):
#        self.assertEqual(round(nk.compute_BMI(182, 70, 27, "m")['BMI_old'], 2), 21.13)
#
#    def test_compute_interoceptive_accuracy(self):
#        self.assertEqual(nk.compute_interoceptive_accuracy(5, 3), 0.5)

#==============================================================================
# Plots
#==============================================================================
#    def test_plot_polarbar(self):
#        fig = nk.plot_polarbar([1, 2, 3])
#        self.assertIsInstance(fig, matplotlib.figure.Figure)

#if __name__ == '__main__':
#    unittest.main()
