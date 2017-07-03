# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import scipy

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def extract_peak(channel_data, value="max", size=0):
    """
    Extract the peak (max or min) of one or several channels.

    Parameters
    ----------
    channel_data = pandas.DataFrame
        Use the `to_data_frame()` method for evoked nme data.
    value = str
        "max" or "min".
    size = int
        Return an averaged peak from how many points before and after.

    Returns
    ----------
    tuple
        (peak, time_peak)

    Example
    ----------
    >>> channel_data = evoked.pick_channels(["C1", "C2"]).to_data_frame()
    >>> peak, time_peak = nk.extract_peak(channel_data, size=2)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - numpy
    - pandas
    """
    data = channel_data.mean(axis=1)
    data.plot()
    if value == "max":
        peak = np.max(data)
        time_peak = np.argmax(data)
    if value == "min":
        peak = np.min(data)
        time_peak = np.argmin(data)
    if size > 0:
        peak_list = [peak]
        peak_index = list(data.index).index(time_peak)
        data = data.reset_index(drop=True)
        for i in range(size):
            peak_list.append(data[peak_index+int(i+1)])
            peak_list.append(data[peak_index-int(i-1)])
        peak = np.mean(peak_list)
    return(peak, time_peak)







# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def discrete_to_continuous(values, value_times, sampling_rate=1000):
    """
    3rd order spline interpolation.

    Parameters
    ----------
    values : dataframe
        Values.
    value_times : list
        Time indices of values.
    sampling_rate : int
        Sampling rate (samples/second).

    Returns
    ----------
    signal : pd.Series
        An array containing the values indexed by time.

    Example
    ----------
    >>> import neurokit as nk
    >>> signal = discrete_to_continuous([4, 5, 1, 2], [1, 2, 3, 4], sampling_rate=1000)
    >>> pd.Series(signal).plot()

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - scipy
    - pandas
    """
#    values=heart_rate.copy()
#    value_times=heart_rate_times.copy()
    # Preprocessing
    initial_index = value_times[0]
    value_times = np.array(value_times) - initial_index

    # fit a 3rd degree spline on the data.
    spline = scipy.interpolate.splrep(x=value_times, y=values, k=3, s=0)  # s=0 guarantees that it will pass through ALL the given points
    x = np.arange(0, value_times[-1], 1)
    # Get the values indexed per time
    signal = scipy.interpolate.splev(x=x, tck=spline, der=0)
    # Transform to series
    signal = pd.Series(signal)
    signal.index = np.array(np.arange(initial_index, initial_index+len(signal), 1))

    return(signal)