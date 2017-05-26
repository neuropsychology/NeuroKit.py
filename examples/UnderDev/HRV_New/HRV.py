import pandas as pd
import biosppy
import numpy as np


df = pd.read_csv("normal_ECG.csv")

rpeaks = dict(biosppy.ecg.ecg(df["ECG"], show=False))["rpeaks"]
rri = np.diff(rpeaks)


