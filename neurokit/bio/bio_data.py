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
def acq_to_df(filename, path="", index="datetime", sampling_rate=1000, resampling_method="mean"):
    """
    Format a BIOPAC's AcqKnowledge file into a pandas' dataframe.

    Parameters
    ----------
    filename =  str
        File name (with or without the extension) of a BIOPAC's AcqKnowledge file.
    path = str
        Data Directory.
    index = str
        How to index the dataframe. "datetime" for aproximate datetime (based on the file creation/change) and "range" for a simple range index.
    sampling_rate = int
        final sampling rate (samples/second).
    resampling_method = str
        "mean" or "pad", resampling method.

    Returns
    ----------
    df = pandas.DataFrame()
        the dataframe


    Example
    ----------
    >>> import neuropsydia as n
    >>> n.start(False)
    >>>
    >>> df = acq_to_df('file.acq')

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - pandas
    - bioread
    - datetime
    """
    # Check path
    file = path + filename
    if ".acq" not in file:
        file += ".acq"
    if os.path.exists(file) is False:
        print("NeuroKit Error: acq_to_df(): couldn't find the following file: " + filename)
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
    if data_else:
        df = pd.concat([df, df2], 1)

    if index == "range":
        df = df.reset_index()

    return(df)
