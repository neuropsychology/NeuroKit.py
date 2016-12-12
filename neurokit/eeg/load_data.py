"""
Loading data submodule.
"""
from ..signal import select_events

import numpy as np
import pandas as pd
import mne


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def load_brainvision_raw(participant, path="data/", experiment="", system="brainvision", reference=None):
    """
    """
    if system == "brainvision":
        extension = ".vhdr"
    raw = mne.io.read_raw_brainvision(path + participant + "/" + participant + "_" + experiment + extension, eog=('HEOG', 'VEOG'), misc=['PHOTO'], montage="easycap-M1", preload=True)
    if reference is None:
        raw.set_eeg_reference()
    else:
        raw.set_eeg_reference(reference)
    return(raw)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_create_events(events_onset, events_list):
    """
    Create MNE compatible events.

    Parameters
    ----------
    events_onset = list
        Events onset (from find_events() or select_events()).
    events_list = list
        A list of equal length containing the stimuli types/conditions.


    Returns
    ----------
    tuple
        events and a dictionary with event's names.

    Example
    ----------
    >>> import neurokit as nk
    >>> events_onset = nk.create_mne_events(events_onset, trigger_list)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    event_id = {}
    event_names = list(set(events_list))
    event_index = [1, 2, 3, 4, 5, 32]
    for i in enumerate(event_names):
        events_list = [event_index[i[0]] if x==i[1] else x for x in events_list]
        event_id[i[1]] = event_index[i[0]]

    events = np.array([events_onset, [0]*len(events_onset), events_list]).T
    return(events, event_id)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def add_events(raw, participant, path="data/", stimdata_extension=".xlsx", experiment="", stim_channel="PHOTO", treshold=0.04, upper=False, number=90, pause=None, after=0, before=None, conditions=None, order_column="Order"):
    """
    """
    signal, time_index = raw.copy().pick_channels([stim_channel])[:]
    if pause is not None:
        after = pause
        before = pause
    events_onset, events_time = select_events(signal[0],
                                            treshold=treshold,
                                            upper=upper,
                                            time_index=time_index,
                                            number=int(number/2),
                                            after=after,
                                            before=before)
    if stimdata_extension == ".xlsx":
        trigger_list = pd.read_excel(path + participant + "/" + participant + "_" + experiment + stimdata_extension)
    elif stimdata_extension == ".csv":
        trigger_list = pd.read_csv(path + participant + "/" + participant + "_" + experiment + stimdata_extension)
    else:
        print("NeuroKit Error: add_events(): Wrong stimdata_extension extension")

    # Sort the df
    try:
        trigger_list = trigger_list.sort_values(order_column)
    except KeyError:
        print("NeuroKit Warning: add_events(): Wrong order_column provided. Dataframe will remain unsorted.")

    if conditions is not None:
        triggers = {}
        for condition in list(conditions):
            triggers[condition] = trigger_list[condition][0:number-1]


        events_list = []
        conditions = triggers.keys()
        old_cond = conditions[0]
        for condition in conditions:
            if condition != old_cond:
                events_list = [m + "/" + n for m, n in zip(triggers[old_cond], triggers[condition])]
                old_cond = condition


        events, event_id = eeg_create_events(events_onset, events_list)
        raw.add_events(events, stim_channel="STI 014")
        return(raw, events, event_id)
    return(raw)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_load(participant, path="", experiment="", system="brainvision", reference=None, stimdata_extension=".xlsx", stim_channel="PHOTO", treshold=0.04, upper=False, number=45, pause=None, after=0, before=None, conditions=None, order_column="Order"):
    """
    """
    raw = load_brainvision_raw(participant, path=path, experiment=experiment, system=system, reference=reference)

    raw, events, event_id = add_events(raw=raw,
                                           participant=participant,
                                           path=path,
                                           stimdata_extension=stimdata_extension,
                                           experiment=experiment,
                                           stim_channel=stim_channel,
                                           treshold=treshold,
                                           upper=upper,
                                           number=number,
                                           pause=pause,
                                           after=after,
                                           before=before,
                                           conditions=conditions,
                                           order_column=order_column)
    return(raw, events, event_id)