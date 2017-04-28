import biosppy
import neurokit as nk
import pandas as pd
import numpy as np

emg = pd.DataFrame.from_csv("test.csv")
emg["EMG_1"] = emg["EMG"] + np.random.normal(scale=0.01, size=len(emg))

#df = nk.bio_process()
#emg = emg["EMG"]





#a = emg_process(emg, sampling_rate=1000, emg_names=["Sin", "Cosin"])
#
#visually_check_events_in_signal(a["df"], a["EMG_0"]["EMG_Pulse_Onsets"])
