import unittest
import os
import numpy as np
import pandas as pd
import neurokit as nk

run_tests_in_local = False

class Test(unittest.TestCase):
#==============================================================================
# BIO
#==============================================================================
    def test_read_acqknowledge(self):

        if run_tests_in_local is False:
            data_path = os.getcwd() + r"/tests/data/test_bio_data.acq"  # If running from travis
        else:
            data_path = "data/test_bio_data.acq"  # If running in local

        # Read data
        df = nk.read_acqknowledge(data_path)
        # Resample to 100Hz
        df = df.resample("10L").mean()
        df.columns = ['ECG', 'EDA', 'PPG', 'Photosensor', 'RSP']
        # Check length
        self.assertEqual(len(df), 35645)
        return(df)

    def test_bio_process(self):

        df = self.test_read_acqknowledge()

        if run_tests_in_local is False:  # If travis
            ecg_quality_model = os.getcwd() + r"/neurokit/materials/heartbeat_classification.model"
        else:  # If local
            ecg_quality_model = "default"

        bio = nk.bio_process(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"], sampling_rate=100, add=df["Photosensor"], ecg_quality_model=ecg_quality_model, age=24, sex="m", position="supine")

        self.assertEqual(len(bio), 4)
        return(bio)


    def test_hrv(self):

        bio = self.test_bio_process()

        self.assertEqual(len(bio["ECG"]["R_Peaks"]), 499)
        self.assertEqual(len(bio["EDA"]["SCR_Onsets"]), 5)

#==============================================================================
# SIGNAL
#==============================================================================
# Not working for some reasons...
#    def test_complexity(self):
#        np.random.seed(666)
#        signal = np.sin(np.log(np.random.sample(100)))
#        complexity = nk.complexity(signal, lyap_r=False, lyap_e=False)
#        self.assertEqual("%.2f" %complexity["DFA"], "0.64")
#        self.assertEqual("%.2f" %complexity["Fractal_Dimension"], '1.13')
#        self.assertEqual("%.2f" %complexity["Hurst"], '0.60')
#        self.assertEqual("%.2f" %complexity["Multiscale_Entropy"], '1.70')
#        self.assertEqual("%.2f" %complexity["Sample_Entropy_Chebychev"], '2.07')
#        self.assertEqual("%.2f" %complexity["Sample_Entropy_Euclidean"], '2.25')
#        self.assertEqual("%.2f" %complexity["Shannon_Entropy"], '6.64')

    def test_find_events(self):
        signal = [0]*30 + [1]*5 + [0]*30 + [1]*5 +[0]*30
        events = nk.find_events(np.array(signal))
        self.assertEqual(len(events["onsets"]), 2)

    def test_create_epochs(self):
        signal = [0]*30 + [1]*5 + [0]*30 + [1]*5 +[0]*30
        events = nk.find_events(np.array(signal))
        data = nk.create_epochs(pd.DataFrame({"Signal": signal}), events_onsets=events["onsets"], duration=5)
        self.assertEqual(len(data), 2)
#==============================================================================
# MISCELLANEOUS
#==============================================================================
    def test_BMI(self):
        self.assertEqual(round(nk.BMI(182, 70, 27, "m")['BMI_old'], 2), 21.13)

    def test_mad(self):
        self.assertEqual(nk.mad([1, 2, 3, 4, 5, 6, 7]), 2.0)

    def test_find_following_duplicates(self):
        array = ["a","a","b","a","a","a","c","c","b","b"]
        first = nk.find_following_duplicates(array)[0]
        self.assertEqual(first, True)

    def test_find_closest_in_list(self):
        closest = nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2])
        self.assertEqual(closest, 2)

    def test_Time(self):
        clock = nk.Time()
        time_passed = clock.get()
        self.assertEqual(isinstance(time_passed, float), True)

if __name__ == '__main__':
    unittest.main()
