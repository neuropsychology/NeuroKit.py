import sklearn
import pandas as pd
import neurokit as nk
import numpy as np
import seaborn as sns

ecg = pd.read_csv("data_test_ecg.csv")["ECG"]

ecg.index = pd.date_range(pd.datetime.today(), periods=len(ecg), freq="ms")
ecg = ecg.resample("5L").mean()
sampling_rate=200

heartbeats = nk.ecg_process(ecg, sampling_rate=sampling_rate)["ECG"]["Cardiac_Cycles"]

quality = ecg_signal_quality(heartbeats, 200)