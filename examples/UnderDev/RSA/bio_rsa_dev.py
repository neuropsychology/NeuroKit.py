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


# ==============================================================================
def bio_rsa(rpeaks, rsp_zero_crossings):

    # Find all RSP cycles and the Rpeaks within
    cycles_rri = []
    for idx in range(len(rsp_zero_crossings) - 1):
        cycle_init = rsp_zero_crossings[idx]
        cycle_end = rsp_zero_crossings[idx + 1]
        cycles_rri.append(rpeaks[np.logical_and(rpeaks >= cycle_init,
                                                rpeaks < cycle_end)])

    # Iterate over all cycles
    RSA = []
    for cycle in cycles_rri:
        RRis = np.diff(cycle)
        if len(RRis < 2):
            RSA.append(np.max(RRis) - np.min(RRis))

    return(RSA)








#==============================================================================
# TEST
#==============================================================================
data = pd.read_csv('clean_rsp.csv')
processed_rsp = nk.ecg_process(ecg=data["ECG"], rsp=data["RSP"])
df = processed_rsp["df"][["ECG_Filtered", "RSP_Raw", "RSP_Filtered", "RSP_Inspiration"]]


# Check RSP cycles onsets
cycles_onsets = processed_rsp["RSP"]["Cycles_Onsets"]
df[0:15000].plot()
plt.plot(df.index[cycles_onsets][0:15000],
         df['RSP_Filtered'][cycles_onsets][0:15000], 'ro')
