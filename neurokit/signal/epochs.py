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
def create_epochs(data, events_onsets, sampling_rate=1000, duration=1, onset=0, index=None):
    """
    Epoching a dataframe.

    Parameters
    ----------
    data : pandas.DataFrame
        Data*time.
    events_onsets : list
        A list of event onsets indices.
    sampling_rate : int
        Sampling rate (samples/second).
    duration : int or list
        Duration(s) of each epoch(s) (in seconds).
    onset : int
        Epoch onset(s) relative to events_onsets (in seconds).
    index : list
        Events names in order that will be used as index. Must contains uniques names. If not provided, will be replaced by event number.

    Returns
    ----------
    epochs : dict
        dict containing all epochs.

    Example
    ----------
    >>> import neurokit as nk
    >>> epochs = nk.create_epochs(data, events_onsets)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - numpy
    """
    # Convert ints to arrays if needed
    if isinstance(duration, list) or isinstance(duration, np.ndarray):
        duration = np.array(duration)
    else:
        duration = np.array([duration]*len(events_onsets))

    if isinstance(onset, list) or isinstance(onset, np.ndarray):
        onset = np.array(onset)
    else:
        onset = np.array([onset]*len(events_onsets))

    if isinstance(data, list) or isinstance(data, np.ndarray) or isinstance(data, pd.Series):
        data = pd.DataFrame({"Signal": list(data)})

    # Store durations
    duration_in_s = duration.copy()
    onset_in_s = onset.copy()

    # Convert to timepoints
    duration = duration*sampling_rate
    onset = onset*sampling_rate



    # Create the index
    if index is None:
        index = list(range(len(events_onsets)))
    else:
        if len(list(set(index))) != len(index):
            print("NeuroKit Warning: create_epochs(): events_names does not contain uniques names, replacing them by numbers.")
            index = list(range(len(events_onsets)))
        else:
            index = list(index)


    # Create epochs
    epochs = {}
    for event, event_onset in enumerate(events_onsets):

        epoch_onset = int(event_onset + onset[event])
        epoch_end = int(event_onset+duration[event]+1)

        epoch = data[epoch_onset:epoch_end].copy()
        epoch.index  = np.linspace(start=onset_in_s[event], stop=duration_in_s[event], num=len(epoch), endpoint=True)


        relative_time = np.linspace(start=onset[event], stop=duration[event], num=len(epoch), endpoint=True).astype(int).tolist()
        absolute_time = np.linspace(start=epoch_onset, stop=epoch_end, num=len(epoch), endpoint=True).astype(int).tolist()

        epoch["Epoch_Relative_Time"] = relative_time
        epoch["Epoch_Absolute_Time"] = absolute_time

        epochs[index[event]] = epoch



    return(epochs)