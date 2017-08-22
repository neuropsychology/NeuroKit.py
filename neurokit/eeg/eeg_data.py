"""
Loading data and events submodule.
"""
from ..signal import find_events

import numpy as np
import pandas as pd
import mne
import os
import re

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
    Load EEG data into mne.io.Raw file.

    Parameters
    ----------
    filename : str
        Filename.
    path : str
        File's path.
    eog : list
        Names of channels or list of indices that should be designated EOG channels. Values should correspond to the vhdr file. Default is ('HEOG', 'VEOG'), but MNE's default is ('HEOGL', 'HEOGR', 'VEOGb').
    misc : list
        Names of channels or list of indices that should be designated MISC channels. Values should correspond to the electrodes in the vhdr file. If 'auto', units in vhdr file are used for inferring misc channels. Default is 'auto'.
    reference : str or list
        re-reference using specific sensors.
    montage : str
        Path or instance of montage containing electrode positions. If None, sensor locations are (0,0,0). See the documentation of mne.channels.read_montage() for more information.
    preload : bool
        If True, all data are loaded at initialization. If False, data are not read until save.
    verbose : str
        Level of verbosity. "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL".


    Returns
    ----------
    raw : mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.read_eeg("filename")

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - mne

    *See Also*

    - mne package: http://martinos.org/mne/dev/index.html
    """
    file = path + filename

    # Find correct file
    extension = filename.split(".")
    if len(extension) == 1:
        extension = None
    else:
        extension = "." + extension[-1]

    if extension in [".vhdr", ".raw", ".set", ".fif", ".edf"]:
        file = file.split(".")[0]
    else:
        if extension is None:
            extension = ".vhdr"
        if os.path.exists(file + extension) is False:
            extension = ".raw"
        if os.path.exists(file + extension) is False:
            extension = ".set"
        if os.path.exists(file + extension) is False:
            extension = ".fif"
        if os.path.exists(file + extension) is False:
            extension = ".edf"
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
        elif extension == ".edf":
            raw = mne.io.read_raw_edf(file + extension, preload=preload, verbose=verbose)
        else:
            print("NeuroKit Error: read_eeg(): couldn't find compatible reader of data. Try to do it manually using mne.")

        # Re-reference if needed and if not MEG data
        if True not in ["MEG" in chan for chan in raw.info["ch_names"]]:
            if reference is None:
                raw.set_eeg_reference()
            else:
                raw.set_eeg_reference(reference)

    except KeyError:
        print("NeuroKit Error: read_eeg(): something went wrong. This might be because you have channel names that are missing from the montage definition. Try do read data manually using mne.")
    except FileNotFoundError:
        print("NeuroKit Error: read_eeg(): something went wrong, check the file names that are inside your info files (.vhdr, .vmrk, ...)")
    except:
        print("NeuroKit Error: read_eeg(): error in data loading. Try to do it manually using mne.")


    return(raw)






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_add_channel(raw, channel, sync_index_raw=0, sync_index_channel=0, channel_type=None, channel_name=None):
    """
    Add a channel to a raw m/eeg file.

    Parameters
    ----------
    raw : mne.io.Raw
        Raw EEG data.
    channel : list or numpy.array
        The channel to be added.
    sync_index_raw : int or list
        The index by which to align the two inputs.
    sync_index_channel : int or list
        The index by which to align the two inputs.
    channel_type : str
        Channel type. Currently supported fields are 'ecg', 'bio', 'stim', 'eog', 'misc', 'seeg', 'ecog', 'mag', 'eeg', 'ref_meg', 'grad', 'emg', 'hbr' or 'hbo'.

    Returns
    ----------
    raw : mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.eeg_add_channel(raw, ecg, channel_type="ecg")

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - mne

    *See Also*

    - mne: http://martinos.org/mne/dev/index.html
    """
    if channel_name is None:
        if isinstance(channel, pd.core.series.Series):
            if channel.name is not None:
                channel_name = channel.name
            else:
                channel_name = "Added_Channel"
        else:
            channel_name = "Added_Channel"

    # Compute the distance between the two signals
    diff = sync_index_channel - sync_index_raw
    if diff > 0:
        channel = list(channel)[diff:len(channel)]
        channel = channel + [np.nan]*diff
    if diff < 0:
        channel = [np.nan]*diff + list(channel)
        channel = list(channel)[0:len(channel)]

    # Adjust to raw size
    if len(channel) < len(raw):
        channel = list(channel) + [np.nan]*(len(raw)-len(channel))
    else:
        channel = list(channel)[0:len(raw)]  # Crop to fit the raw data

    info = mne.create_info([channel_name], raw.info["sfreq"], ch_types=channel_type)
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
def eeg_select_channels(raw, channel_names):
    """
    Select one or several channels by name and returns them in a dataframe.

    Parameters
    ----------
    raw : mne.io.Raw
        Raw EEG data.
    channel_names : str or list
        Channel's name(s).

    Returns
    ----------
    channels : pd.DataFrame
        Channel.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.eeg_select_channel(raw, "TP7")

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - mne

    *See Also*

    - mne package: http://martinos.org/mne/dev/index.html
    """
    if isinstance(channel_names, list) is False:
        channel_names = [channel_names]

    channels, time_index = raw.copy().pick_channels(channel_names)[:]
    if len(channel_names) > 1:
        channels = pd.DataFrame(channels.T, columns=channel_names)
    else:
        channels = pd.Series(channels[0])
        channels.name = channel_names[0]
    return(channels)










# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_create_events(onsets, conditions=None):
    """
    Create MNE compatible events.

    Parameters
    ----------
    onsets : list or array
        Events onsets.
    conditions : list
        A list of equal length containing the stimuli types/conditions.


    Returns
    ----------
    (events, event_id) : tuple
        MNE-formated events and a dictionary with event's names.

    Example
    ----------
    >>> import neurokit as nk
    >>> events, event_id = nk.create_mne_events(events_onset, trigger_list)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    event_id = {}

    if conditions is None:
        conditions = ["Event"] * len(onsets)

    # Sanity check
    if len(conditions) != len(onsets):
        print("NeuroKit Warning: eeg_create_events(): conditions parameter of different length than onsets. Aborting.")
        return()



    event_names = list(set(conditions))
