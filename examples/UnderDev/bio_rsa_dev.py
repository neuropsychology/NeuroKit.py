# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import biosppy



df = pd.read_csv("data_rsa.csv")

sampling_rate = 1000
ecg = df["ECG"]
rsp = df["RSP"]



"""
Biopac's notice:
The software automatically measures the minimum and maximum R-R intervals during each respiration cycle. Breath-to-breath values are reported for the Cycle number, Time of the cycle, Minimum R-R interval, Maximum R-R interval and the Respiratory Sinus Arrhythmia value (difference between the minimum and maximum R-R intervals) with option to show logarithmic scaling of the result

https://www.biopac.com/?app-advanced-feature=respiratory-sinus-arrhythmia-rsa-analysis

See also this:
http://ieeexplore.ieee.org.sci-hub.cc/document/470252/?reload=true
"""

# ==============================================================================
def bio_rsa(ecg, rsp, sampling_rate=1000):

    # Compute useful features
    ecg_filtered = dict(biosppy.ecg.ecg(df["ECG"], show=False))["filtered"]
    rpeaks = dict(biosppy.ecg.ecg(df["ECG"], show=False))["rpeaks"]
    rsp_filtered = dict(biosppy.resp.resp(df["RSP"], show=False))["filtered"]
    rsp_zero_crossings = dict(biosppy.resp.resp(df["RSP"], show=False))["zeros"]


    # RR interval
    rri = np.diff(rpeaks)

    return()
# ==============================================================================


