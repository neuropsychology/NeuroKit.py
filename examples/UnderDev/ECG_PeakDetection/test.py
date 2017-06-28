# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import biosppy
import matplotlib.pyplot as plt
import scipy
#df = pd.read_csv('data.csv')
#df = df.loc[5000:10000]
#
#sampling_rate=1000
#df = nk.bio_process(ecg=df["ECG"], sampling_rate=sampling_rate)
#ecg = df["df"]["ECG_Filtered"]
#rpeaks = df["ECG"]["R_Peaks"]
#
#
#ecg_waves = ecg_wave_detector(ecg, rpeaks)
#systole = ecg_systole(ecg, rpeaks, ecg_waves["T_Waves"])
#df["df"]["Systole"] = systole
#
#df["df"].plot()



df = pd.read_csv('data.csv')
df = df.loc[10000:20000]


sampling_rate=1000
df = nk.bio_process(ecg=df["ECG"], sampling_rate=sampling_rate)

#df["df"]["ECG_Filtered"].plot()

rri = df["ECG"]['RR_Intervals']
rpeaks = df["ECG"]['R_Peaks']




# HRV Test

# Initialize empty dict
hrv = {}

# Preprocessing
# ==================
# Basic resampling to 1Hz to standardize the scale
rri = rri/sampling_rate
rri = rri.astype(float)


# Artifact detection - Statistical
for index, rr in enumerate(rri):
    # Remove RR intervals that differ more than 25% from the previous one
    if rri[index] < rri[index-1]*0.75:
        rri[index] = np.nan
    if rri[index] > rri[index-1]*1.25:
        rri[index] = np.nan

# Artifact detection - Physiological (http://emedicine.medscape.com/article/2172196-overview)
rri = pd.Series(rri)
rri[rri < 0.6] = np.nan
rri[rri > 1.3] = np.nan

# Artifact treatment
hrv["n_Artifacts"] = pd.isnull(rri).sum()/len(rri)


artifacts_indices = rri.index[rri.isnull()]  # get the indices of the outliers
rri = rri.drop(artifacts_indices)  # remove the artifacts

# resampling RRIbeat signal in order to make it a function of time (not a function of beat)

beat_time = rpeaks[1:] # the time (in samples) at which each beat occured (and thus the RR intervals occured) starting from the 2nd beat
beat_time = np.delete(beat_time, artifacts_indices) #delete also the outlier beat moments
beat_time = beat_time/sampling_rate  # the time (in sec) at which each beat occured, starting from the 2nd beat
beat_time = beat_time-beat_time[0] #offseting in order to start from 0 sec



# fit a 3rd degree spline in the RRIbeat data. s=0 guarantees that it will pass through ALL the given points
spline = scipy.interpolate.splrep(x=beat_time, y=rri, k=3, s=0)

# RR intervals indexed per time
rri_new = scipy.interpolate.splev(x=np.arange(0, beat_time[-1], 1/sampling_rate), tck=spline, der=0)



data = df["df"][["ECG_Filtered", "Heart_Rate"]].copy()
data["ECG_HRV"] = np.nan
data["ECG_HRV"].ix[rpeaks[0]+1:rpeaks[0]+len(rri_new)] = rri_new

nk.z_score(data).plot()
