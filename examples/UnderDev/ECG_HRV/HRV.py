import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib.pyplot as plt
import scipy
import biosppy
import mne


df = pd.read_csv('normal_ECG.csv')
df = df.loc[10000:100000].reset_index(drop=True)  # Select 10s of signal
sampling_rate=1000
ecg=df["ECG"]
rpeaks = dict(biosppy.ecg.ecg(ecg, 100, show=False))["rpeaks"]

#rsp = pd.Series(dict(biosppy.resp.resp(rsp, 100, show=False))["filtered"])


#nk.plot_events_in_signal(rsp, rsp_onsets)
#nk.z_score(df).plot()

