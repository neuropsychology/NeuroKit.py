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
def create_epochs(data, events_onsets, duration=1000, onset=0, names=None):
    """
    Epoching a dataframe.

    Parameters
    ----------
    data : pandas.DataFrame
        Data*time.
    events_onsets : list
        A list of event onsets indices.
    duration : int or list
        Duration(s) of each epoch(s) (in time points).
    onset : int
        Epoch onset (in time points, relative to event onset).
    names : list
        Events names in order. Must contains uniques names. If not provided, will be replaced by event number.

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
    # Adjust duration regarding onset
    if isinstance(duration, int):
        duration = np.array([duration]*len(events_onsets))
    else:
        duration = np.array(duration)

    # Check the events names
    if names is None:
        names = list(range(len(events_onsets)))
    else:
        if len(list(set(names))) != len(names):
            print("NeuroKit error: create_epochs(): events_names does not contain uniques names, replacing them by numbers.")
            names = list(range(len(events_onsets)))

    # Create epochs
    epochs = {}
    for event, event_onset in enumerate(events_onsets):
        event_onset += onset
        epoch = data[event_onset:event_onset+duration[event]]
        epoch.index  = range(onset, duration[event] + onset)
        epochs[names[event]] = epoch

    return(epochs)