# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk



df = pd.read_csv('data.csv')
signal = df["ECG"].ix[0:5000]
df = nk.bio_process(ecg=signal, sampling_rate=1000)
events = df["ECG"]["Rpeaks"]
#
#
nk.visually_check_events_in_signal(signal, events)


