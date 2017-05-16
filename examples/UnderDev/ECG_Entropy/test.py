# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import pyrem
import nolds



df = pd.read_csv('data.csv')
df = nk.ecg_process(ecg=df["ECG"])


rri = df["ECG"]["RR_Intervals"]

signal=rri
tolerance = "default"
emb_dim=2
comp = nk.complexity(signal)



