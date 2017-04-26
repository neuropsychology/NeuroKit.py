import neurokit as nk
import pandas as pd
import matplotlib.pyplot as plt
import biosppy
import numpy as np
eda = pd.Series.from_csv("test_eda.csv")  # 100 Hz

#proc = nk.eda_process(eda, sampling_rate=100, use_cvxEDA=True, cvxEDA_normalize=True, cvxEDA_alpha=0.0008, cvxEDA_gamma=0.01)
proc = nk.eda_process(eda, sampling_rate=100, use_cvxEDA=False, cvxEDA_normalize=True, cvxEDA_alpha=0.0008, cvxEDA_gamma=0.01)


print(len(proc["EDA"]["SCR_Peaks_Indexes"]))

proc["df"].plot()
for i in proc["EDA"]["SCR_Peaks_Indexes"]:
    plt.axvline(i, color='red')
#
#eda2 = proc["df"]["EDA_Filtered"]
#scr = dict(biosppy.eda.basic_scr(eda2, sampling_rate=100))
#print(len(scr["peaks"]))
#
#
#onsets, peaks, amps = biosppy.eda.kbk_scr(eda2, sampling_rate=100)
#print(len(peaks))
#onsets, peaks, amps = biosppy.eda.basic_scr(eda2, sampling_rate=100)
#print(len(peaks))
