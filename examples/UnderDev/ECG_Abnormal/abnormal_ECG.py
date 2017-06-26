import neurokit as nk
import numpy as np
import pandas as pd
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



artifacts_treatment="deletion"
artifacts_treatment="interpolation"


# Initialize empty dict
hrv = {}

# Preprocessing
# ==================
# Basic resampling to 1000Hz to standardize the scale
rri = rri*1000/sampling_rate
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
rri[rri < 600] = np.nan
rri[rri > 1300] = np.nan

# Artifact treatment
hrv["n_Artifacts"] = pd.isnull(rri).sum()/len(rri)
if artifacts_treatment == "deletion":
    rri = rri.dropna()
if artifacts_treatment == "interpolation":
    rri = pd.Series(rri).interpolate(method="cubic")  # Interpolate using a 3rd order spline
    rri = rri.dropna()  # Remove first and lasts NaNs that cannot be interpolated



# Preprocessing
outliers = np.array(identify_outliers(rri, treshold=2.58))
rri[outliers] = np.nan
rri = pd.Series(rri).interpolate()