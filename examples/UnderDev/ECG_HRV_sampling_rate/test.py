# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import hrv
import scipy


# window comparison
df = nk.read_acqknowledge('long.acq')
df = nk.ecg_process(df['ECG, X, RSPEC-R'])
rri = df["ECG"]["RR_Intervals"]


df_vlf = {}
df_lf = {}
df_hf = {}
df_tp = {}

for window in ["boxcar", "triang", "blackman", "hamming", "hann", "bartlett", "flattop", "parzen", "bohman", "blackmanharris", "nuttall", "barthann"]:

    vlf = []
    lf = []
    hf = []
    total_power = []
    length = []
#    for i in range(50, len(df["ECG"]["RR_Intervals"])):
    for i in range(50, len(rri)):
        length.append(i)
        vlf.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i, window=window)["VLF"])
        lf.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i, window=window)["LF"])
        hf.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i, window=window)["HF"])
        total_power.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i, window=window)["Total_Power"])

    df_vlf[window] = vlf
    df_lf[window] = lf
    df_hf[window] = lf
    df_tp[window] = total_power

df_vlf = pd.DataFrame.from_dict(df_vlf)
df_vlf.index = length
df_lf = pd.DataFrame.from_dict(df_lf)
df_lf.index = length
df_hf = pd.DataFrame.from_dict(df_hf)
df_hf.index = length
df_tp = pd.DataFrame.from_dict(df_tp)
df_tp.index = length

df_vlf.plot()
df_lf.plot()
df_hf.plot()
df_tp.plot()