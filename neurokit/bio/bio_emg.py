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
def emg_process(emg, sampling_rate=1000):
    """
    Automated processing of EMG signal.

    Parameters
    ----------
    emg :  list or array
        EMG signal array.
    sampling_rate : int
        Sampling rate (samples/second).

    Returns
    ----------
    processed_emg : dict
        Dict containing processed EMG features.

        Contains the EMG raw signal, the filtered signal and the pulse onsets.

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
    emg_df = pd.DataFrame({"EMG_Raw": np.array(emg)})

    # Compute several features using biosppy
    biosppy_emg = dict(biosppy.emg.emg(emg, sampling_rate=sampling_rate, show=False))

    emg_df["EMG_Filtered"] = biosppy_emg["filtered"]

    # Store EMG pulse onsets
    pulse_onsets = np.array([np.nan]*len(emg))
    if len(biosppy_emg['onsets']) > 0:
        pulse_onsets[biosppy_emg['onsets']] = 1
    emg_df["EMG_Pulse_Onsets"] = pulse_onsets


    processed_emg = {"df": emg_df,
                     "EMG": {
                            "EMG_Pulse_Onsets": emg_df['EMG_Pulse_Onsets']}}
    return(processed_emg)
