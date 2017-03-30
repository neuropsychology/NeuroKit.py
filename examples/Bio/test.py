# -*- coding: utf-8 -*-
import neurokit as nk
import pandas as pd
import numpy as np


df = pd.read_csv("data_bio.csv")
eda = df["EDA"]
ecg = df["ECG"]
rsp = df["RSP"]
processed_ecg = process_ecg(df["ECG"], df["RSP"])
processed_eda = process_eda(eda, use_cvxEDA=False)

events = nk.find_events(df["Photosensor"], 3, cut="lower")


epochs = create_epochs(processed_eda["EDA_Processed"], events["onsets"], duration=5000)

amplitudes = []
for epoch in epochs:
    amplitudes.append(epochs[epoch]["SCR_Peaks"].mean())
amplitudes
#bio_features = nk.process_bio(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"])
#
#df["ECG_Filtered"] = bio_features["ECG_Filtered"]
#df["Heart_Rate"] = bio_features["Heart_Rate"]
#df["RSP_Filtered"] = bio_features["RSP_Filtered"]
#df["RSP_Rate"] = bio_features["RSP_Rate"]
#df["EDA_Phasic"] = bio_features["EDA_Phasic"]
#
#
#
#
## Evoked
condition_list = ["Negative", "Neutral", "Neutral", "Neutral", "Neutral", "Negative", "Negative", "Neutral"]
#
#
#events = nk.find_events(df["Photosensor"], treshold = 3, cut="lower")
#
#data = df
#events_onsets = events["onsets"]
#onset=-250
#duration=5000
#names=None
#
#events_onsets = events["onsets"]
#
#epoch = epochs[1]
#epochs = nk.create_epochs(data, onsets=events["onsets"], duration=5000)
