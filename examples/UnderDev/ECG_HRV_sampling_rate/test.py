# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import hrv
import scipy
import matplotlib.pyplot as plt

# window comparison
df = nk.read_acqknowledge('long.acq')
df = nk.ecg_process(df['ECG, X, RSPEC-R'])
rri = df["ECG"]["RR_Intervals"]


df_vlf = {}
df_lf = {}
df_hf = {}
df_tp = {}


vlf = []
lf = []
hf = []
total_power = []
length = []
for i in range(61, 1000):
    length.append(i)
    vlf.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i)["VLF"])
    lf.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i)["LF"])
    hf.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i)["HF"])
    total_power.append(ecg_hrv(rri, sampling_rate=1000, segment_length=i)["Total_Power"])

df_vlf[detrend] = vlf
df_lf[detrend] = lf
df_hf[detrend] = hf
df_tp[detrend] = total_power

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



p = np.polynomial.Polynomial.fit(df_hf.index, df_hf["linear"], 2)
df_hf.plot()
plt.plot(*p.linspace(1000))

p = np.polynomial.Polynomial.fit(df_lf.index, df_lf["linear"], 2)
df_lf.plot()
plt.plot(*p.linspace(1000))

p = np.polynomial.Polynomial.fit(df_vlf.index, df_vlf["linear"], 2)
df_vlf.plot()
plt.plot(*p.linspace(1000))

p = np.polynomial.Polynomial.fit(df_vlf.index, df_vlf["linear"], 2)
df_vlf.plot()
plt.plot(*p.linspace(1000))
