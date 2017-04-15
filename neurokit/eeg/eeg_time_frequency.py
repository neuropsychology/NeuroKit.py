"""
Time-frequency submodule.
"""
from .eeg_preprocessing import eeg_select_sensor_area
from ..miscellaneous import Time

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
def eeg_name_frequencies(freqs):
    """
    Name frequencies according to standart classifications.

    Parameters
    ----------
    freqs : list or numpy.array
        list of floats containing frequencies to classify.

    Returns
    ----------
    freqs_names : list
        Named frequencies

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.eeg_name_frequencies([0.5, 1.5, 3, 5, 7, 15])

    Notes
    ----------
    *Details*

    - Delta: 1-3Hz
    - Theta: 4-7Hz
    - Alpha1: 8-9Hz
    - Alpha2: 10-12Hz
    - Beta1: 13-17Hz
    - Beta2: 18-30Hz
    - Gamma1: 31-40Hz
    - Gamma2: 41-50Hz
    - Mu: 8-13Hz

    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    References
    ------------
    - None
    """
    freqs = list(freqs)
    freqs_names = []
    for freq in freqs:
        if freq < 1:
            freqs_names.append("UltraLow")
        elif freq <= 3:
            freqs_names.append("Delta")
        elif freq <= 7:
            freqs_names.append("Theta")
        elif freq <= 9:
            freqs_names.append("Alpha1/Mu")
        elif freq <= 12:
            freqs_names.append("Alpha2/Mu")
        elif freq <= 13:
            freqs_names.append("Beta1/Mu")
        elif freq <= 17:
            freqs_names.append("Beta1")
        elif freq <= 30:
            freqs_names.append("Beta2")
        elif freq <= 40:
            freqs_names.append("Gamma1")
        elif freq <= 50:
            freqs_names.append("Gamma2")
        else:
            freqs_names.append("UltraHigh")
    return(freqs_names)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_psd(raw, sensors_include="all", sensors_exclude=None, fmin=0.016, fmax=60, method="multitaper", proj=False):
    """
    Compute Power-Spectral Density (PSD).

    Parameters
    ----------
    raw : mne.io.Raw
        Raw EEG data.
    sensors_include : str
        Sensor area to include. See :func:`neurokit.eeg_select_sensors()`.
    sensors_exclude : str
        Sensor area to exclude. See :func:`neurokit.eeg_select_sensors()`.
    fmin : float
        Min frequency of interest.
    fmax: float
        Max frequency of interest.
    method : str
        "multitaper" or "welch".
    proj : bool
        add projectors.

    Returns
    ----------
    mean_psd : pandas.DataFrame
        Averaged PSDs.

    Example
    ----------
    >>> import neurokit as nk


    Notes
    ----------
    *Details*

    - Delta: 1-3Hz
    - Theta: 4-7Hz
    - Alpha1: 8-9Hz
    - Alpha2: 10-12Hz
    - Beta1: 13-17Hz
    - Beta2: 18-30Hz
    - Gamma1: 31-40Hz
    - Gamma2: 41-50Hz
    - Mu: 8-13Hz

    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    References
    ------------
    - None
    """
    picks = mne.pick_types(raw.info, include=eeg_select_sensor_area(include=sensors_include, exclude=sensors_exclude), exclude="bads")

    if method == "multitaper":
        psds, freqs = mne.time_frequency.psd_multitaper(raw,
                                                        fmin=fmin,
                                                        fmax=fmax,
                                                        low_bias=True,
                                                        proj=proj,
                                                        picks=picks)
    else:
        psds, freqs = mne.time_frequency.psd_welch(raw,
                                                        fmin=fmin,
                                                        fmax=fmax,
                                                        proj=proj,
                                                        picks=picks)
    tf = pd.DataFrame(psds)
    tf.columns = eeg_name_frequencies(freqs)
    tf = tf.mean(axis=0)

    mean_psd = {}
    for freq in ["UltraLow", "Delta", "Theta", "Alpha", "Alpha1", "Alpha2", "Mu", "Beta", "Beta1", "Beta2", "Gamma", "Gamma1", "Gamma2", "UltraHigh"]:
        mean_psd[freq] = tf[[freq in s for s in tf.index]].mean()
    mean_psd = pd.DataFrame.from_dict(mean_psd, orient="index").T

    return(mean_psd)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_create_frequency_bands(bands="all", step=1):
    """
    Delta: 1-3Hz
    Theta: 4-7Hz
    Alpha1: 8-9Hz
    Alpha2: 10-12Hz
    Beta1: 13-17Hz
    Beta2: 18-30Hz
    Gamma1: 31-40Hz
    Gamma2: 41-50Hz
    Mu: 8-13Hz
    """
    if bands == "all" or bands == "All":
        bands = ["Delta", "Theta", "Alpha", "Beta", "Gamma", "Mu"]
    if "Alpha" in bands:
        bands.remove("Alpha")
        bands += ["Alpha1", "Alpha2"]
    if "Beta" in bands:
        bands.remove("Beta")
        bands += ["Beta1", "Beta2"]
    if "Gamma" in bands:
        bands.remove("Gamma")
        bands += ["Gamma1", "Gamma2"]

    frequencies = {}
    for band in bands:
        if band == "Delta":
            frequencies[band] = np.arange(1, 3+0.1, step)
        if band == "Theta":
            frequencies[band] = np.arange(4, 7+0.1, step)
        if band == "Alpha1":
            frequencies[band] = np.arange(8, 9+0.1, step)
        if band == "Alpha2":
            frequencies[band] = np.arange(10, 12+0.1, step)
        if band == "Beta1":
            frequencies[band] = np.arange(13, 17+0.1, step)
        if band == "Beta2":
            frequencies[band] = np.arange(18, 30+0.1, step)
        if band == "Gamma1":
            frequencies[band] = np.arange(31, 40+0.1, step)
        if band == "Gamma2":
            frequencies[band] = np.arange(41, 50+0.1, step)
        if band == "Mu":
            frequencies[band] = np.arange(8, 13+0.1, step)
    return(frequencies)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_power_per_frequency_band(epoch, bands="all", step=1):
    """
    """
    frequencies = eeg_create_frequency_bands(bands=bands, step=step)

    power_per_band = {}
    for band in frequencies:
        power, itc = mne.time_frequency.tfr_morlet(epoch, freqs=frequencies[band], n_cycles=frequencies[band]/2, use_fft=True, return_itc=True, decim=3, n_jobs=1)

        data = power.data
        times = power.times
        freqs = power.freqs

        df =  pd.DataFrame(np.average(data, axis=0).T, index=times, columns=freqs)
        df = df.mean(axis=1)
        power_per_band[band] = list(df)

    df = pd.DataFrame.from_dict(power_per_band)
    df.index = times

    return(df)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_power_per_epoch(epochs, include="all", exclude=None, hemisphere="both", include_central=True, frequency_bands="all", time_start=0, time_end="max", fill_bads="NA", print_progression=True):
    """
    """


    epochs = epochs.copy().pick_channels(eeg_select_sensors(include=include, exclude=exclude, hemisphere=hemisphere, include_central=include_central))

    dropped = list(epochs.drop_log)  # get events
    frequencies = eeg_create_frequency_bands(bands=frequency_bands)

    events = {}
    n_epoch = 0
    clock = Time()
    for event_type in enumerate(dropped):
        if event_type[1] == []:
            df = eeg_power_per_frequency_band(epochs[n_epoch], bands=frequency_bands, step=1)
            if time_end == "max":
                df = df.loc[time_start:,:]  # Select times
            else:
                df = df.loc[time_start:time_end,:]  # Select times
            df = df.mean(axis=0)  # Compute average

            events[event_type[0]] = list(df)
            n_epoch += 1
        else:
            if fill_bads == "NA":
                events[event_type[0]] = [np.nan]*len(frequencies)
            else:
                events[event_type[0]] = [fill_bads]*len(frequencies)

        # Compute remaining time
        time = clock.get(reset=False)/1000
        time = time/(event_type[0]+1)
        time = time * (len(dropped)-(event_type[0]+1))
        if print_progression == True:
            print(str(round((event_type[0]+1)/len(dropped)*100)) + "% complete, remaining time: " + str(round(time, 2)) + 's')

    df = pd.DataFrame.from_dict(events, orient="index")

    columns_names =  ["Power_" + x for x in frequencies.keys()]
    df.columns = columns_names

    return(df)






