"""
Loading data submodule.
"""
from ..signal import find_events
from ..miscellaneous import read_data
from .eeg_preprocessing import *

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
def read_eeg(filename, path="", eog=('HEOG', 'VEOG'), misc="auto", reference=None, montage="easycap-M1", preload=True, verbose="CRITICAL"):
    """
    Load EEG data into raw file.

    Parameters
    ----------
    filename = str
        File name (with or without the extension).
    path = str
        Data Directory.
    eog = list
        Names of channels or list of indices that should be designated EOG channels. Values should correspond to the vhdr file. Default is ('HEOG', 'VEOG'), but MNE's default is ('HEOGL', 'HEOGR', 'VEOGb').
    misc = list
        Names of channels or list of indices that should be designated MISC channels. Values should correspond to the electrodes in the vhdr file. If 'auto', units in vhdr file are used for inferring misc channels. Default is 'auto'.
    reference = str or list
        re-reference using specific sensors.
    montage = str
        Path or instance of montage containing electrode positions. If None, sensor locations are (0,0,0). See the documentation of mne.channels.read_montage() for more information.
    preload = bool
        If True, all data are loaded at initialization. If False, data are not read until save.
    verbose = str
        Level of verbosity. "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL".


    Returns
    ----------
    raw = mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.read_eeg("", trigger_list)

    Authors
    ----------
    Dominique Makowski, the mne dev team.

    Dependencies
    ----------
    - mne
    """
    file = path + filename

    # Find correct file
    extension = filename.split(".")
    if len(extension) == 1:
        extension = None
    else:
        extension = "." + extension[-1]

    if extension is None:
        extension = ".vhdr"
    if os.path.exists(file + extension) is False:
        extension = ".raw"
    if os.path.exists(file + extension) is False:
        extension = ".set"
    if os.path.exists(file + extension) is False:
        extension = ".fif"
    if os.path.exists(file + extension) is False:
        print("NeuroKit Error: read_eeg(): couldn't find compatible format of data.")
        return()

    # Load the data
    try:
        if extension == ".vhdr":
            raw = mne.io.read_raw_brainvision(file + extension, eog=eog, misc=misc, montage=montage, preload=preload, verbose=verbose)
        elif extension == ".raw":
            raw = mne.io.read_raw_egi(file + extension, eog=eog, misc=misc, montage=montage, preload=preload, verbose=verbose)
        elif extension == ".set":
            raw = mne.io.read_raw_eeglab(file + extension, eog=eog, misc=misc, montage=montage, preload=preload, verbose=verbose)
        elif extension == ".fif":
            raw = mne.io.read_raw_fif(file + extension, preload=preload, verbose=verbose)
        else:
            print("NeuroKit Error: read_eeg(): couldn't find compatible reader of data.")
            return()
    except FileNotFoundError:
        print("NeuroKit Error: read_eeg(): something went wrong, check the file names that are inside your info files (.vhdr, .vmrk, ...)")
        return()
    except:
        print("NeuroKit Error: read_eeg(): error in data loading.")
        return()


    # Re-reference if needed and if not MEG data
    if True not in ["MEG" in chan for chan in raw.info["ch_names"]]:
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
def eeg_add_channel(raw, channel, sync_by="start", channel_type=None):
    """
    Add a channel to a raw eeg file.

    Parameters
    ----------
    raw = mne.io.Raw
        Raw EEG data.
    channel = list or array
        The channel to be added.
    sync_by = str
        How to sync the two channels? "start", "end" or ...
    channel_type = str
        Channel type. currently supported fields are 'ecg', 'bio', 'stim', 'eog', 'misc', 'seeg', 'ecog', 'mag', 'eeg', 'ref_meg', 'grad', 'emg', 'hbr' or 'hbo'.
    sync_by =

    Returns
    ----------
    raw = mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.read_eeg("", trigger_list)

    Authors
    ----------
    Dominique Makowski, the mne dev team.

    Dependencies
    ----------
    - mne
    """
