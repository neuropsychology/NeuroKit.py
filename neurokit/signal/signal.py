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
def create_epochs(signal, events_onset, sampling_rate, onset=-250, duration=1000, stimuli_name=None):
    """
    Create a dataframe of epoched data.

    Parameters
    ----------
    signal = array or list
        the signal.
    events_onset = list
        list of events onsets (see `events_onset()` function).
    sampling_rate = int
        Signal's sampling rate (samples/second).

    Returns
    ----------
    pandas' dataframe
        timepoints * epochs

    Example
    ----------
    >>> import neurokit as nk
    >>> epochs = nk.create_epochs(signal)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - numpy
    - pandas
    """
    length = int(sampling_rate * duration / 1000)
    length_onset =  int(sampling_rate * abs(onset) / 1000)

    events_onset = np.array(events_onset)
    events_onset = events_onset + onset


    epoch = 0
    data = {}
    for i in range(len(signal)):
        try:
            if i == events_onset[epoch]:
                data[epoch] = []
                j = 0
                for j in range(length):
                    data[epoch].append(signal[i+j])
                epoch += 1
        except IndexError:
            pass

    index = np.array(list(range(length)))-length_onset
    epochs = pd.DataFrame.from_dict(data)
    epochs.index = index
    if stimuli_name is not None:
        if len(list(set(stimuli_name))) != len(stimuli_name):
            print("Neuropsydia error: create_epochs(): stimuli names must be all different. See create_evoked()")
        else:
            epochs.columns = stimuli_name
    return(epochs)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def create_evoked(epochs, events, average=True):
    """
    Create a dictionary containing evoked data.

    Parameters
    ----------
    epochs : dataframe
        epoched data.
    events : list
        list of events types.
    average : bool
        Set True for collapsing the epoched.

    Returns
    ----------
    evoked : dic
        A dictionary containing one dataframe for each event.

    Example
    ----------
    >>> import neurokit as nk
    >>> events = ["emotion", "neutral", "emotion", "neutral"]
    >>> evoked = nk.create_evoked(epochs)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - numpy
    - pandas
    """
    index = epochs.index

    evoked = {}
    for event in set(events):
        evoked[event] = {}

    for event in enumerate(events):
        evoked[event[1]][event[0]] = epochs[event[0]]

    for event in evoked:
        evoked[event] = pd.DataFrame.from_dict(evoked[event])
        evoked[event].index = index
        if average == True:
            evoked[event] = evoked[event].mean(axis=1)
    return(evoked)

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
    >>> signal.plot()

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - scipy
    - pandas
    """
    # fit a 3rd degree spline on the data.
    spline = scipy.interpolate.splrep(x=value_times, y=values, k=3, s=0)  # s=0 guarantees that it will pass through ALL the given points
    # Get the values indexed per time
    signal = scipy.interpolate.splev(x=np.arange(0, value_times[-1], 1/sampling_rate), tck=spline, der=0)
    # Transform to series
    signal = pd.Series(signal)
    return(signal)