#    event_index = [1, 2, 3, 4, 5, 32, 64, 128]
    event_index = list(range(len(event_names)))
    for i in enumerate(event_names):
        conditions = [event_index[i[0]] if x==i[1] else x for x in conditions]
        event_id[i[1]] = event_index[i[0]]

    events = np.array([onsets, [0]*len(onsets), conditions]).T
    return(events, event_id)






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_add_events(raw, events_channel, conditions=None, treshold="auto", cut="higher", time_index=None, number="all", after=0, before=None, min_duration=1):
    """
    Create MNE compatible events.

    Parameters
    ----------
    raw : mne.io.Raw
        Raw EEG data.
    events_channel : str or array
        Name of the trigger channel if in the raw, or array of equal length if externally supplied.
    conditions : list
        List containing the stimuli types/conditions.
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
    (raw, events, event_id) : tuple
        The raw file with events, the mne-formatted events and event_id.

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> raw, events, event_id = nk.eeg_add_events(raw, events_channel, conditions)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - pandas

    *See Also*

    - mne: http://martinos.org/mne/dev/index.html


    References
    -----------
    - None
    """
    # Extract the events_channel from raw if needed
    if isinstance(events_channel, str):
        try:
            events_channel = eeg_select_channels(raw, events_channel)
        except:
            print("NeuroKit error: eeg_add_events(): Wrong events_channel name provided.")

    # Find event onsets
    events = find_events(events_channel, treshold=treshold, cut=cut, time_index=time_index, number=number, after=after, before=before, min_duration=min_duration)

    # Create mne compatible events
    events, event_id = eeg_create_events(events["onsets"], conditions)

    # Add them
    raw.add_events(events)

    return(raw, events, event_id)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_to_all_evokeds(all_epochs):
    """
    Convert all_epochs to all_evokeds.
    """
    # Get event_id
    event_id = {}
    for participant, epochs in all_epochs.items():
        event_id.update(epochs.event_id)

    all_evokeds = {}
    for participant, epochs in all_epochs.items():
        evokeds = dict((cond, epochs[cond].average()) for cond in event_id)
        all_evokeds[participant] = evokeds

    return(all_evokeds)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_to_df(eeg, index=None, include="all", exclude=None, hemisphere="both", central=True):
    """
    Convert mne Raw or Epochs object to dataframe or dict of dataframes.
    """
    if isinstance(eeg, mne.Epochs):
        data = {}

        if index is None:
            index=range(len(eeg))

        for epoch_index, epoch in zip(index, eeg.get_data()):

            epoch = pd.DataFrame(epoch.T)
            epoch.columns = eeg.ch_names
            epoch.index = eeg.times

            selection = eeg_select_electrodes(eeg, include=include, exclude=exclude, hemisphere=hemisphere, central=central)

            data[epoch_index] = epoch[selection]

    else:  # it might be a Raw object
        data = eeg.get_data().T
        data = pd.DataFrame(data)
        data.columns = eeg.ch_names
        data.index = eeg.times

    return(data)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_select_electrodes(eeg, include="all", exclude=None, hemisphere="both", central=True):
    """
    Returns electrodes/sensors names of selected region (according to a 10-20 EEG montage).

    Parameters
    ----------
    eeg : mne.Raw or mne.Epochs
        EEG data.
    include : str ot list
        Sensor area to include.
    exclude : str or list or None
        Sensor area to exclude.
    hemisphere : str
        Select both hemispheres? "both", "left" or "right".
    central : bool
        Select the central line.

    Returns
    ----------
    electrodes : list
        List of electrodes/sensors corresponding to the selected area.

    Example
    ----------
    >>> import neurokit as nk
    >>> nk.eeg_select_electrodes(include="F", exclude="C")


    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    """
    # Get all channel names
    eeg = eeg.copy().pick_types(meg=False, eeg=True)
    channel_list = eeg.ch_names

    # Include
    if include == "all":
        electrodes = channel_list
    elif isinstance(include, str):
        electrodes = [s for s in channel_list if include in s]
    elif isinstance(include, list):
        electrodes = []
        for i in include:
            electrodes += [s for s in channel_list if i in s]
    else:
        print("NeuroKit Warning: eeg_select_electrodes(): 'include' parameter must be 'all', str or list.")

    # Exclude
    if exclude is not None:
        if isinstance(exclude, str):
            to_remove = [s for s in channel_list if exclude in s]
            electrodes = [s for s in electrodes if s not in to_remove]
        elif isinstance(exclude, list):
            to_remove = []
            for i in exclude:
                to_remove += [s for s in channel_list if i in s]
            electrodes = [s for s in electrodes if s not in to_remove]
        else:
            print("NeuroKit Warning: eeg_select_electrodes(): 'exclude' parameter must be None, str or list.")

    # Laterality
    if hemisphere != "both":
        if hemisphere.lower() == "left" or hemisphere.lower() == "l":
            hemi = [s for s in electrodes if len(re.findall(r'\d+', s)) > 0 and int(re.findall(r'\d+', s)[0])%2 > 0]
        elif hemisphere.lower() == "right" or hemisphere.lower() == "r":
            hemi = [s for s in electrodes if len(re.findall(r'\d+', s)) > 0 and int(re.findall(r'\d+', s)[0])%2 == 0]
        else:
            print("NeuroKit Warning: eeg_select_electrodes(): 'hemisphere' parameter must be 'both', 'left' or 'right'. Returning both.")

        if central is True:
            hemi += [s for s in electrodes if 'z' in s]

        electrodes = hemi

    return(electrodes)


