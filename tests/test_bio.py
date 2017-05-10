import unittest
import os
import neurokit as nk



class Test(unittest.TestCase):

    def test_read_acqknowledge(self):
        # Read data
        df = nk.read_acqknowledge(os.getcwd() + r"/tests/test_bio_data.acq")
        # Resample to 100Hz
        df = df.resample("10L").mean()
        df.columns = ['ECG', 'EDA', 'PPG', 'Photosensor', 'RSP']
        # Check length
        self.assertEqual(len(df), 35645)
        return(df)

    def test_bio_process(self):
        df = self.test_read_acqknowledge()
        bio = nk.bio_process(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"], sampling_rate=100, add=df["Photosensor"])
        self.assertEqual(len(bio), 3)
        self.assertEqual(len(bio["ECG"]["R_Peaks"]), 499)
        self.assertEqual(len(bio["EDA"]["SCR_Onsets"]), 5)
        return(bio)


if __name__ == '__main__':
    unittest.main()