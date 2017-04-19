# -*- coding: utf-8 -*-
import biosppy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
        RSA.append(np.max(RRis) - np.min(RRis))

    return(RSA)







def _get_useful_signals(data, *cols):
    ecg = biosppy.ecg.ecg(data[cols[0]], show=False)
    rsp = biosppy.resp.resp(data[cols[1]], show=False)

    rpeaks = ecg['rpeaks']
    rsp_zero_crossings = rsp['zeros']

    return(ecg, rsp, rpeaks, rsp_zero_crossings)


# ==============================================================================

if __name__ == "__main__":
    data = pd.read_csv('noisy_rsp.csv')
    ecg, rsp, rpeaks, rsp_zero_crossings = _get_useful_signals(data, 'ECG','RSP')
    cycles_rri = bio_rsa(rpeaks, rsp_zero_crossings)

    # Some plots to check if the RRi found within the resp cycles are correct.
    # Later use tdd

    plt.figure()
    plt.plot(ecg['ts'], ecg['filtered'])
    plt.plot(rsp['ts'], rsp['filtered'], 'k')
    plt.plot(rsp['ts'][rsp_zero_crossings],
             rsp['filtered'][rsp_zero_crossings], 'ro')