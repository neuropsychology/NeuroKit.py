# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import biosppy
import scipy


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def emg_process(emg, sampling_rate=1000, emg_names=None, envelope_freqs=[10, 400], envelope_lfreq=4, activation_treshold="default", activation_n_above=0.25, activation_n_below=1):
    """
    Automated processing of EMG signal.

    Parameters
    ----------
    emg :  list, array or DataFrame
        EMG signal array. Can include multiple channels.
    sampling_rate : int
        Sampling rate (samples/second).
    emg_names : list
        List of EMG channel names.
    envelope_freqs : list [fc_h, fc_l], optional
            cutoff frequencies for the band-pass filter (in Hz).
    envelope_lfreq : number, optional
            cutoff frequency for the low-pass filter (in Hz).
    activation_treshold : float
        minimum amplitude of `x` to detect.
    activation_n_above : float
        minimum continuous time (in s) greater than or equal to `threshold` to detect (but see the parameter `n_below`).
    activation_n_below : float
        minimum time (in s) below `threshold` that will be ignored in the detection of `x` >= `threshold`.


    Returns
    ----------
    processed_emg : dict
        Dict containing processed EMG features.

        Contains the EMG raw signal, the filtered signal and pulse onsets.

        This function is mainly a wrapper for the biosppy.emg.emg() function. Credits go to its authors.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_emg = nk.emg_process(emg_signal)


    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - biosppy
    - numpy
    - pandas

    *See Also*

    - BioSPPy: https://github.com/PIA-Group/BioSPPy

    References
    -----------
    - None
    """
    if emg_names is None:
        if isinstance(emg, pd.DataFrame):
            emg_names = emg.columns.values

    emg = np.array(emg)
    if len(np.shape(emg)) == 1:
        emg = np.array(pd.DataFrame(emg))

    if emg_names is None:
        if np.shape(emg)[1]>1:
            emg_names = []
            for index in range(np.shape(emg)[1]):
                emg_names.append("EMG_" + str(index))
        else:
            emg_names = ["EMG"]


    processed_emg = {"df": pd.DataFrame()}
    for index, emg_chan in enumerate(emg.T):
        # Store Raw signal
        processed_emg["df"][emg_names[index] + "_Raw"] = emg_chan

        # Compute several features using biosppy
        biosppy_emg = dict(biosppy.emg.emg(emg_chan, sampling_rate=sampling_rate, show=False))

        # Store EMG pulse onsets
        pulse_onsets = np.array([np.nan]*len(emg))
        if len(biosppy_emg['onsets']) > 0:
            pulse_onsets[biosppy_emg['onsets']] = 1
        processed_emg["df"][emg_names[index] + "_Pulse_Onsets"] = pulse_onsets

        processed_emg["df"][emg_names[index] + "_Filtered"] = biosppy_emg["filtered"]
        processed_emg[emg_names[index]] = {}
        processed_emg[emg_names[index]]["EMG_Pulse_Onsets"] = biosppy_emg['onsets']

        # Envelope
        envelope = emg_linear_envelope(biosppy_emg["filtered"], sampling_rate=sampling_rate, freqs=envelope_freqs, lfreq=envelope_lfreq)
        processed_emg["df"][emg_names[index] + "_Envelope"] = envelope

        # Activation
        if activation_treshold == "default":
            activation_treshold = 1*np.std(envelope)
        processed_emg["df"][emg_names[index] + "_Activation"] = emg_find_activation(envelope, sampling_rate=sampling_rate, threshold=1*np.std(envelope), n_above=activation_n_above, n_below=activation_n_below)

    return(processed_emg)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def emg_tkeo(emg):
    """
    Calculates the Teager–Kaiser Energy operator.

    Parameters
    ----------
    emg : array
        raw EMG signal.

    Returns
    -------
    tkeo : 1D array_like
        signal processed by the Teager–Kaiser Energy operator.

    Notes
    -----

    *Authors*

    - Marcos Duarte



    *See Also*

    See this notebook [1]_.

    References
    ----------
    .. [1] https://github.com/demotu/BMC/blob/master/notebooks/Electromyography.ipynb

    """
    emg = np.asarray(emg)
    tkeo = np.copy(emg)
    # Teager–Kaiser Energy operator
    tkeo[1:-1] = emg[1:-1]*emg[1:-1] - emg[:-2]*emg[2:]
    # correct the data in the extremities
    tkeo[0], tkeo[-1] = tkeo[1], tkeo[-2]

    return(tkeo)




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def emg_linear_envelope(emg, sampling_rate=1000, freqs=[10, 400], lfreq=4):
    r"""Calculate the linear envelope of a signal.

    Parameters
    ----------
    emg : array
        raw EMG signal.
    sampling_rate : int
        Sampling rate (samples/second).
    freqs : list [fc_h, fc_l], optional
            cutoff frequencies for the band-pass filter (in Hz).
    lfreq : number, optional
            cutoff frequency for the low-pass filter (in Hz).

    Returns
    -------
    envelope : array
        linear envelope of the signal.

    Notes
    -----

    *Authors*

    - Marcos Duarte



    *See Also*

    See this notebook [1]_.

    References
    ----------
    .. [1] https://github.com/demotu/BMC/blob/master/notebooks/Electromyography.ipynb
    """
    emg = emg_tkeo(emg)

    if np.size(freqs) == 2:
        # band-pass filter
        b, a = scipy.signal.butter(2, np.array(freqs)/(sampling_rate/2.), btype = 'bandpass')
        emg = scipy.signal.filtfilt(b, a, emg)
    if np.size(lfreq) == 1:
        # full-wave rectification
        envelope = abs(emg)
        # low-pass Butterworth filter
        b, a = scipy.signal.butter(2, np.array(lfreq)/(sampling_rate/2.), btype = 'low')
        envelope = scipy.signal.filtfilt(b, a, envelope)

    return (envelope)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def emg_find_activation(envelope, sampling_rate=1000, threshold=0, n_above=0.25, n_below=1):
    """Detects onset in data based on amplitude threshold.

    Parameters
    ----------
    envelope : array
        Linear envelope of EMG signal.
    sampling_rate : int
        Sampling rate (samples/second).
    threshold : float
        minimum amplitude of `x` to detect.
    n_above : float
        minimum continuous time (in s) greater than or equal to `threshold` to detect (but see the parameter `n_below`).
    n_below : float
        minimum time (in s) below `threshold` that will be ignored in the detection of `x` >= `threshold`.

    Returns
    -------
    activation : array
        With 1 when muscle activated and 0 when not.

    Notes
    -----
    You might have to tune the parameters according to the signal-to-noise
    characteristic of the data.

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectOnset.ipynb
    """
    n_above = n_above*sampling_rate
    n_below = n_below*sampling_rate


    envelope = np.atleast_1d(envelope).astype('float64')
    # deal with NaN's (by definition, NaN's are not greater than threshold)
    envelope[np.isnan(envelope)] = -np.inf
    # indices of data greater than or equal to threshold
    inds = np.nonzero(envelope >= threshold)[0]
    if inds.size:
        # initial and final indexes of continuous data
        inds = np.vstack((inds[np.diff(np.hstack((-np.inf, inds))) > n_below+1], \
                          inds[np.diff(np.hstack((inds, np.inf))) > n_below+1])).T
        # indexes of continuous data longer than or equal to n_above
        inds = inds[inds[:, 1]-inds[:, 0] >= n_above-1, :]
    if not inds.size:
        inds = np.array([])  # standardize inds shape

    inds = np.array(inds)

    activation = np.array([0]*len(envelope))
    for i in inds:
        activation[i[0]:i[1]] = 1
    return (activation)
