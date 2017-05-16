import sklearn
import pandas as pd
import neurokit as nk
import numpy as np
import seaborn as sns

ecg = pd.read_csv("data_test_ecg.csv")["ECG"]


ecg = nk.ecg_process(ecg)["ECG"]
heartbeats = ecg["Cardiac_Cycles"]
#heartbeats.index = pd.date_range(pd.datetime.today(), periods=600, freq="ms")
#model, heartbeats = nk.ecg_classify_heartbeats(heartbeats)