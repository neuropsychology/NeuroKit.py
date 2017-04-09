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
def ecg_process(ecg, rsp=None, sampling_rate=1000, resampling_method="bfill"):
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
    processed_ecg = dict
        Dict containing processed ECG features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, and the RSP filtered signal (if respiration provided).

        This function is mainly a wrapper for the biosspy.ecg.ecg() and the hrv.hrv() functions. Credits go to their authors.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_ecg = nk.ecg_process(ecg_signal, resp_signal)

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
    ecg_df = pd.DataFrame({"ECG_Raw": np.array(ecg)})

    # Compute several features using biosppy
    biosppy_ecg = dict(biosppy.signals.ecg.ecg(ecg, sampling_rate=sampling_rate, show=False))

    # Filtered signal
    ecg_df["ECG_Filtered"] = biosppy_ecg["filtered"]

    # Store R peaks indexes
    r_peaks = np.array([np.nan]*len(ecg))
    r_peaks[biosppy_ecg['rpeaks']] = 1
    ecg_df["ECG_R_Peaks"] = r_peaks


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
    if len(heart_rate) >= len(ecg):
        ecg_df["Heart_Rate"] = np.array(heart_rate[0:len(ecg)])
    else:
        ecg_df["Heart_Rate"] = np.array([heart_rate[-1]]*(len(ecg)-len(heart_rate)) + list(heart_rate))
#        ecg_features["Heart_Rate"] = scipy.signal.resample(heart_rate, len(ecg))  # Looks more badly when resampling with scipy


    # HRV
    rri = np.diff(biosppy_ecg["rpeaks"])
    rri_time = np.cumsum(rri) / 1000.0
    rri_time -= rri_time[0]

    # Calculate time domain indexes
    hrv_time_domain = hrv.classical.time_domain(rri)
    hrv_features = {"HRV_mhr": hrv_time_domain['mhr'],
                    "HRV_mrri": hrv_time_domain['mrri'],
                    "HRV_nn50": hrv_time_domain['nn50'],
                    "HRV_pnn50": hrv_time_domain['pnn50'],
                    "HRV_rmssd": hrv_time_domain['rmssd'],
                    "HRV_sdnn": hrv_time_domain['sdnn']
            }
    # Calculate frequency domain indexes
    try:
        hrv_freq_domain = hrv.classical.frequency_domain(rri, method='welch', interp_freq=4.0)
        hrv_features["HRV_hf"] = hrv_freq_domain["hf"]
        hrv_features["HRV_hfnu"] = hrv_freq_domain["hfnu"]
        hrv_features["HRV_lf"] = hrv_freq_domain["lf"]
        hrv_features["HRV_lf_hf"] = hrv_freq_domain["lf_hf"]
        hrv_features["HRV_lfnu"] = hrv_freq_domain["lfnu"]
        hrv_features["HRV_total_power"] = hrv_freq_domain["total_power"]
        hrv_features["HRV_vlf"] = hrv_freq_domain["vlf"]
    except:
        print("NeuroKit Error: ecg_process(): Signal to short to compute frequency domains HRV. Must me longer than 3.4 minutes.")


    # Store results
    processed_ecg = {"ECG": ecg_df,
                     "ECG_Features": {
                            "Heart_Beats": biosppy_ecg["templates"],
                            "ECG_R_Peaks": biosppy_ecg["rpeaks"],
                            "HRV": hrv_features}}

    # RSP
    if rsp is not None:
        biosppy_rsp = dict(biosppy.signals.resp.resp(rsp, sampling_rate=sampling_rate, show=False))
        processed_ecg["ECG"]["RSP_Raw"] = rsp
        processed_ecg["ECG"]["RSP_Filtered"] = biosppy_rsp["filtered"]

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
        processed_ecg["ECG"]["RSP_Rate"] = np.array(rsp_rate)*60  # From Hz to respiration per seconds

    return(processed_ecg)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_find_peaks(signal, sampling_rate=1000):
    """
    Find R peaks indices on the ECG channel.

    Parameters
    ----------
    signal = list or array
        ECG signal (preferably filtered).
    sampling_rate = int
        sampling_rate = int


    Returns
    ----------
    rpeaks
        List of R-peak location indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> Rpeaks = nk.ecg_find_Rpeaks(raw)

    Authors
    ----------
    Dominique Makowski, the biosppy dev team

    Dependencies
    ----------
    None
    """
    rpeaks, = biosppy.ecg.hamilton_segmenter(signal, sampling_rate=sampling_rate)
    return(rpeaks)
