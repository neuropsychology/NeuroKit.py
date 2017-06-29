import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib.pyplot as plt
import scipy
import biosppy
import datetime

df = pd.read_csv('normal_ECG.csv')
df = df.loc[10000:20000]  # Select 10s of signal


sampling_rate=1000
ecg = df["ECG"]
bio = nk.bio_process(ecg=df["ECG"], sampling_rate=sampling_rate)

#
## Extract useful things
#data = df["df"][["ECG_Filtered", "Heart_Rate"]].copy()
#rri = df["ECG"]['RR_Intervals']
#rpeaks = df["ECG"]['R_Peaks']
#ecg = df["df"]["ECG_Raw"]



def discrete_to_continuous(values, value_times, sampling_rate=1000):
    """
    3rd order spline interpolation.
    """
    # fit a 3rd degree spline on the data.
    spline = scipy.interpolate.splrep(x=value_times, y=values, k=3, s=0)  # s=0 guarantees that it will pass through ALL the given points
    # Get the values indexed per time
    signal = scipy.interpolate.splev(x=np.arange(0, beat_time[-1], 1/sampling_rate), tck=spline, der=0)
    # Transform to series
    signal = pd.Series(signal)
    return(signal)

# OLD
#=====================

# Convert to DataFrame
ecg_df = pd.DataFrame({"ECG_Raw": np.array(ecg)})

# Compute several features using biosppy
biosppy_ecg = dict(biosppy.signals.ecg.ecg(ecg, sampling_rate=sampling_rate, show=False))

# Filtered signal
ecg_df["ECG_Filtered"] = biosppy_ecg["filtered"]

# Store R peaks indexes
rpeaks = biosppy_ecg['rpeaks']

# Transform to markers to add to the main dataframe
rpeaks_signal = np.array([np.nan]*len(ecg))
rpeaks_signal[rpeaks] = 1
ecg_df["ECG_Rpeaks"] = rpeaks_signal


# Heart Rate
heart_rate = biosppy_ecg["heart_rate"]  # Get heart rate values
beats_times = rpeaks[1:]/sampling_rate  # the time (in sec) at which each beat occured starting from the 2nd beat
heart_rate = discrete_to_continuous(heart_rate, beats_times, sampling_rate)  # Interpolation using 3rd order spline



# plotting
data = bio["df"][["ECG_Filtered", "Heart_Rate"]].copy()
data["Heart_Rate2"] = np.nan
data["Heart_Rate2"].ix[rpeaks[1]+1:rpeaks[1]+len(heart_rate)] = heart_rate

#  nk.z_score(data).plot()
nk.plot_events_in_signal(nk.z_score(data), rpeaks)

