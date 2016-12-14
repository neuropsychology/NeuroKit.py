"""
Loading data submodule.
"""
from ..signal import select_events
from ..miscellaneous import read_data

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
#    event_index = [1, 2, 3, 4, 5, 32, 64, 128]
    event_index = list(range(len(event_names)))
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
def eeg_add_events(raw, stim_channel, treshold=0.04, upper=False, number=None, after=0, before=None, events_list=None, events_from_file=None, path="", experiment="", conditions=None, order_column="Order"):
    """
    Create MNE compatible events.

    Parameters
    ----------
    raw = mne.io.Raw
        Raw EEG data.
    stim_channel = str
        Name of the stimuli channel.
    events_from_file = str
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

    # Read the dataframe
    if events_from_file is not None:
        if experiment != "":
            experiment = "_" + experiment
        file = events_from_file + experiment
        df = read_data(file, path=path)

        # Sort the dataframe
        try:
            df = df.sort_values(order_column)
        except KeyError:
            print("NeuroKit Warning: add_events(): Wrong order_column provided. Dataframe will remain unsorted.")

        if number == "all":
            number = len(df)

        # Create dic of events
        if conditions is not None:

            # If only one name provided
            if isinstance(conditions, str):
                conditions = [conditions]

            triggers = {}
            for condition in list(conditions):
                triggers[condition] = df[condition][0:number]


            # create events_list
            events_list = []
            conditions_names = list(triggers.keys())

            # For each row, concatenate all conditions
            for row in range(len(triggers[conditions_names[0]])):
                element = ""
                for condition in conditions_names:
                    element += triggers[condition][row] + "/"
                events_list.append(element[:-1])  # Remove last "/"

        else:
            print("NeuroKit Warning: add_events(): No condition name(s) provided.")






    # Extract time serie from stim channel
    signal, time_index = raw.copy().pick_channels([stim_channel])[:]

    # Select events based on the treshold value
    events_onset, events_time = select_events(signal[0],
                                            treshold=treshold,
                                            upper=upper,
                                            time_index=time_index,
                                            number=number,
                                            after=after,
                                            before=before)

    # if events_list is None, replace with range
    if events_list is None and conditions is None:
        events_list = range(len(events_onset))



    events, event_id = eeg_create_events(events_onset, events_list)
    raw.add_events(events, stim_channel="STI 014")

    return(raw, events, event_id)


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