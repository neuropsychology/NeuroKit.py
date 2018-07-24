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
        rsp_rate = interpolate(rsp_rate, rsp_times, sampling_rate)  # Interpolation using 3rd order spline
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
def rsp_EventRelated(epoch, event_length, window_post=4):
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
    >>> bio = nk.bio_process(ecg=data["ECG"], rsp=data["RSP"], eda=data["EDA"], sampling_rate=1000, add=data["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=7, onset=-0.5)
    >>> for epoch in epochs:
    >>>     bio_response = nk.bio_EventRelated(epoch, event_length=4, window_post=3)

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


    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    References
    -----------
    - Gomez, P., Stahel, W. A., & Danuser, B. (2004). Respiratory responses during affective picture viewing. Biological Psychology, 67(3), 359-373.
    """
    # Initialization
    RSP_Response = {}
    window_end = event_length + window_post

    # RSP Rate
    # =============
    if "RSP_Rate" in epoch.columns:
        RSP_Response["RSP_Rate_Baseline"] = epoch["RSP_Rate"].ix[0]
        RSP_Response["RSP_Rate_Min"] = epoch["RSP_Rate"].ix[0:window_end].min()
        RSP_Response["RSP_Rate_MinDiff"] = RSP_Response["RSP_Rate_Min"] - RSP_Response["RSP_Rate_Baseline"]
        RSP_Response["RSP_Rate_MinTime"] = epoch["RSP_Rate"].ix[0:window_end].idxmin()
        RSP_Response["RSP_Rate_Max"] = epoch["RSP_Rate"].ix[0:window_end].max()
        RSP_Response["RSP_Rate_MaxDiff"] = RSP_Response["RSP_Rate_Max"] - RSP_Response["RSP_Rate_Baseline"]
        RSP_Response["RSP_Rate_MaxTime"] = epoch["RSP_Rate"].ix[0:window_end].idxmax()
        RSP_Response["RSP_Rate_Mean"] = epoch["RSP_Rate"].ix[0:window_end].mean()
        RSP_Response["RSP_Rate_MeanDiff"] = RSP_Response["RSP_Rate_Mean"] - RSP_Response["RSP_Rate_Baseline"]


    # RSP Phase
    # =============
    if "RSP_Inspiration" in epoch.columns:
        RSP_Response["RSP_Inspiration"] = epoch["RSP_Inspiration"].ix[0]

        # Identify beginning and end
        phase_beg = np.nan
        phase_end = np.nan
        for i in epoch[0:window_end].index:
            if epoch["RSP_Inspiration"].ix[i] != RSP_Response["RSP_Inspiration"]:
                phase_end = i
                break
        for i in epoch[:0].index[::-1]:
            if epoch["RSP_Inspiration"].ix[i] != RSP_Response["RSP_Inspiration"]:
                phase_beg = i
                break

        RSP_Response["RSP_Inspiration_Completion"] = -1*phase_beg/(phase_end - phase_beg)*100


    return(RSP_Response)
