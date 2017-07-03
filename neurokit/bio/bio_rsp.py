# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import biosppy

from ..signal import *

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def rsp_process(rsp, sampling_rate=1000):
    """
    Automated processing of RSP signals.

    Parameters
    ----------
    rsp : list or array
        Respiratory (RSP) signal array.
    sampling_rate : int
        Sampling rate (samples/second).

    Returns
    ----------
    processed_rsp : dict
        Dict containing processed RSP features.

        Contains the RSP raw signal, the filtered signal, the respiratory cycles onsets, and respiratory phases (inspirations and expirations).

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_rsp = nk.rsp_process(rsp_signal)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - biosppy
    - numpy
    - pandas

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy
    """
    processed_rsp = {"df": pd.DataFrame({"RSP_Raw": np.array(rsp)})}

    biosppy_rsp = dict(biosppy.signals.resp.resp(rsp, sampling_rate=sampling_rate, show=False))
    processed_rsp["df"]["RSP_Filtered"] = biosppy_rsp["filtered"]


#   RSP Rate
#   ============
    rsp_rate = biosppy_rsp["resp_rate"]*60  # Get RSP rate value (in cycles per minute)
    rsp_times = biosppy_rsp["resp_rate_ts"]   # the time (in sec) of each rsp rate value
    rsp_times = np.round(rsp_times*sampling_rate).astype(int)  # Convert to timepoints
    try:
        rsp_rate = discrete_to_continuous(rsp_rate, rsp_times, sampling_rate)  # Interpolation using 3rd order spline
        processed_rsp["df"]["RSP_Rate"] = rsp_rate
    except TypeError:
        print("NeuroKit Warning: rsp_process(): Sequence too short to compute respiratory rate.")
        processed_rsp["df"]["RSP_Rate"] = np.nan


#   RSP Cycles
#   ===========================
    rsp_cycles = rsp_find_cycles(biosppy_rsp["filtered"])
    processed_rsp["df"]["RSP_Inspiration"] = rsp_cycles["RSP_Inspiration"]

    processed_rsp["RSP"] = {}
    processed_rsp["RSP"]["Cycles_Onsets"] = rsp_cycles["RSP_Cycles_Onsets"]
    processed_rsp["RSP"]["Expiration_Onsets"] = rsp_cycles["RSP_Expiration_Onsets"]
    processed_rsp["RSP"]["Cycles_Length"] = rsp_cycles["RSP_Cycles_Length"]/sampling_rate

