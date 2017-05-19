# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import biosppy
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df = df.loc[5000:10000]

sampling_rate=1000
df = nk.bio_process(ecg=df["ECG"], sampling_rate=sampling_rate)
ecg = df["df"]["ECG_Filtered"]
rpeaks = df["ECG"]["R_Peaks"]


ecg_waves = ecg_wave_detector(ecg, rpeaks)
systole = ecg_systole(ecg, rpeaks, ecg_waves["T_Waves"])
df["df"]["Systole"] = systole

df["df"].plot()
