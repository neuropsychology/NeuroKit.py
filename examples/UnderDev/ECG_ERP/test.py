# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import biosppy
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
events = nk.find_events(df["Photosensor"], cut="lower")
epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+800, onset=-400)



def rsp_ERP(epoch, event_length, sampling_rate=1000, window_post=4):
    """
    Extract event-related respiratory (RSP) changes.

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contains in the epochs dict returned by :function:`nk.create_epochs()` on dataframe returned by :function:`nk.bio_process()`.
    event_length : int
        In seconds.
    sampling_rate : int
        Sampling rate (samples/second).
    window_post : float
        Post-stimulus window size (in seconds) to include eventual responses (usually 3 or 4).

    Returns
    ----------
    RSP_Response : dict
        Event-locked RSP response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(RSP=df["RSP"], add=df["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+8000, onset=-4000)
    >>> for epoch in epochs:
    >>>     RSP_Response = nk.rsp_ERP(epoch, event_length=4000)

    Notes
    ----------
    *Details*

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



    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    References
    -----------
    - Gomez, P., Stahel, W. A., & Danuser, B. (2004). Respiratory responses during affective picture viewing. Biological Psychology, 67(3), 359-373.
    """
    # Initialization
    event_length = event_length/sampling_rate*1000
    RSP_Response = {}

    # RSP Rate
    RSP_Response["RSP_Rate_Baseline"] = epoch["RSP_Rate"].ix[:0].mean()
    RSP_Response["RSP_Rate_Min"] = epoch["RSP_Rate"].ix[0:event_length].min()
    RSP_Response["RSP_Rate_MinDiff"] = RSP_Response["RSP_Rate_Min"] - RSP_Response["RSP_Rate_Baseline"]
    RSP_Response["RSP_Rate_MinTime"] = epoch["RSP_Rate"].ix[0:event_length].idxmin()/sampling_rate*1000
    RSP_Response["RSP_Rate_Max"] = epoch["RSP_Rate"].ix[0:event_length].max()
    RSP_Response["RSP_Rate_MaxDiff"] = RSP_Response["RSP_Rate_Max"] - RSP_Response["RSP_Rate_Baseline"]
    RSP_Response["RSP_Rate_MaxTime"] = epoch["RSP_Rate"].ix[0:event_length].idxmax()/sampling_rate*1000
    RSP_Response["RSP_Rate_Mean"] = epoch["RSP_Rate"].ix[0:event_length].mean()
    RSP_Response["RSP_Rate_MeanDiff"] = RSP_Response["RSP_Rate_Mean"] - RSP_Response["RSP_Rate_Baseline"]

    # Normalize
    baseline_mean = epoch["RSP_Filtered"].ix[:0].mean()
    baseline_std = epoch["RSP_Filtered"].ix[:0].std()
    z_rsp = (epoch["RSP_Filtered"].ix[0:]-baseline_mean)/baseline_std

    RSP_Response["RSP_Min"] = z_rsp.min()
    RSP_Response["RSP_MinTime"] = z_rsp.ix[0:event_length].idxmin()/sampling_rate*1000
    RSP_Response["RSP_Max"] = z_rsp.ix[0:event_length].max()
    RSP_Response["RSP_MaxTime"] = z_rsp.ix[0:event_length].idxmax()/sampling_rate*1000

    # RSP Phase
    RSP_Response["RSP_Inspiration"] = epoch["RSP_Inspiration"].ix[0]

    for i in range(0, int(event_length)-1):
        if epoch["RSP_Inspiration"].ix[i] != RSP_Response["RSP_Inspiration"]:
            phase_end = i
            break

    for i in range(0, epoch.index[0]+1, -1):
        if epoch["RSP_Inspiration"].ix[i] != RSP_Response["RSP_Inspiration"]:
            phase_beg = i
            break

    try:
        RSP_Response["RSP_Inspiration_Completion"] = -1*phase_beg/(phase_end - phase_beg)*100
    except ZeroDivisionError:
        RSP_Response["RSP_Inspiration_Completion"] = np.nan

    try:
        baseline_phase = nk.rsp_find_cycles(epoch["RSP_Inspiration"].ix[:0])
        phase = nk.rsp_find_cycles(epoch["RSP_Inspiration"].ix[0:])

        RSP_Response["RSP_Cycle_Length"] = pd.Series(phase["RSP_Cycles_Length"]).mean()/sampling_rate*1000
        RSP_Response["RSP_Cycle_Length_Baseline"] = pd.Series(baseline_phase["RSP_Cycles_Length"]).mean()/sampling_rate*1000
        RSP_Response["RSP_Cycle_LengthDiff"] = RSP_Response["RSP_Cycle_Length"]-RSP_Response["RSP_Cycle_Length_Baseline"]
    except IndexError:
        RSP_Response["RSP_Cycle_Length"] = np.nan
        RSP_Response["RSP_Cycle_Length_Baseline"] = np.nan
        RSP_Response["RSP_Cycle_LengthDiff"] = np.nan

    return(RSP_Response)

Responses = {}
for i in epochs:
    epoch = epochs[i]
    Responses[i] = rsp_ERP(epoch, event_length=300, sampling_rate=100, window_post=4)