#   RSP Variability
#   ===========================
    rsp_diff = processed_rsp["RSP"]["Cycles_Length"]

    processed_rsp["RSP"]["Respiratory_Variability"] = {}
    processed_rsp["RSP"]["Respiratory_Variability"]["RSPV_SD"] = np.std(rsp_diff)
    processed_rsp["RSP"]["Respiratory_Variability"]["RSPV_RMSSD"] = np.sqrt(np.mean(rsp_diff ** 2))
    processed_rsp["RSP"]["Respiratory_Variability"]["RSPV_RMSSD_Log"] = np.log(processed_rsp["RSP"]["Respiratory_Variability"]["RSPV_RMSSD"])


    return(processed_rsp)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def rsp_find_cycles(signal):
    """
    Find Respiratory cycles onsets, durations and phases.

    Parameters
    ----------
    signal : list or array
        Respiratory (RSP) signal (preferably filtered).


    Returns
    ----------
    rsp_cycles : dict
        RSP cycles features.

    Example
    ----------
    >>> import neurokit as nk
    >>> rsp_cycles = nk.rsp_find_cycles(signal)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - biosppy

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy

    """
    # Compute gradient (sort of derivative)
    gradient = np.gradient(signal)
    # Find zero-crossings
    zeros, = biosppy.tools.zero_cross(signal=gradient, detrend=True)

    # Find respiratory phases
    phases_indices = []
    for i in zeros:
        if gradient[i+1] > gradient[i-1]:
            phases_indices.append("Inspiration")
        else:
            phases_indices.append("Expiration")

    # Select cycles (inspiration) and expiration onsets
    inspiration_onsets = []
    expiration_onsets = []
    for index, onset in enumerate(zeros):
        if phases_indices[index] == "Inspiration":
            inspiration_onsets.append(onset)
        if phases_indices[index] == "Expiration":
            expiration_onsets.append(onset)


    # Create a continuous inspiration signal
    # ---------------------------------------
    # Find initial phase
    if phases_indices[0] == "Inspiration":
        phase = "Expiration"
    else:
        phase = "Inspiration"

    inspiration = []
    phase_counter = 0
    for i, value in enumerate(signal):
        if i == zeros[phase_counter]:
            phase = phases_indices[phase_counter]
            if phase_counter < len(zeros)-1:
                phase_counter += 1
        inspiration.append(phase)

    # Find last phase
    if phases_indices[len(phases_indices)-1] == "Inspiration":
        last_phase = "Expiration"
    else:
        last_phase = "Inspiration"
    inspiration = np.array(inspiration)
    inspiration[max(zeros):] = last_phase

    # Convert to binary
    inspiration[inspiration == "Inspiration"] = 1
    inspiration[inspiration == "Expiration"] = 0
    inspiration = pd.to_numeric(inspiration)

    cycles_length = np.diff(inspiration_onsets)

    rsp_cycles = {"RSP_Inspiration": inspiration,
                  "RSP_Expiration_Onsets": expiration_onsets,
                  "RSP_Cycles_Onsets": inspiration_onsets,
                  "RSP_Cycles_Length": cycles_length}

    return(rsp_cycles)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def rsp_EventRelated(epoch, event_length, sampling_rate=1000, window_post=4):
    """
    Extract event-related respiratory (RSP) changes.

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
        try:
            if epoch["RSP_Inspiration"].ix[i] != RSP_Response["RSP_Inspiration"]:
                phase_end = i
                break
        except KeyError as error:
            print("NeuroKit Warning: rsp_ERP(): Didn't find any phase end. Error: " + str(error))
            phase_end = np.nan

    for i in range(0, epoch.index[0]+1, -1):
        try:
            if epoch["RSP_Inspiration"].ix[i] != RSP_Response["RSP_Inspiration"]:
                phase_beg = i
                break
        except KeyError as error:
            print("NeuroKit Warning: rsp_ERP(): Didn't find any phase beginning. Error: " + str(error))
            phase_beg = np.nan

    try:
        RSP_Response["RSP_Inspiration_Completion"] = -1*phase_beg/(phase_end - phase_beg)*100
    except ZeroDivisionError as error:
        print("NeuroKit Warning: rsp_ERP(): RSP_Inspiration_Completion. Error: " + str(error))
        RSP_Response["RSP_Inspiration_Completion"] = np.nan
    except UnboundLocalError as error:
        print("NeuroKit Warning: rsp_ERP(): RSP_Inspiration_Completion. Error: " + str(error))
        RSP_Response["RSP_Inspiration_Completion"] = np.nan

    try:
        baseline_phase = rsp_find_cycles(epoch["RSP_Inspiration"].ix[:0])
        phase = rsp_find_cycles(epoch["RSP_Inspiration"].ix[0:])

        RSP_Response["RSP_Cycle_Length"] = pd.Series(phase["RSP_Cycles_Length"]).mean()/sampling_rate*1000
        RSP_Response["RSP_Cycle_Length_Baseline"] = pd.Series(baseline_phase["RSP_Cycles_Length"]).mean()/sampling_rate*1000
        RSP_Response["RSP_Cycle_LengthDiff"] = RSP_Response["RSP_Cycle_Length"]-RSP_Response["RSP_Cycle_Length_Baseline"]
    except IndexError:
        RSP_Response["RSP_Cycle_Length"] = np.nan
        RSP_Response["RSP_Cycle_Length_Baseline"] = np.nan
        RSP_Response["RSP_Cycle_LengthDiff"] = np.nan

    return(RSP_Response)
