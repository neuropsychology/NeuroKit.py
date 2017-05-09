# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import biosppy
import datetime


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def rsp_process(rsp, sampling_rate=1000, resampling_method="bfill"):
    """
    Automated processing of RSP signals.

    Parameters
    ----------
    rsp : list or array
        Respiratory (RSP) signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    resampling_method : str
        "mean", "pad" or "bfill", the resampling method used for RSP heart rate.

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
    processed_rsp = {"df": pd.DataFrame({"RSP_Raw":rsp})}

    biosppy_rsp = dict(biosppy.signals.resp.resp(rsp, sampling_rate=sampling_rate, show=False))
    processed_rsp["df"]["RSP_Filtered"] = biosppy_rsp["filtered"]


    # RSP Rate resampling
    # ===========================
    # Create resampling factor
    resampling_rate = str(int(1000/sampling_rate)) + "L"

    # RSP rate index creation
    time_now = datetime.datetime.now()
    # Convert seconds to datetime deltas
    time_index = [datetime.timedelta(seconds=x) for x in biosppy_rsp["resp_rate_ts"]]
    time_index = np.array(time_index) + time_now
    rsp_rate = pd.Series(biosppy_rsp["resp_rate"], index=time_index)

    if resampling_method == "mean":
        rsp_rate = rsp_rate.resample(resampling_rate).mean()
    if resampling_method == "pad":
        rsp_rate = rsp_rate.resample(resampling_rate).pad()
    if resampling_method == "bfill":
        rsp_rate = rsp_rate.resample(resampling_rate).bfill()

    if len(rsp_rate) >= len(rsp):
        rsp_rate = rsp_rate[0:len(rsp)]
    else:
        rsp_rate = [rsp_rate[-1]]*(len(rsp)-len(rsp_rate)) + list(rsp_rate)
    processed_rsp["df"]["RSP_Rate"] = np.array(rsp_rate)*60  # From Hz to respiration per seconds



    # RSP Cycles
    # ===========================
    rsp_cycles = rsp_find_cycles(biosppy_rsp["filtered"])
    processed_rsp["df"]["RSP_Inspiration"] = rsp_cycles["RSP_Inspiration"]

    processed_rsp["RSP"] = {}
    processed_rsp["RSP"]["Cycles_Onsets"] = rsp_cycles["RSP_Cycles_Onsets"]
    processed_rsp["RSP"]["Expiration_Onsets"] = rsp_cycles["RSP_Expiration_Onsets"]
    processed_rsp["RSP"]["Cycles_Length"] = rsp_cycles["RSP_Cycles_Length"]/sampling_rate

    # RSP Variability
    # ===========================
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
    Find R peaks indices on the ECG channel.

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