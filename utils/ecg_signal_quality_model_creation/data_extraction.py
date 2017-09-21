"""
This transforms a database of ECG signals into into a formatted file.
"""
import os
import numpy as np
import pandas as pd
import wfdb
import neurokit as nk

#==============================================================================
# Setup
#==============================================================================
path = "./" + "/" # Path of the database folder. Do not forget the "/" at the end.
database = "PTB"  # Shoud it use the PTB-Diagnostic-ECG raw data (https://www.physionet.org/physiobank/database/ptbdb/)


#==============================================================================
# Extraction - PTB
#==============================================================================
if database == "PTB":
    data={"Control": {}, "Patient": {}}
    participants = [x for x in os.listdir(path) if 'patient' in x]
    for participant in participants:
        files = os.listdir(path + participant)
        if len([x for x in files if '.dat' in x]) > 0:
            file = [x for x in files if '.dat' in x][0].split(".")[0]
            signals, info = wfdb.srdsamp(path + participant + "/" + file)

            signals = pd.DataFrame(signals)
            signals.columns = info["signame"]

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

else:
    print("Other database not supported for now")

##==============================================================================
## Save
##==============================================================================
nk.save_nk_object(data, path="./", filename="PTB-Diagnostic_database-ECG", compress=True)
