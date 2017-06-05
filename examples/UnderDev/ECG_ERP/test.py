# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import biosppy
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
events = nk.find_events(df["Photosensor"], cut="lower")
epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+800, onset=-400)

Responses = {}
for i in epochs:
    epoch = epochs[i]
    Responses[i] = nk.bio_ERP(epoch, event_length=300, sampling_rate=100, window_post=4)


