# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from itertools import groupby




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def binarize_signal(signal, treshold="auto", cut="higher"):
    """
    Binarize a channel based on a continuous channel.

    Parameters
    ----------
    signal = array or list
        The signal channel.
    treshold = float
        The treshold value by which to select the events. If "auto", takes the value between the max and the min.
    cut = str
        "higher" or "lower", define the events as above or under the treshold. For photosensors, a white screen corresponds usually to higher values. Therefore, if your events were signalled by a black colour, events values would be the lower ones, and you should set the cut to "lower".

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
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    Dependencies
    ----------
    None
    """
    if treshold == "auto":
        treshold = (np.max(np.array(signal)) - np.min(np.array(signal)))/2
    signal = list(signal)
    binary_signal = []
    for i in range(len(signal)):
        if cut == "higher":
            if signal[i] > treshold:
                binary_signal.append(1)
            else:
                binary_signal.append(0)
        else:
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
def localize_events(events_channel, treshold="auto", cut="higher", time_index=None):
    """
    Find the onsets of all events based on a continuous signal.

    Parameters
    ----------
    events_channel = array or list
        The trigger channel.
    treshold = float
        The treshold value by which to select the events. If "auto", takes the value between the max and the min.
    cut = str
        "higher" or "lower", define the events as above or under the treshold. For photosensors, a white screen corresponds usually to higher values. Therefore, if your events were signalled by a black colour, events values would be the lower ones, and you should set the cut to "lower".
    time_index = array or list
        Add a corresponding datetime index, will return an addional array with the onsets as datetimes.

    Returns
    ----------
    dict
        dict containing the onsets, the duration and the time index if provided.

    Example
    ----------
    >>> import neurokit as nk
    >>> events_onset = nk.events_onset(events_channel)

    Authors
    ----------
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    Dependencies
    ----------
    None
    """
    events_channel = binarize_signal(events_channel, treshold=treshold, cut=cut)

    events = {"onsets":[], "durations":[]}
    if time_index is not None:
        events["onsets_time"] = []

    index = 0
    for key, g in (groupby(events_channel)):
        duration = len(list(g))
        if key == 1:
            events["onsets"].append(index)
            events["durations"].append(duration)
            if time_index is not None:
                events["onsets_time"].append(time_index[index])
        index += duration
    return(events)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_events(events_channel, treshold="auto", cut="higher", time_index=None, number="all", after=0, before=None, min_duration=1):
    """
    Find and select events based on a continuous signal.

    Parameters
    ----------
    events_channel : array or list
        The trigger channel.
    treshold : float
        The treshold value by which to select the events. If "auto", takes the value between the max and the min.
    cut : str
        "higher" or "lower", define the events as above or under the treshold. For photosensors, a white screen corresponds usually to higher values. Therefore, if your events were signalled by a black colour, events values would be the lower ones, and you should set the cut to "lower".
        Add a corresponding datetime index, will return an addional array with the onsets as datetimes.
    number : str or int
        How many events should it select.
    after : int
        If number different than "all", then at what time should it start selecting the events.
    before : int
        If number different than "all", before what time should it select the events.
    min_duration : int
        The minimum duration of an event (in timepoints).

    Returns
    ----------
    events : dict
        Dict containing events onsets and durations.

    Example
    ----------
    >>> import neurokit as nk
    >>> events = nk.select_events(events_channel)

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    """
    events = localize_events(events_channel, treshold=treshold, cut=cut, time_index=time_index)

    # Warning when no events detected
    if len(events["onsets"]) == 0:
        print("NeuroKit warning: find_events(): No events found. Check your events_channel or adjust trehsold.")
        return()

    # Remove less than duration
    toremove = []
    for event in range(len(events["onsets"])):
        if events["durations"][event] < min_duration:
            toremove.append(False)
        else:
            toremove.append(True)
    events["onsets"] = np.array(events["onsets"])[np.array(toremove)]
    events["durations"] = np.array(events["durations"])[np.array(toremove)]
    if time_index is not None:
        events["onsets_time"] = np.array(events["onsets_time"])[np.array(toremove)]

    # Before and after
    if isinstance(number, int):
        after_times = []
        after_onsets = []
        after_length = []
        before_times = []
        before_onsets = []
        before_length = []
        if after != None:
            if events["onsets_time"] == []:
                events["onsets_time"] = np.array(events["onsets"])
            else:
                events["onsets_time"] = np.array(events["onsets_time"])
            after_onsets = list(np.array(events["onsets"])[events["onsets_time"]>after])[:number]
            after_times = list(np.array(events["onsets_time"])[events["onsets_time"]>after])[:number]
            after_length = list(np.array(events["durations"])[events["onsets_time"]>after])[:number]
        if before != None:
            if events["onsets_time"] == []:
                events["onsets_time"] = np.array(events["onsets"])
            else:
                events["onsets_time"] = np.array(events["onsets_time"])
            before_onsets = list(np.array(events["onsets"])[events["onsets_time"]<before])[:number]
            before_times = list(np.array(events["onsets_time"])[events["onsets_time"]<before])[:number]
            before_length = list(np.array(events["durations"])[events["onsets_time"]<before])[:number]
        events["onsets"] = before_onsets + after_onsets
        events["onsets_time"] = before_times + after_times
        events["durations"] = before_length + after_length

    return(events)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def plot_events_in_signal(signal, events_onsets, color="red", marker=None):
    """
    Plot events in signal.

    Parameters
    ----------
    signal : array or DataFrame
        Signal array (can be a dataframe with many signals).
    events_onsets : list or ndarray
        Events location.
    color : int or list
        Marker color.
    marker : marker or list of markers (for possible marker values, see: https://matplotlib.org/api/markers_api.html)
        Marker type.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(ecg=signal, sampling_rate=1000)
    >>> events_onsets = bio["ECG"]["R_Peaks"]
    >>> plot_events_in_signal(bio["df"]["ECG_Filtered"], events_onsets)
    >>> plot_events_in_signal(bio["df"]["ECG_Filtered"], events_onsets, color="red", marker="o")
    >>> plot_events_in_signal(bio["df"]["ECG_Filtered"], [bio["ECG"]["P_Waves"], bio["ECG"]["R_Peaks"]], color=["blue", "red"], marker=["d","o"])

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    - `Renatosc <https://github.com/renatosc/>`_

    *Dependencies*

    - matplotlib
    - pandas
    """

    df = pd.DataFrame(signal)
    ax = df.plot()

    def plotOnSignal(x, color, marker=None):
        if (marker is None):
            plt.axvline(x=event, color=color)
        else:
            plt.plot(x, signal[x], marker, color=color)


    events_onsets = np.array(events_onsets)
    try:
        len(events_onsets[0])
        for index, dim in enumerate(events_onsets):
            for event in dim:
                plotOnSignal(x=event,
                             color=color[index] if isinstance(color, list) else color,
                             marker=marker[index] if isinstance(marker, list) else marker)
    except TypeError:
        for event in events_onsets:
            plotOnSignal(x=event,
                         color=color[0] if isinstance(color, list) else color,
                         marker=marker[0] if isinstance(marker, list) else marker)
    return ax

