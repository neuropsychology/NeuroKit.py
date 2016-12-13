"""
Loading data submodule.
"""
from ..signal import select_events

import numpy as np
import pandas as pd
import mne
import os

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_load_raw(filename, path="", experiment="", eog=('HEOG', 'VEOG'), misc="auto", reference=None, montage="easycap-M1", preload=True):
    """
    Load EEG data into raw file.
    
    Parameters
    ----------
    filename = str
        File name (with or without the extension).
    path = str
        Data Directory.
    experiment = str
        Experiment name to be appenned after the filename (using an underscore; e.g., "participant_task1").
    eog = list
        Names of channels or list of indices that should be designated EOG channels. Values should correspond to the vhdr file Default is ('HEOG', 'VEOG').
    misc = list
        Names of channels or list of indices that should be designated MISC channels. Values should correspond to the electrodes in the vhdr file. If ‘auto’, units in vhdr file are used for inferring misc channels. Default is 'auto'.
    reference = str or list
        re-reference using specific sensors.
    montage = str
        see 
    preload = bool
        If True, all data are loaded at initialization. If False, data are not read until save.


    Returns
    ----------
    raw = mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.eeg_load_raw("", trigger_list)

    Authors
    ----------
    Dominique Makowski, the mne dev team.

    Dependencies
    ----------
    - mne
    """
    file = path + filename + experiment
    
    # Find correct file
    extension = filename.split(".")
    if len(extension) == 1:
        extension = None
    else:
        extension = "." + extension[-1]
    
    if extension is None:
        extension = ".vhdr"
    elif os.path.exists(file + extension) is False:
        extension = ".raw"
    elif os.path.exists(file + extension) is False:
        extension = ".set"
    elif os.path.exists(file + extension) is False:
        extension = ".fif"
    else:
        print("NeuroKit Error: eeg_load_raw(): couldn't find compatible format of data.")
        return()
        
    # Load the data
    try:
        if extension == ".vhdr":
            raw = mne.io.read_raw_brainvision(file + extension, eog=eog, misc=misc, montage=montage, preload=preload)
        elif extension == ".raw":
            raw = mne.io.read_raw_egi(file + extension, eog=eog, misc=misc, montage=montage, preload=preload)
        elif extension == ".set":
            raw = mne.io.read_raw_eeglab(file + extension, eog=eog, misc=misc, montage=montage, preload=preload)
        elif extension == ".fif":
            raw = mne.io.read_raw_fif(file + extension, eog=eog, misc=misc, montage=montage, preload=preload)
        else:
            print("NeuroKit Error: eeg_load_raw(): couldn't find compatible reader of data.")
    except FileNotFoundError:
        print("NeuroKit Error: eeg_load_raw(): something went wrong, check your the file name that is inside your info files (such as .vhdr, .vmrk, ...)")
        return()
    except:
        print("NeuroKit Error: eeg_load_raw(): error in data loading.")
        return()
        

    # Re-reference if needed
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
def eeg_add_events(raw, stim_channel, filename, path="", experiment="", treshold=0.04, upper=False, number=None, pause=None, after=0, before=None, conditions=None, order_column="Order"):
    """
    Create MNE compatible events.

    Parameters
    ----------
    raw = mne.io.Raw
        Raw EEG data.
    stim_channel = str
        Name of the stimuli channel.
    filename = str
        Name of the dataframe that contain the events.
    ...


    Returns
    ----------
    raw = mne.io.Raw
        The raw file with events.

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
    import neurokit as nk
    
    file = filename + "_" + experiment
    df = nk.read_data(file, path=path)
    # Sort the dataframe
    try:
        df = df.sort_values(order_column)
    except KeyError:
        print("NeuroKit Warning: add_events(): Wrong order_column provided. Dataframe will remain unsorted.")
    
    
        
    signal, time_index = raw.copy().pick_channels([stim_channel])[:]
    if pause is not None:
        after = pause
        before = pause
        number = int(number/2)
    events_onset, events_time = nk.select_events(signal[0],
                                            treshold=treshold,
                                            upper=upper,
                                            time_index=time_index,
                                            number=number,
                                            after=after,
                                            before=before)


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