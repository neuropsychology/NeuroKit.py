"""
Miscellaenous submodule.
"""
from .eeg_data import eeg_select_channels

import mne
import biosppy

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_find_Rpeaks(raw, ecg_channel="ecg"):
    """
    Find R peaks indices on the ECG channel.

    Parameters
    ----------
    raw = mne.io.Raw
        Raw EEG data.
    ecg_channel = str
        ECG's channel name.


    Returns
    ----------
    rpeaks
        List of R-peak location indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> Rpeaks = nk.eeg_find_Rpeaks(raw)

    Authors
    ----------
    Dominique Makowski, the biosppy dev team

    Dependencies
    ----------
    None
    """
    rpeaks, = biosppy.ecg.hamilton_segmenter(signal=eeg_select_channels(raw, ecg_channel="ecg"), sampling_rate=raw.info["sfreq"])
    return(rpeaks)

