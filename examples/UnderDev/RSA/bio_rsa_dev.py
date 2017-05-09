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
def bio_rsa(rpeaks, rsp_cycles, rsp_signal, sampling_rate=1000):

    # Find all RSP cycles and the Rpeaks within
    cycles_rri = []
    for idx in range(len(rsp_cycles) - 1):
        cycle_init = rsp_cycles[idx]
        cycle_end = rsp_cycles[idx + 1]
        cycles_rri.append(rpeaks[np.logical_and(rpeaks >= cycle_init,
                                                rpeaks < cycle_end)])

    # Iterate over all cycles
    RSA = []
    for cycle in cycles_rri:
        RRis = np.diff(cycle)/sampling_rate
        if len(RRis) > 1:
            RSA.append(np.max(RRis) - np.min(RRis))
        else:
            RSA.append(np.nan())


    # Continuous RSA
    current_rsa = np.nan

    continuous_rsa = []
    phase_counter = 0
    for i in range(len(rsp_signal)):
        if i == rsp_cycles[phase_counter]:
            current_rsa = RSA[phase_counter]
            if phase_counter < len(rsp_cycles)-2:
                phase_counter += 1
        continuous_rsa.append(current_rsa)

    # Find last phase
    continuous_rsa = np.array(continuous_rsa)
    continuous_rsa[max(rsp_cycles):] = np.nan

    RSA = {"RSA": continuous_rsa,
           "RSA_Values": RSA,
           "RSA_Mean": pd.Series(RSA).mean(),
           "RSA_Variability": pd.Series(RSA).std()}

    return(RSA)








#==============================================================================
# TEST
#==============================================================================
data = pd.read_csv('clean_rsp.csv')
bio = nk.ecg_process(ecg=data["ECG"], rsp=data["RSP"])
df = bio["df"][["ECG_Filtered", "RSP_Raw", "RSP_Filtered", "RSP_Inspiration"]]

# Check RSP cycles onsets
cycles_onsets = bio["RSP"]["Cycles_Onsets"]
# Plot only the 15s of data
df[0:15000].plot()
plt.plot(df.index[cycles_onsets][0:15000],
         df['RSP_Filtered'][cycles_onsets][0:15000], 'ro')





# RSA
rpeaks = bio["ECG"]["R_Peaks"]
rsp_cycles = bio["RSP"]['Cycles_Onsets']
rsp_signal = bio["df"]["RSP_Filtered"]

RSA = bio_rsa(rpeaks, rsp_cycles, rsp_signal, sampling_rate=1000)

df = df.reset_index(drop=True)
df["RSA"] = RSA["RSA"]

# Plot only the 15s of data
df[0:15000].plot()




