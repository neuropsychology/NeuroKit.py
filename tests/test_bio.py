import pytest
import doctest
import os
import numpy as np
import pandas as pd
import neurokit as nk

 run_tests_in_local = False


#==============================================================================
# BIO
#==============================================================================
def test_read_acqknowledge():

    if run_tests_in_local is False:
        data_path = os.getcwd() + r"/tests/data/test_bio_data.acq"  # If running from travis
    else:
        data_path = "data/test_bio_data.acq"  # If running in local

    # Read data
    df, sampling_rate = nk.read_acqknowledge(data_path, return_sampling_rate=True)
    # Resample to 100Hz
    df = df.resample("10L").mean()
    df.columns = ['ECG', 'EDA', 'PPG', 'Photosensor', 'RSP']
    # Check length
    assert len(df) == 35645
    return(df)

# ---------------
def test_bio_process():

    df = test_read_acqknowledge()

    if run_tests_in_local is False:  # If travis
        ecg_quality_model = os.getcwd() + r"/neurokit/materials/heartbeat_classification.model"
    else:  # If local
        ecg_quality_model = "default"

    bio = nk.bio_process(ecg=df["ECG"], rsp=df["RSP"], eda=df["EDA"], sampling_rate=100, add=df["Photosensor"], ecg_quality_model=ecg_quality_model, age=24, sex="m", position="supine")

    assert len(bio) == 4
    return(bio)

if __name__ == '__main__':
#    nose.run(defaultTest=__name__)
    doctest.testmod()
    pytest.main()

