# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import nolds



df = pd.read_csv('data.csv')
df = nk.ecg_process(ecg=df["ECG"])
rri = df["ECG"]["RR_Intervals"]

#nolds.sampen(rri, 2, 0.1*np.std(rri), dist="euler")
#sample_entropy(rri,2, 0.1*np.std(rri))[1]
#
#
