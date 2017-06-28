import neurokit as nk
import numpy as np
import pandas as pd
import scipy
#df = nk.read_acqknowledge("abnormal_ECG.acq")
#df['ECG, X, RSPEC-R'].plot()


#events = nk.find_events(df["Photosensor"], cut="lower")
#df = nk.create_epochs(df, events["onsets"], duration=events["durations"])[0]



#df["Photosensor"].plot()
#df = nk.ecg_process(df['ECG, X, RSPEC-R'])
#ecg = df["ECG"]
#df = df["df"]
#rpeaks = nk.ecg_find_peaks(df['ECG_Filtered'])
#nk.plot_events_in_signal(df['ECG_Filtered'], ecg["R_Peaks"])
#df['ECG, X, RSPEC-R'].iloc[104000:140000].plot()



#==============================================================================
# HRV Interpolation
#==============================================================================
df = nk.read_acqknowledge("abnormal_ECG.acq")
df = df[4000:19000]
sampling_rate = 1000
df = nk.ecg_process(df['ECG, X, RSPEC-R'], sampling_rate=sampling_rate)
df["df"]["ECG_Filtered"].plot()


rri = df["ECG"]['RR_Intervals']
rpeaks = df["ECG"]['R_Peaks']

ecg=df["df"]["ECG_Filtered"]


artifacts_treatment="interopolation"





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
#if artifacts_treatment == "deletion":
#    rri = rri.dropna()
#if artifacts_treatment == "interpolation":
#    rri = pd.Series(rri).interpolate(method="cubic")  # Interpolate using a 3rd order spline
#    rri = rri.dropna()  # Remove firsts and lasts NaNs that cannot be interpolated
#

  # dealing with outliers, resampling and converting RR intervals to a function of time (not a function of beats)






#rri_original = rri.copy()
rri = rri_original.copy()

# NEW
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



  # plotting
  plt.figure(figsize=(20, 3), dpi=100)
  plt.scatter(np.arange(rri_new.shape[0]), rri_new,s=1)
  plt.grid(True)
  plt.title('RRI indexed per beat')
  plt.ylabel('RR interval duration (sec)')
  plt.xlabel('#beat')
  plt.tight_layout()
  plt.show()

  plt.figure(figsize=(20, 3), dpi=100)
  plt.plot(rri,'b-',linewidth=0.5)
  plt.grid(True)
  plt.title('Resampled RRI indexed per time')
  plt.ylabel('RR interval duration (sec)')
  plt.xlabel('Time (sec)')
  plt.tight_layout()
  plt.show()


df=df["df"][["ECG_Filtered", "Heart_Rate"]]

df["ECG_HRV"] = np.nan
df["ECG_HRV"].ix[rpeaks[0]+1:rpeaks[0]+len(rri_new)] = rri_new

nk.z_score(df).plot()
