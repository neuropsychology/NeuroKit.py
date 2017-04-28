import neurokit as nk
import pandas as pd
import numpy as np
import matplotlib
import seaborn as sns
import biosppy

df = pd.read_csv("https://raw.githubusercontent.com/neuropsychology/NeuroKit.py/master/examples/Bio/data/bio_rest.csv")
events = nk.find_events(df["Photosensor"], cut="lower")

df = nk.create_epochs(df, events["onsets"], duration=events["durations"], onset=0)
df = df[0]  # Select the first element of that list.

bio = nk.bio_process(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"], add=df["Photosensor"])
#
#ecg = nk.ecg_process(ecg=df["ECG"])
#
#biosppy_ecg = biosppy.ecg.ecg(df["ECG"], show=False)
#rri = np.diff(biosppy_ecg["rpeaks"])
#
#
