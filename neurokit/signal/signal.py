# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

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
def binarize_signal(signal, treshold, upper=True):
    """
    Binarize a channel based on a continuous channel.

    Parameters
    ----------
    signal = array or list
        The signal channel.
    treshold = float
        The treshold.
    upper = bool
        Associate a 1 with a value above or under the treshold.

    Returns
    ----------
    list
        binary_signal

    Example
    ----------
    >>> import neurokit as nk
    >>> binary_signal = nk.binarize_signal(signal, treshold=4)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    signal = list(signal)
    binary_signal = []
    for i in range(len(signal)):
        if upper == True:
            if signal[i] > treshold:
                binary_signal.append(1)
            else:
                binary_signal.append(0)
        if upper == False:
            if signal[i] < treshold:
                binary_signal.append(1)
            else:
                binary_signal.append(0)
    return(binary_signal)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================

def find_events_onset(signal, treshold, upper=False, time_index=None):
    """
    Find the onsets of all events based on a continuous signal.

    Parameters
    ----------
    signal = array or list
        The signal channel.
    treshold = float
        The treshold.
    upper = bool
        Associate a 1 with a value above or under the treshold.
    time_index = array or list
        Add a corresponding datetime index, will return an addional array with the onsets as datetimes.

    Returns
    ----------
    list or tuple of lists
        events onsets

    Example
    ----------
    >>> import neurokit as nk
    >>> events_onset = nk.events_onset(signal, treshold=4)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    binary_data = binarize_signal(signal, treshold=treshold, upper=upper)

    events_time = []
    events_onset = []
    for i in range(len(binary_data)):
        if i > 0:
            if binary_data[i]==1 and binary_data[i-1]==0:
                events_onset.append(i)
                if time_index is not None:
                    events_time.append(time_index[i])
    if time_index is None:
        return(events_onset, events_time)
    else:
        return(events_onset, events_time)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================

def select_events(signal, treshold, upper=False, time_index=None, number="all", after=0, before=None):
    """
    Find and select events based on a continuous signal.

    Parameters
    ----------
    signal = array or list
        The signal channel.
    treshold = float
        The treshold.
    upper = bool
        Associate a 1 with a value above or under the treshold.
    time_index = array or list
        Add a corresponding datetime index, will return an addional array with the onsets as datetimes.
    number = str or int
        How many events should it select.
    after = int
        If number different than "all", then at what time should it start selecting the events.
    before = int
        If number different than "all", before what time should it select the events.

    Returns
    ----------
    list or tuple of lists
        events onsets

    Example
    ----------
    >>> import neurokit as nk
    >>> events_onset = nk.select_events(signal, treshold=4)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    events_onset, events_time = find_events_onset(signal, treshold=treshold, upper=upper, time_index=time_index)

    if isinstance(number, int):
        after_times = []
        after_onsets = []
        before_times = []
        before_onsets = []
        if after != None:
            if events_time == []:
                events_time = np.array(events_onset)
            else:
                events_time = np.array(events_time)
            after_onsets = list(np.array(events_onset)[events_time>after])[:number]
            after_times = list(events_time[events_time>after])[:number]
        if before != None:
            if events_time == []:
                events_time = np.array(events_onset)
            else:
                events_time = np.array(events_time)
            before_onsets = list(np.array(events_onset)[events_time<before])[:number]
            before_times = list(events_time[events_time<before])[:number]
        events_onset = before_onsets + after_onsets
        events_time = before_times + after_times

        return(events_onset, events_time)
    else:
        return(events_onset, events_time)





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
    epochs = dataframe
        epoched data.
    events = list
        list of events types.
    average = bool
        Set True for collapsing the epoched.

    Returns
    ----------
    dic
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

