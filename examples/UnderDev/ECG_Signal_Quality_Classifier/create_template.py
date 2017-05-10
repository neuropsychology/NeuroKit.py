import neurokit as nk
import numpy as np
import pandas as pd
import biosppy

data = read_nk_object("ecg-id_database.nk")

cycles = np.empty([0, 300])
for participant in data:
    bio = nk.ecg_process(data[participant]["ECG"], sampling_rate=500)
    cycles = np.concatenate((cycles, bio["ECG"]["Cardiac_Cycles"]))


df = pd.DataFrame(cycles).T.plot(legend=False)
