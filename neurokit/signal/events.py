# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from itertools import groupby




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
def find_events(signal, treshold, upper=True, time_index=None):
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
    dict
        dict containing the onsets, the duration and the time index if provided.

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

    events = {"onsets":[], "length":[]}
    if time_index is not None:
        events["onsets_Time"] = []

    index = 0
    for key, g in (groupby(signal)):
        length = len(list(g))
        if key == 1:
            events["onsets"].append(index)
            events["length"].append(length)
            if time_index is not None:
                events["onsets_time"].append(time_index[index])
        index += length
    return(events)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def select_events(signal, treshold, upper=False, time_index=None, number="all", after=0, before=None, min_duration=1):
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
    min_duration = int
        The minimum duration of an event.

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
    events = find_events(signal, treshold=treshold, upper=upper, time_index=time_index)

    # Remove less than duration
    toremove = []
    for event in range(len(events["onsets"])):
        if events["length"][event] < min_duration:
            toremove.append(False)
        else:
            toremove.append(True)
    events["onsets"] = np.array(events["onsets"])[np.array(toremove)]
    events["length"] = np.array(events["length"])[np.array(toremove)]
    if time_index is not None:
        events["onsets_time"] = np.array(events["onsets_time"])[np.array(toremove)]

    return(events)
#    events_onset = events["onsets"]
#    events_length = events["length"]
#    if time_index is not None:
#        events_time = events["onsets_time"]


#    if isinstance(number, int):
#        after_times = []
#        after_onsets = []
#        before_times = []
#        before_onsets = []
#        if after != None:
#            if events_time == []:
#                events_time = np.array(events_onset)
#            else:
#                events_time = np.array(events_time)
#            after_onsets = list(np.array(events_onset)[events_time>after])[:number]
#            after_times = list(events_time[events_time>after])[:number]
#        if before != None:
#            if events_time == []:
#                events_time = np.array(events_onset)
#            else:
#                events_time = np.array(events_time)
#            before_onsets = list(np.array(events_onset)[events_time<before])[:number]
#            before_times = list(events_time[events_time<before])[:number]
#        events_onset = before_onsets + after_onsets
#        events_time = before_times + after_times
#
#        return(events_onset, events_time)
#    else:
#        return(events_onset, events_time)


