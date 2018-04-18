import os
import re
import numpy as np
import pandas as pd
import wfdb
import neurokit as nk
import seaborn as sns
import matplotlib.pyplot as plt


"""
The data from the PTB-Diagnostic-ECG database must be in a data folder.
- data_creation.py
- model_creation.py
- data/
    - patient001/
    - patient002/
    - ...
"""


#==============================================================================
# Extracting
#==============================================================================
data={"Control": {}, "Patient": {}}
participants = [x for x in os.listdir("./data/") if 'patient' in x]
for participant in participants:
    files = os.listdir("./data/" + participant)
    if len([x for x in files if '.dat' in x]) > 0:
        file = [x for x in files if '.dat' in x][0].split(".")[0]
        signals, info = wfdb.rdsamp("data/" + participant + "/" + file)

        signals = pd.DataFrame(signals)
        signals.columns = info["sig_name"]

        data_participant = {}
        data_participant["Signals"] = signals
        data_participant["sampling_rate"] = info["fs"]


        for key in info["comments"]:
            try:
                data_participant[key.split(": ")[0]] = key.split(": ")[1]
            except IndexError:
                data_participant[key.split(":")[0]] = np.nan

        if data_participant["Reason for admission"] in ["n/a", "Healthy control"]:
            data["Control"][participant] = data_participant
        else:
            data["Patient"][participant] = data_participant


##==============================================================================
## Save
##==============================================================================
nk.save_nk_object(data, path="./", filename="PTB-Diagnostic_database-ECG", compress=True)
