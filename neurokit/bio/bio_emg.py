# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import biosppy





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def emg_process(emg, sampling_rate=1000, emg_names=None):
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


    return(processed_emg)
