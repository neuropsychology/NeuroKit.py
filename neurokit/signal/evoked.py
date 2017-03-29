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
def create_epochs(data, onsets, duration=1000, onset=-250, names=None):
    """
    Create epoched data.

    Parameters
    ----------
    data = dataframe
        In the form data*time.
    onsets = list
        A list of events onsets.
    duration = int or list
        Duration of each epoch.
    onset = int
        Where to start each epoch (in relation with each event onset).
    names = list
        Events names in order. Must contains uniques names. If not provided, will be replaced by event number.



    Returns
    ----------
    list
        binary_signal

    Example
    ----------
    >>> import neurokit as nk
    >>> binary_signal = nk.create_epochs(signal, treshold=4)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    # Adjust duration regarding onset
    if isinstance(duration, int):
        duration = np.array([duration-onset]*len(onsets))
    else:
        duration = np.array(duration) - onset

    # Check the events names
    if names is None:
        names = list(range(len(onsets)))
    else:
        if len(list(set(names))) != len(names):
            print("NeuroKit error: create_epochs(): events_names does not contain uniques names, replacing them by numbers.")
            names = list(range(len(onsets)))

    epochs = {}
    for event, event_onset in enumerate(onsets):
        event_onset += onset
        epochs[names[event]] = data[event_onset:event_onset+duration[event]]

    return(epochs)