# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import biosppy
import datetime
import hrv

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def process_ecg(ecg, rsp=None, sampling_rate=1000, resampling_method="bfill"):
    """
    Automated processing of ECG and RSP signals.

    Parameters
    ----------
    ecg =  array
        ECG signal array.
    rsp =  array
        Respiratory signal array.
    sampling_rate = int
        Sampling rate (samples/second).
    resampling_method = str
        "mean", "pad" or "bfill", the resampling method.

    Returns
    ----------
    ecg_features = dict
        Dict containing ECG extracted features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, and the RSP filtered signal (if respiration provided).

        This function is mainly a wrapper for the biosspy.ecg.ecg() and the hrv.hrv() functions. Credits go to their authors.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> ecg_features = nk.process_ecg(ecg_signal, resp_signal)

    Authors
    ----------
    Dominique Makowski, the bioSSPy dev team, Rhenan Bartels (from hrv)

    Dependencies
    ----------
    - biosppy
    - hrv
    - numpy
    - pandas
    """
    ecg_features = {"ECG_Raw": ecg}

    # Compute several features using biosppy
    biosppy_ecg = dict(biosppy.signals.ecg.ecg(ecg, sampling_rate=sampling_rate, show=False))

    # Filtered signal and R peaks
    ecg_features["ECG_Filtered"] = biosppy_ecg["filtered"]
    ecg_features["ECG_Rpeaks_Indexes"] = biosppy_ecg["rpeaks"]

    # Heart rate index creation
    time_now = datetime.datetime.now()
    # Convert seconds to datetime deltas
    time_index = [datetime.timedelta(seconds=x) for x in biosppy_ecg["heart_rate_ts"]]
    time_index = np.array(time_index) + time_now
    heart_rate = pd.Series(biosppy_ecg["heart_rate"], index=time_index)

    # Create resampling factor
    resampling_rate = str(int(1000/sampling_rate)) + "L"

    # Resample
    if resampling_method == "mean":
        heart_rate = heart_rate.resample(resampling_rate).mean()
    if resampling_method == "pad":
        heart_rate = heart_rate.resample(resampling_rate).pad()
    if resampling_method == "bfill":
        heart_rate = heart_rate.resample(resampling_rate).bfill()

    # Store Heart Rate
#    ecg_features["Heart_Rate"] = scipy.signal.resample(heart_rate, len(ecg))  # Looks more bad than by truncating as below
    ecg_features["Heart_Rate"] = heart_rate[0:len(ecg)]
    ecg_features["Heart_Beats"] = biosppy_ecg["templates"]

    # RSP
    if rsp is not None:
        biosppy_rsp = dict(biosppy.signals.resp.resp(rsp, sampling_rate=sampling_rate, show=False))
        ecg_features["RSP_Raw"] = rsp
        ecg_features["RSP_Filtered"] = biosppy_rsp["filtered"]

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

        ecg_features["RSP_Rate"] = rsp_rate[0:len(rsp)]


    # HRV
    rri = np.diff(ecg_features["ECG_Rpeaks_Indexes"])
    rri_time = np.cumsum(rri) / 1000.0
    rri_time -= rri_time[0]

    # Calculate time domain indexes
    ecg_features["HRV"] = hrv.classical.time_domain(rri)

    # Calculate frequency domain indexes
    try:
        ecg_features["HRV"].update(hrv.classical.frequency_domain(rri, method='welch', interp_freq=4.0))
    except:
        print("NeuroKit Error: process_ecg(): Signal to short to compute frequency domains HRV. Must me longer than 3.4 minutes.")


    return(ecg_features)