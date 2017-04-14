# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import datetime
import bioread

from ..miscellaneous import get_creation_date




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def read_acqknowledge(filename, path="", index="datetime", sampling_rate=1000, resampling_method="pad", fill_interruptions=True):
    """
    Read and Format a BIOPAC's AcqKnowledge file into a pandas' dataframe.

    Parameters
    ----------
    filename :  str
        Filename (with or without the extension) of a BIOPAC's AcqKnowledge file.
    path : str
        Data directory.
    index : str
        How to index the dataframe. "datetime" for aproximate datetime (based on the file creation/change) and "range" for a simple range index.
    sampling_rate : int
        Final sampling rate (samples/second).
    resampling_method : str
        The resampling method: "mean", "pad" or "bfill",
    fill_interruptions : bool
        Automatically fill the eventual signal interruptions using a backfill method.

    Returns
    ----------
    df : pandas.DataFrame()
        the acqknowledge file converted to a dataframe.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> df = nk.read_acqknowledge('file.acq')

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - pandas
    - bioread
    - datetime

    *See Also*

    - bioread package: https://github.com/njvack/bioread

    """
    # Check path
    file = path + filename
    if ".acq" not in file:
        file += ".acq"
    if os.path.exists(file) is False:
        print("NeuroKit Error: read_acqknowledge(): couldn't find the following file: " + filename)
        return()

    # Convert creation date
    creation_date = get_creation_date(file)
    creation_date = datetime.datetime.fromtimestamp(creation_date)


    # Read file
    file = bioread.read(file)


    # Get the channel frequencies
    freq_list = []
    for channel in file.named_channels:
        freq_list.append(file.named_channels[channel].samples_per_second)

    # Get data with max frequency and the others
    data = {}
    data_else = {}
    for channel in file.named_channels:
        if file.named_channels[channel].samples_per_second == max(freq_list):
            data[channel] = file.named_channels[channel].data
        else:
            data_else[channel] = file.named_channels[channel].data

    # Create index
    time = []
    beginning_date = creation_date - datetime.timedelta(0, max(file.time_index))
    for timestamps in file.time_index:
        time.append(beginning_date + datetime.timedelta(0, timestamps))
    df = pd.DataFrame(data, index=time)


    # Create resampling factor
    sampling_rate = str(int(1000/sampling_rate)) + "L"


    # max frequency must be 1000
    if data_else:  # if not empty
        for channel in data_else:
            channel_frequency = file.named_channels[channel].samples_per_second
            serie = data_else[channel]
            index = list(np.arange(0, max(file.time_index), 1/channel_frequency))
            index = index[:len(serie)]

            # Create index
            time = []
            for timestamps in index:
                time.append(beginning_date + datetime.timedelta(0, timestamps))
            data_else[channel] = pd.Series(serie, index=time)
        df2 = pd.DataFrame(data_else)


    # Resample
    if resampling_method == "mean":
        if data_else:
            df2 = df2.resample(sampling_rate).mean()
        df = df.resample(sampling_rate).mean()
    if resampling_method == "pad":
        if data_else:
            df2 = df2.resample(sampling_rate).pad()
        df = df.resample(sampling_rate).pad()
    if resampling_method == "bfill":
        if data_else:
            df2 = df2.resample(sampling_rate).bfill()
        df = df.resample(sampling_rate).bfill()
    if data_else:
        df = pd.concat([df, df2], 1)

    if index == "range":
        df = df.reset_index()

    # Fill signal interruptions
    df = df.fillna(method="backfill")

    return(df)
