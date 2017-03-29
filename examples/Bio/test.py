# -*- coding: utf-8 -*-
import neurokit as nk
import pandas as pd
import numpy as np


df = pd.read_csv("data_bio.csv")
bio_features = nk.process_bio(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"])

df["ECG_Filtered"] = bio_features["ECG_Filtered"]
df["Heart_Rate"] = bio_features["Heart_Rate"]
df["RSP_Filtered"] = bio_features["RSP_Filtered"]
df["RSP_Rate"] = bio_features["RSP_Rate"]
df["EDA_Phasic"] = bio_features["EDA_Phasic"]




# Evoked
condition_list = ["Negative", "Neutral", "Neutral", "Neutral", "Negative", "Neutral", "Negative", "Negative"]


events = nk.find_events(df["Photosensor"], treshold = 3, cut="lower")

data = df
events_onsets = events["onsets"]
onset=-250


epochs = create_epochs(data, onsets=events["onsets"], duration=events["duration"])
