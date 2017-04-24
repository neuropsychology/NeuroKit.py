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
    ecg : list or array
        ECG signal array.
    rsp : list or array
        Respiratory signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    resampling_method : str
        "mean", "pad" or "bfill", the resampling method used for ECG and RSP heart rate.

    Returns
    ----------
    processed_ecg : dict
        Dict containing processed ECG features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, and the RSP filtered signal (if respiration provided).

        This function is mainly a wrapper for the biosppy.ecg.ecg() and the hrv.hrv() functions. Credits go to their authors.

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_ecg = nk.ecg_process(ecg_signal, resp_signal)

    Notes
    ----------
    *Details*

    - HRV: Heart-Rate Variability is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013).

       - SDNN is the standard deviation of the time interval between successive normal heart beats (i.e., the RR intervals). Reflects all influences on HRV including slow influences across the day, circadian variations, the effect of hormonal influences such as cortisol and epinephrine.
       - The RMSSD is the root mean square of the RR intervals (i.e., square root of the mean of the squared differences in time between successive normal heart beats). Reflects high frequency (fast or parasympathetic) influences on HRV (i.e., those influencing larger changes from one beat to the next).
       - VLF is the variance (i.e., power) in HRV in the Very Low Frequency (.003 to .04 Hz). Reflect an intrinsic rhythm produced by the heart which is modulated by primarily by sympathetic activity.
       - LF  is the variance (i.e., power) in HRV in the Low Frequency (.04 to .15 Hz). Reflects a mixture of sympathetic and parasympathetic activity, but in long-term recordings like ours, it reflects sympathetic activity and can be reduced by the beta-adrenergic antagonist propanolol (McCraty & Atkinson, 1996).
       - HF  is the variance (i.e., power) in HRV in the High Frequency (.15 to .40 Hz). Reflects fast changes in beat-to-beat variability due to parasympathetic (vagal) activity. Sometimes called the respiratory band because it corresponds to HRV changes related to the respiratory cycle and can be increased by slow, deep breathing (about 6 or 7 breaths per minute) (Kawachi et al., 1995) and decreased by anticholinergic drugs or vagal blockade (Hainsworth, 1995).

    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - biosppy
    - numpy
    - pandas

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy
    - hrv package: https://github.com/rhenanbartels/hrv

    References
    ------------
    - Zohar, A. H., Cloninger, C. R., & McCraty, R. (2013). Personality and heart rate variability: exploring pathways from personality to cardiac coherence and health. Open Journal of Social Sciences, 1(06), 32.
    """
    ecg_df = pd.DataFrame({"ECG_Raw": np.array(ecg)})

    # Compute several features using biosppy
    biosppy_ecg = dict(biosppy.signals.ecg.ecg(ecg, sampling_rate=sampling_rate, show=False))

    # Filtered signal
    ecg_df["ECG_Filtered"] = biosppy_ecg["filtered"]

    # Store R peaks indexes
    r_peaks = np.array([np.nan]*len(ecg))
    r_peaks[biosppy_ecg['rpeaks']] = 1
    ecg_df["ECG_Rpeaks"] = r_peaks


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

    # RR intervals (RRis)
    rri = np.diff(biosppy_ecg["rpeaks"])

    # Store results
    processed_ecg = {"df": ecg_df,
                     "ECG": {
                            "RRis": rri,
                            "Heart_Beats": biosppy_ecg["templates"],
                            "Rpeaks": biosppy_ecg["rpeaks"],
                            "HRV": np.nan
                            }}



    # HRV
    if sampling_rate == 1000:

        rri_time = np.cumsum(rri) / sampling_rate
        rri_time -= rri_time[0]

        # Calculate time domain indexes
        hrv_time_domain = hrv.classical.time_domain(rri)
        hrv_features = {"HRV_MHR": hrv_time_domain['mhr'],
                        "HRV_MRRI": hrv_time_domain['mrri'],
                        "HRV_NN50": hrv_time_domain['nn50'],
                        "HRV_PNN50": hrv_time_domain['pnn50'],
                        "HRV_RMSSD": hrv_time_domain['rmssd'],
                        "HRV_SDNN": hrv_time_domain['sdnn']
                }
        # Calculate frequency domain indexes
        try:
            hrv_freq_domain = hrv.classical.frequency_domain(rri, method='welch', interp_freq=4.0)
            hrv_features["HRV_HF"] = hrv_freq_domain["hf"]
            hrv_features["HRV_HFNU"] = hrv_freq_domain["hfnu"]
            hrv_features["HRV_LF"] = hrv_freq_domain["lf"]
            hrv_features["HRV_LF_HF"] = hrv_freq_domain["lf_hf"]
            hrv_features["HRV_LFNU"] = hrv_freq_domain["lfnu"]
            hrv_features["HRV_total_power"] = hrv_freq_domain["total_power"]
            hrv_features["HRV_VLF"] = hrv_freq_domain["vlf"]
        except:
            print("NeuroKit Error: ecg_process(): Signal to short to compute frequency domains HRV. Must me longer than 3.4 minutes.")

        processed_ecg["ECG"]["HRV"] = hrv_features
    else:
        print("NeuroKit Warning: ecg_process(): No HRV computation supported for sampling rates different from 1000Hz for now.")



    # RSP
    if rsp is not None:
        biosppy_rsp = dict(biosppy.signals.resp.resp(rsp, sampling_rate=sampling_rate, show=False))
        processed_ecg["df"]["RSP_Raw"] = rsp
        processed_ecg["df"]["RSP_Filtered"] = biosppy_rsp["filtered"]

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
        processed_ecg["df"]["RSP_Rate"] = np.array(rsp_rate)*60  # From Hz to respiration per seconds

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
    signal : list or array
        ECG signal (preferably filtered).
    sampling_rate : int
        sampling_rate = int


    Returns
    ----------
    rpeaks : list
        List of R-peaks location indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> Rpeaks = nk.ecg_find_peaks(signal)

    Notes
    ----------
    *Authors*

    - the bioSSPy dev team (https://github.com/PIA-Group/BioSPPy)

    *Dependencies*

    - biosppy

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy

    """
    rpeaks, = biosppy.ecg.hamilton_segmenter(signal, sampling_rate=sampling_rate)
    return(rpeaks)
