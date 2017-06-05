# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import biosppy
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
events = nk.find_events(df["Photosensor"], cut="lower")
epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+800, onset=-400)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def bio_ERP(epoch, event_length, sampling_rate=1000, window_post=4):
    """
    Extract event-related bio (EDA, ECG and RSP) changes.

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contains in the epochs dict returned by :function:`neurokit.create_epochs()` on dataframe returned by :function:`neurokit.bio_process()`.
    event_length : int
        In seconds.
    sampling_rate : int
        Sampling rate (samples/second).
    window_post : float
        Post-stimulus window size (in seconds) to include eventual responses (usually 3 or 4).

    Returns
    ----------
    RSP_Response : dict
        Event-locked bio response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(RSP=df["RSP"], add=df["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+8000, onset=-4000)
    >>> for epoch in epochs:
    >>>     bio_response = nk.bio_ERP(epoch, event_length=4000)

    Notes
    ----------
    *Details*

    - **ECG Features**

        - **Heart_Rate_Baseline**: mean HR before stimulus onset.
        - **Heart_Rate_Min**: Min HR after stimulus onset.
        - **Heart_Rate_MinDiff**: HR mininum - baseline.
        - **Heart_Rate_MinTime**: Time of minimum.
        - **Heart_Rate_Max**: Max HR after stimulus onset.
        - **Heart_Rate_MaxDiff**: Max HR - baseline.
        - **Heart_Rate_MaxTime**: Time of maximum.
        - **Heart_Rate_Mean**: Mean HR after stimulus onset.
        - **Heart_Rate_MeanDiff**: Mean HR - baseline.
        - **Cardiac_Systole**: Cardiac phase on stimulus onset (1 = systole, 0 = diastole).
        - **Cardiac_Systole_Completion**: Percentage of cardiac phase completion on simulus onset.
        - **HRV**: Returns HRV features. See :func:`neurokit.ecg_hrv()`.
        - **HRV_Diff**: HRV post-stimulus - HRV pre-stimulus.
    - **Respiration Features**

        - **RSP_Rate_Baseline**: mean RSP Rate before stimulus onset.
        - **RSP_Rate_Min**: Min RSP Rate after stimulus onset.
        - **RSP_Rate_MinDiff**: RSP Rate mininum - baseline.
        - **RSP_Rate_MinTime**: Time of minimum.
        - **RSP_Rate_Max**: Max RSP Rate after stimulus onset.
        - **RSP_Rate_MaxDiff**: Max RSP Rate - baseline.
        - **RSP_Rate_MaxTime**: Time of maximum.
        - **RSP_Rate_Mean**: Mean RSP Rate after stimulus onset.
        - **RSP_Rate_MeanDiff**: Mean RSP Rate - baseline.
        - **RSP_Min**: Value in standart deviation (normalized by baseline) of the lowest point.
        - **RSP_MinTime**: Time of RSP Min.
        - **RSP_Max**: Value in standart deviation (normalized by baseline) of the highest point.
        - **RSP_MaxTime**: Time of RSP Max.
        - **RSP_Inspiration**: Respiration phase on stimulus onset (1 = inspiration, 0 = expiration).
        - **RSP_Inspiration_Completion**: Percentage of respiration phase on stimulus onset.
        - **RSP_Cycle_Length**: Mean duration of RSP cycles (inspiration and expiration) after stimulus onset.
        - **RSP_Cycle_Length_Baseline**: Mean duration of RSP cycles (inspiration and expiration) before stimulus onset.
        - **RSP_Cycle_LengthDiff**: mean cycle length after - mean cycle length before stimulus onset.
    - **EDA Features**
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

    References
    -----------
    - Gomez, P., Stahel, W. A., & Danuser, B. (2004). Respiratory responses during affective picture viewing. Biological Psychology, 67(3), 359-373.
    - Schneider, R., Schmidt, S., Binder, M., Schäfer, F., & Walach, H. (2003). Respiration-related artifacts in EDA recordings: introducing a standardized method to overcome multiple interpretations. Psychological reports, 93(3), 907-920.
    """
    bio_response = {}
    if "ECG_Filtered" in epoch.columns:
        ECG_Response = ecg_ERP(epoch, event_length, sampling_rate, window_post)
        bio_response.update(ECG_Response)
    if "RSP_Filtered" in epoch.columns:
        RSP_Response = rsp_ERP(epoch, event_length, sampling_rate, window_post)
        bio_response.update(RSP_Response)
    if "EDA_Filtered" in epoch.columns:
        EDA_Response = eda_ERP(epoch, event_length, sampling_rate, window_post)
        bio_response.update(EDA_Response)

    return(bio_response)


Responses = {}
for i in epochs:
    epoch = epochs[i]
    Responses[i] = bio_ERP(epoch, event_length=300, sampling_rate=100, window_post=4)


