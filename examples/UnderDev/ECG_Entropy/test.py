# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import nolds



df = pd.read_csv('data.csv')
df = nk.ecg_process(ecg=df["ECG"])


rri = df["ECG"]["RR_Intervals"]

signal=rri
tolerance = "default"
emb_dim=2
chaos = nk.complexity(signal, lyap_r=False, lyap_e=False)


#chaos = pd.Series(chaos)
#chaos.index = ["ECG_Complexity_" + s for s in chaos.index]
#processed_ecg["ECG"]["Complexity"] = chaos.to_dict()
#nolds.sampen(rri, 2, 0.1*np.std(rri), dist="euler")
#sample_entropy(rri,2, 0.1*np.std(rri))[1]
#
#
