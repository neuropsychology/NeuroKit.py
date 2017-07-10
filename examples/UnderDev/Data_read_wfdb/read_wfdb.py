import pandas as pd
import numpy as np
import wfdb
import os

def read_physionet(filename):
    """
    Read and Format a Physiobank/Physionet's WFDB file into a pandas' dataframe.

    Parameters
    ----------
    filename :  str
        Filename (without the extensions) of a WFDB's set of files. For example, "rec_1" if you have 3 files rec_1.atr/rec_1.xyz, rec_1.dat and rec_1.hea.

    Returns
    ----------
    df, info : tuple
        The WFDB file converted to a dataframe and a dict containing additional info.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> df, info = nk.read_physionet('rec_1')

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - pandas
    - wfdb

    *See Also*

    - wfdb package: https://github.com/MIT-LCP/wfdb-python

    """
    # Read it
    data, info = wfdb.srdsamp(filename)

    # Convert to dataframe
    data = pd.DataFrame(data)
    data.columns = info["signame"]

    return(data, info)

data, info = read_physionet("data/rec_1")

data.plot()
sampling_rate = 1000

peak_indexes = wfdb.processing.gqrs_detect(x=data["ECG I filtered"], frequency=sampling_rate, adcgain=record.adcgain[0], adczero=record.adczero[0])




fs = fields['fs']
min_bpm = 10
max_bpm = 350
min_gap = fs*60/min_bpm
max_gap = fs*60/max_bpm
new_indexes = wfdb.processing.correct_peaks(x=sig[:,0], peak_indexes=peak_indexes, min_gap=min_gap, max_gap=max_gap, smooth_window=150)
#dblist = wfdb.getdblist()


#wfdb.dldatabasefiles('ecgiddb', os.getcwd(), ['/Person_04/rec_1.atr'])
