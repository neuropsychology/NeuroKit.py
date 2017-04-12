# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import biosppy



df = pd.read_csv("data_rsa.csv")

sampling_rate = 1000
ecg_filtered = dict(biosppy.ecg.ecg(df["ECG"], show=False))["filtered"]
rpeaks = dict(biosppy.ecg.ecg(df["ECG"], show=False))["rpeaks"]
rsp_filtered = dict(biosppy.resp.resp(df["RSP"], show=False))["filtered"]
#resp_cycles = dict(biosppy.resp.resp(df["RSP"]))["zeros"]  # Returns zero crossings rather than beginning and end of cycles


"""
Biopac's notice:
The software automatically measures the minimum and maximum R-R intervals during each respiration cycle. Breath-to-breath values are reported for the Cycle number, Time of the cycle, Minimum R-R interval, Maximum R-R interval and the Respiratory Sinus Arrhythmia value (difference between the minimum and maximum R-R intervals) with option to show logarithmic scaling of the result

https://www.biopac.com/?app-advanced-feature=respiratory-sinus-arrhythmia-rsa-analysis
"""

# ==============================================================================
def bio_rsa(ecg_filtered, rsp_filtered, rpeaks, sampling_rate=1000):
    """
    Computation of Respiratory Sinus Arrythmia (RSA).

    Parameters
    ----------
    ecg_filtered =  array
        ECG signal array.
    rsp_filtered =  array
        Respiratory signal array.
    sampling_rate = int
        Sampling rate (samples/second).


    Returns
    ----------
    rsa = dict
        Dict containing RSA features.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>>

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - numpy
    - pandas

    """
    rri = np.diff(rpeaks)

    return()
# ==============================================================================


