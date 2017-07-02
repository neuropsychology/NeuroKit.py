import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib.pyplot as plt
import scipy
import biosppy

df = pd.read_csv('normal_ECG.csv')
df = df.loc[10000:50000].reset_index(drop=True)  # Select 10s of signal

sampling_rate=1000


df = nk.rsp_process(rsp=df["RSP"], sampling_rate=sampling_rate)
#df = nk.bio_process(ecg=df["ECG"], sampling_rate=sampling_rate)


#
#
#rpeaks = biosppy.ecg.ecg(df["ECG"], sampling_rate, False)['rpeaks']
#
#
#from numpy import arange, cumsum, logical_and
#from scipy.signal import welch
#from scipy.interpolate import splrep, splev
#
#
#
#rri = np.diff(rpeaks)
#
##Create time array
#t = cumsum(rri) / 1000.0
#t -= t[0]
#
##Evenly spaced time array (4Hz)
#tx = np.arange(t[0], np.array(t)[-1], 1.0 / 4)
#
##Interpolate RRi serie
#tck = scipy.interpolate.splrep(t, rri, s=0)
#rrix = scipy.interpolate.splev(tx, tck, der=0)
#
##pd.Series(rrix).plot()
##RRi.plot()
#
#
##len(RRi)/len(rrix)
##Number os estimations
#P = int((len(tx) - 256 / 128)) + 1
##
###PSD with Welch's Method
#Fxx, Pxx = scipy.signal.welch(rrix, fs=4, window="hanning", nperseg=256, noverlap=128, detrend="linear")
#
##Plot the PSD
#plt.plot(Fxx, Pxx)
#plt.xlabel("Frequency (Hz)")
#plt.ylabel(r"PSD $(ms^ 2$/Hz)")
#plt.title("PSD")

# GO
#========================






#
#
## Initialize empty dict
#hrv = {}
#
## Preprocessing
## ==================
## Extract RR intervals (RRis)
#RRis = np.diff(rpeaks)
## Basic resampling to 1Hz to standardize the scale
#RRis = RRis/sampling_rate
#RRis = RRis.astype(float)
#
#
## Artifact detection - Statistical
#for index, rr in enumerate(RRis):
#    # Remove RR intervals that differ more than 25% from the previous one
#    if RRis[index] < RRis[index-1]*0.75:
#        RRis[index] = np.nan
#    if RRis[index] > RRis[index-1]*1.25:
#        RRis[index] = np.nan
#
## Artifact detection - Physiological (http://emedicine.medscape.com/article/2172196-overview)
#RRis = pd.Series(RRis)
#RRis[RRis < 0.6] = np.nan
#RRis[RRis > 1.3] = np.nan
#
## Artifacts treatment
#hrv["n_Artifacts"] = pd.isnull(RRis).sum()/len(RRis)
#artifacts_indices = RRis.index[RRis.isnull()]  # get the artifacts indices
#RRis = RRis.drop(artifacts_indices)  # remove the artifacts
#
## Convert to continuous RR interval (RRi)
#beats_times = rpeaks[1:]/sampling_rate  # the time (in sec) at which each beat occured starting from the 2nd beat
#beats_times = np.delete(beats_times, artifacts_indices)  # delete also the artifact beat moments
#try:
#    RRi = discrete_to_continuous(RRis, beats_times, sampling_rate)  # Interpolation using 3rd order spline
#except TypeError:
#    print("NeuroKit Warning: ecg_hrv(): Sequence too short to compute HRV.")
#    return(hrv)
#
#
## Check
#df["RR_Interval"] = np.nan
#df["RR_Interval"].ix[rpeaks[1]:rpeaks[1]+len(RRi)] = RRi
#
#
#nk.plot_events_in_signal(nk.z_score(df), rpeaks)

## resampling rri signal in order to make it a function of time
#beat_time = rpeaks[1:]  # the time (in samples) at which each beat occured (and thus the RR intervals occured) starting from the 2nd beat
#beat_time = np.delete(beat_time, artifacts_indices)  # delete also the artifact beat moments
#beat_time = beat_time/sampling_rate  # the time (in sec) at which each beat occured, starting from the 2nd beat
#beat_time = beat_time-beat_time[0]  # offseting in order to start from 0 sec
#
#
## fit a 3rd degree spline on the beat_time data.
#spline = scipy.interpolate.splrep(x=beat_time, y=rri, k=3, s=0)  # s=0 guarantees that it will pass through ALL the given points
#
## Get the RR intervals indexed per time
#rri_new = scipy.interpolate.splev(x=np.arange(0, beat_time[-1], 1/sampling_rate), tck=spline, der=0)
#
#

# CHECK
#==============

# plotting
#plt.figure(figsize=(20, 3), dpi=100)
#plt.scatter(np.arange(rri_new.shape[0]), rri_new,s=1)
#plt.grid(True)
#plt.title('RRI indexed per beat')
#plt.ylabel('RR interval duration (sec)')
#plt.xlabel('#beat')
#plt.tight_layout()
#plt.show()

#plt.figure(figsize=(20, 3), dpi=100)
#plt.plot(rri,'b-',linewidth=0.5)
#plt.grid(True)
#plt.title('Resampled RRI indexed per time')
#plt.ylabel('RR interval duration (sec)')
#plt.xlabel('Time (sec)')
#plt.tight_layout()
#plt.show()



#data = df["df"][["ECG_Filtered", "Heart_Rate"]].copy()
#data["ECG_HRV"] = np.nan
#data["ECG_HRV"].ix[rpeaks[1]+1:rpeaks[1]+len(rri_new)] = rri_new
#
##  nk.z_score(data).plot()
#nk.plot_events_in_signal(nk.z_score(data), rpeaks)
#
#biosppy.ecg.ecg(data["ECG_Filtered"], 1000)
