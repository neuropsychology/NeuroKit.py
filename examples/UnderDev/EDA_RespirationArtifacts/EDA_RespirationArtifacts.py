import neurokit as nk
import pandas as pd
import numpy as np
import scipy

df = pd.read_csv("EDA_RSP_Artifacts.csv")  # Sampled at 100Hz
conditions = pd.Series.from_csv("events.csv")

# Preprocessing
df = nk.bio_process(eda=df["EDA"], rsp=df["RSP"], add=df["Photosensor"], sampling_rate=100, scr_min_amplitude=0.02)
df = df["df"]


events = nk.find_events(df["Photosensor"], cut="lower")
epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+800, onset=-400)


#==============================================================================
#
#==============================================================================
def eda_ERP(epoch, event_length, sampling_rate=1000, window_post=4):
    """
    Extract event-related EDA and Skin Conductance Response (SCR).

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contains in the epochs dict returned by :function:`nk.create_epochs()` on dataframe returned by :function:`nk.bio_process()`. Index must range from -4s to +4s (relatively to event onset and end).
    event_length : int
        In seconds.
    sampling_rate : int
        Sampling rate (samples/second).
    window_post : float
        Post-stimulus window size (in seconds) to include eventual responses (usually 3 or 4).

    Returns
    ----------
    SCR : dict
        Event-locked SCR response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(eda=df["EDA"], add=df["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+8000, onset=-4000)
    >>> for epoch in epochs:
    >>>     SCR = nk.eda_eventlocked_response(epoch, event_length=4000)

    Notes
    ----------
    *Details*

    - **Looking for help**: *Experimental*: respiration artifacts correction needs to be implemented.
    - **EDA_Peak**: Max of EDA (in a window starting 1s after the stim onset) minus baseline.
    - **SCR_Amplitude**: Peak of SCR. If no SCR, returns NA.
    - **SCR_Magnitude**: Peak of SCR. If no SCR, returns 0.
    - **SCR_Amplitude_Log**: log of 1+amplitude.
    - **SCR_Magnitude_Log**: log of 1+magnitude.
    - **SCR_PeakTime**: Time of peak.
    - **SCR_Latency**: Time between stim onset and SCR onset.
    - **SCR_RiseTime**: Time between SCR onset and peak.
    - **SCR_Strength**: *Experimental*: peak divided by latency.


    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    - https://www.biopac.com/wp-content/uploads/EDA-SCR-Analysis.pdf

    References
    -----------
    - Schneider, R., Schmidt, S., Binder, M., Schäfer, F., & Walach, H. (2003). Respiration-related artifacts in EDA recordings: introducing a standardized method to overcome multiple interpretations. Psychological reports, 93(3), 907-920.
    """
    # Initialization
    event_length = event_length/sampling_rate*1000
    SCR = {}

    # Sanity check
    if epoch.index[-1]/sampling_rate*1000-event_length < 1000:
        print("NeuroKit Warning: eda_eventlocked_response(): your epoch only lasts for about %.2f s post stimulus. You might lose some SCRs." %((epoch.index[-1]/sampling_rate*1000-event_length)/1000))

    if epoch.index[0]/sampling_rate*1000 > -3000:
        print("NeuroKit Warning: eda_eventlocked_response(): your epoch only starts %.2f s before the stimulus. Might induce some errors in artifacts correction." %((epoch.index[0]/sampling_rate*1000)/1000))



    # EDA Based
    # =================
    baseline = epoch["EDA_Filtered"].ix[0]
    eda_peak = epoch["EDA_Filtered"].ix[sampling_rate:event_length+window_post*sampling_rate].max()
    SCR["EDA_Peak"] = eda_peak - baseline

    # SCR Based
    # =================
    # Very Basic Model
#    SCR["SCR_Amplitude_Basic"] = epoch["SCR_Peaks"].ix[100:event_length+4*sampling_rate].max()
#    if np.isnan(SCR["SCR_Amplitude_Basic"]):
#        SCR["SCR_Magnitude_Basic"] = 0
#    else:
#        SCR["SCR_Magnitude_Basic"] = SCR["SCR_Amplitude_Basic"]

    # Model
    peak_onset = epoch["SCR_Onsets"].ix[0:event_length].idxmax()
    if pd.isnull(peak_onset) is False:
        SCR["SCR_Amplitude"] = epoch["SCR_Peaks"].ix[peak_onset:event_length+window_post*sampling_rate].max()
        peak_loc = epoch["SCR_Peaks"].ix[peak_onset:event_length+window_post*sampling_rate].idxmax()
        SCR["SCR_Magnitude"] = SCR["SCR_Amplitude"]
        if pd.isnull(SCR["SCR_Amplitude"]):
            SCR["SCR_Magnitude"] = 0
    else:
        SCR["SCR_Amplitude"] = np.nan
        SCR["SCR_Magnitude"] = 0

    # Log
    SCR["SCR_Amplitude_Log"] = np.log(1+SCR["SCR_Amplitude"])
    SCR["SCR_Magnitude_Log"] = np.log(1+SCR["SCR_Magnitude"])


    # Latency and Rise time
    if np.isfinite(SCR["SCR_Amplitude"]):
        peak_onset = epoch["SCR_Onsets"].ix[0:peak_loc].idxmax()

        SCR["SCR_PeakTime"] = peak_loc/sampling_rate*1000
        SCR["SCR_Latency"] = peak_onset/sampling_rate*1000
        SCR["SCR_RiseTime"] = (peak_loc - peak_onset)/sampling_rate*1000
    else:
        SCR["SCR_PeakTime"] = np.nan
        SCR["SCR_Latency"] = np.nan
        SCR["SCR_RiseTime"] = np.nan


    SCR["SCR_Strength"] = SCR["SCR_Magnitude"]/(SCR["SCR_Latency"]/1000)
