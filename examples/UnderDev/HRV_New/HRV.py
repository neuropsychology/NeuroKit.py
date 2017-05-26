import pandas as pd
import biosppy
import numpy as np
import neurokit as nk

df = pd.read_csv("normal_ECG.csv")

bio = nk.ecg_process(df["ECG"])


