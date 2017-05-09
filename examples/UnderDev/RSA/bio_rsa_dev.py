# -*- coding: utf-8 -*-
import biosppy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import neurokit as nk

plt.ion()

"""
Biopac's notice:
The software automatically measures the minimum and maximum R-R intervals during each respiration cycle. Breath-to-breath values are reported for the Cycle number, Time of the cycle, Minimum R-R interval, Maximum R-R interval and the Respiratory Sinus Arrhythmia value (difference between the minimum and maximum R-R intervals) with option to show logarithmic scaling of the result
https://www.biopac.com/?app-advanced-feature=respiratory-sinus-arrhythmia-rsa-analysis
See also this:
http://ieeexplore.ieee.org.sci-hub.cc/document/470252/?reload=true
"""







#==============================================================================
# TEST
#==============================================================================
data = pd.read_csv('clean_rsp.csv')
bio = nk.ecg_process(ecg=data["ECG"], rsp=data["RSP"])
df = bio["df"][["ECG_Filtered", "RSP_Raw", "RSP_Filtered", "RSP_Inspiration"]]
#
## Check RSP cycles onsets
#cycles_onsets = bio["RSP"]["Cycles_Onsets"]
## Plot only the 15s of data
#df[0:15000].plot()
#plt.plot(df.index[cycles_onsets][0:15000],
#         df['RSP_Filtered'][cycles_onsets][0:15000], 'ro')
#
#
#
#
#
## RSA
#rpeaks = bio["ECG"]["R_Peaks"]
#rsp_cycles = bio["RSP"]['Cycles_Onsets']
#rsp_signal = bio["df"]["RSP_Filtered"]
#
#RSA = bio_rsa(rpeaks, rsp_cycles, rsp_signal, sampling_rate=1000)
#
#df = df.reset_index(drop=True)
#df["RSA"] = RSA["RSA"]

# Plot only the 15s of data
df[0:15000].plot()