#     RSP Corrected
    # This needs to be done!!
    if "RSP_Filtered" in epoch.columns:
#        granger = statsmodels.tsa.stattools.grangercausalitytests(epoch[["EDA_Filtered", "RSP_Filtered"]], 10)
        RSP_z = nk.z_score(epoch["RSP_Filtered"])
        RSP_peak = RSP_z.ix[:0].max()
        if np.isnan(RSP_peak[0]) and RSP_peak[0] > 1.96:
            SCR["SCR_Amplitude_RSP_Corrected"] = SCR["SCR_Amplitude"]/(RSP_peak-0.96)
            SCR["SCR_Magnitude_RSP_Corrected"] = SCR["SCR_Magnitude"]/(RSP_peak-0.96)
        else:
            SCR["SCR_Amplitude_RSP_Corrected"] = SCR["SCR_Amplitude"]
            SCR["SCR_Magnitude_RSP_Corrected"] = SCR["SCR_Magnitude"]

    return(SCR)
#==============================================================================
#
#==============================================================================
evoked = {"Negative": {
#        "SCR_Amplitude_Basic": [],
#        "SCR_Magnitude_Basic": [],
        "SCR_Amplitude": [],
        "SCR_Magnitude": [],
        "SCR_Amplitude_Log": [],
        "SCR_Magnitude_Log": [],
        "SCR_Amplitude_RSP_Corrected": [],
        "SCR_Magnitude_RSP_Corrected": [],
        "SCR_PeakTime": [],
        "SCR_Latency": [],
        "SCR_RiseTime": [],
        "SCR_Strength": []},
    "Neutral": {
#        "SCR_Amplitude_Basic": [],
#        "SCR_Magnitude_Basic": [],
        "SCR_Amplitude": [],
        "SCR_Magnitude": [],
        "SCR_Amplitude_Log": [],
        "SCR_Magnitude_Log": [],
        "SCR_Amplitude_RSP_Corrected": [],
        "SCR_Magnitude_RSP_Corrected": [],
        "SCR_PeakTime": [],
        "SCR_Latency": [],
        "SCR_RiseTime": [],
        "SCR_Strength": []}}


for index, condition in enumerate(conditions):
    epoch = epochs[index]
    SCR = eda_ERP(epoch, event_length=300, sampling_rate=100)
#    if SCR["SCR_Magnitude_Basic"] != 0:
#        print(["SCR_Magnitude_Basic"])
#        break
#    evoked[condition]["SCR_Amplitude_Basic"].append(SCR["SCR_Amplitude_Basic"])
#    evoked[condition]["SCR_Magnitude_Basic"].append(SCR["SCR_Magnitude_Basic"])
    evoked[condition]["SCR_Amplitude"].append(SCR["SCR_Amplitude"])
    evoked[condition]["SCR_Magnitude"].append(SCR["SCR_Magnitude"])
    evoked[condition]["SCR_Amplitude_Log"].append(SCR["SCR_Amplitude_Log"])
    evoked[condition]["SCR_Magnitude_Log"].append(SCR["SCR_Magnitude_Log"])
    evoked[condition]["SCR_Amplitude_RSP_Corrected"].append(SCR["SCR_Amplitude_RSP_Corrected"])
    evoked[condition]["SCR_Magnitude_RSP_Corrected"].append(SCR["SCR_Magnitude_RSP_Corrected"])
    evoked[condition]["SCR_PeakTime"].append(SCR["SCR_PeakTime"])
    evoked[condition]["SCR_Latency"].append(SCR["SCR_Latency"])
    evoked[condition]["SCR_RiseTime"].append(SCR["SCR_RiseTime"])
    evoked[condition]["SCR_Strength"].append(SCR["SCR_Strength"])




print("========SCR=========")
#print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_Amplitude_Basic"]).dropna(), pd.Series(evoked["Neutral"]["SCR_Amplitude_Basic"]).dropna()))
#print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(evoked["Negative"]["SCR_Magnitude_Basic"], evoked["Neutral"]["SCR_Magnitude_Basic"]))
print("-------Normal------")
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_Amplitude"]).dropna(), pd.Series(evoked["Neutral"]["SCR_Amplitude"]).dropna()))
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(evoked["Negative"]["SCR_Magnitude"], evoked["Neutral"]["SCR_Magnitude"]))
print("-------Log------")
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_Amplitude_Log"]).dropna(), pd.Series(evoked["Neutral"]["SCR_Amplitude_Log"]).dropna()))
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(evoked["Negative"]["SCR_Magnitude_Log"], evoked["Neutral"]["SCR_Magnitude_Log"]))
print("-------RSP------")
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_Amplitude_RSP_Corrected"]).dropna(), pd.Series(evoked["Neutral"]["SCR_Amplitude_RSP_Corrected"]).dropna()))
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(evoked["Negative"]["SCR_Magnitude_RSP_Corrected"], evoked["Neutral"]["SCR_Magnitude_RSP_Corrected"]))
print("-------Other------")
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_PeakTime"]).dropna(), pd.Series(evoked["Neutral"]["SCR_PeakTime"]).dropna()))
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_Latency"]).dropna(), pd.Series(evoked["Neutral"]["SCR_Latency"]).dropna()))
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_RiseTime"]).dropna(), pd.Series(evoked["Neutral"]["SCR_RiseTime"]).dropna()))
print("f = %0.2f, p = %0.2f" %scipy.stats.ttest_ind(pd.Series(evoked["Negative"]["SCR_Strength"]).dropna(), pd.Series(evoked["Neutral"]["SCR_Strength"]).dropna()))