#    if sync_by in ["start", "end"]:
#        if len(channel) != len(raw):
#            print("NeuroKit Error: eeg_add_channel(): The two signals differ in size. Are you sure you want to sync them by " + sync_by + "?")
#
#    # Extract photosensor:
#    stim_channel_name = "PHOTO"
#    stim_channel, stim_channel_time_index = raw.copy().pick_channels([stim_channel_name])[:]
#    pd.Series(stim_channel[0]).plot()
#    import neurokit as nk
#    nk.localize_events(stim_channel[0])
#
#
#    import neurokit as nk
#    nk.find_events()






    raw.info["sfreq"]
    raw.copy().pick_channels([stim_channel])[:]

    if raw.info["sfreq"] != new_channel_frequency:
        print("NeuroKit Error: eeg_add_channel(): different sampling rates detected between eeg data and new channel.")
        return()

    if len(np.array(raw_events).shape) == 1:
        raw_events_onset = list(raw_events)
    elif len(np.array(raw_events).shape) == 2:
        raw_events_onset = list(raw_events[:,0])
    else:
        print("NeuroKit Error: eeg_add_channel(): raw_events must be a list of onsets or an events object returned by eeg_add_events().")
        return()

    event1_new = new_channel_events_onset[0]
    event1_raw = raw_events_onset[0]

    index = np.array(new_channel.index)
    index = index - (event1_new - event1_raw)
    new_channel.index = index

    if event1_new > event1_raw:
        channel = list(new_channel.ix[0:])
    if event1_new < event1_raw:
        channel = [np.nan] * (event1_raw-event1_new) + list(new_channel)

    random_channel, time_index = raw.copy().pick_channels([raw.info['ch_names'][0]])[:]
    if len(channel) > len(random_channel[0]):
        channel = list(channel)[:len(random_channel[0])]
    if len(channel) < len(random_channel[0]):
        channel = list(channel) + [np.nan] * (len(len(random_channel[0])-len(channel)))

    info = mne.create_info([new_channel_type], new_channel_frequency, ch_types=new_channel_type)
    channel = mne.io.RawArray([channel], info)

    raw.add_channels([channel], force_update_info=True)

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
        Events onset (from find_events() or find_events()).
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
def eeg_add_events(raw, stim_channel_name, treshold=0.04, cut="higher", number=None, after=0, before=None, events_list=None, events_from_file=None, path="", experiment="", conditions=None, order_column="Order", events_channel="STI 014"):
    """
    Create MNE compatible events.

    Parameters
    ----------
    raw = mne.io.Raw
        Raw EEG data.
    stim_channel_name = str
        Name of the trigger channel.
    treshold = float
        The treshold value by which to select the events.
    cut = str
        "higher" or "lower", define the events as above or under the treshold.
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
    events_onset, events_time = find_events(signal[0],
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
    raw.add_events(events, stim_channel=events_channel)

    return(raw, events, event_id)







# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_create_raws(filename, path, participants=None, runs=None, lowpass_filter=None, highpass_filter=None, notch_filter=False, ica_eog=False, ica_ecg=False, resample=False):
    """
    """
    if participants is None:
        participants = os.listdir(path)

    raws = {}  # Initialize empty dic
    for participant in participants:

        if runs is None:
            runs = os.listdir(path + "/" + participant + "/")

        raws[participant] = {}
        for run in runs:
            # Load the participant's file into a raw object
            raw = eeg_load_raw(filename=filename, path=path + "/" + participant + "/" + run + "/")
            # Filter and downsample
            raw = eeg_filter(raw, lowpass=lowpass_filter, highpass=highpass_filter, notch=notch_filter)

            # Apply ICA to remove EOG and ECG artifacts
            raw, ica = eeg_ica(raw, eog=ica_eog, ecg=ica_ecg)

            # Resample to 125 points/s
            raw = raw.resample(resample)

            # Add data to dict
            raws[participant][run] = raw

    return(raws)

