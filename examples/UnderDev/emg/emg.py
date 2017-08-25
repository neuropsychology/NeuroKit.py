import neurokit as nk
import scipy
import numpy as np
import pandas as pd
# Read file
file = nk.read_acqknowledge("emg.acq")

file = file[40000:120000]  # Crop it to a small part to speed things up


# Process it
processed = nk.bio_process(emg=file["EMG100C"], sampling_rate=1000, add=file['Digital input'])

#emg_features = processed["EMG"]
df = processed["df"]


df.plot()


def linear_envelope(x, freq=1000, fc_bp=[10, 400], fc_lp=8):
    r"""Calculate the linear envelope of a signal.

    Parameters
    ----------
    x     : 1D array_like
            raw signal
    freq  : number
            sampling frequency
    fc_bp : list [fc_h, fc_l], optional
            cutoff frequencies for the band-pass filter (in Hz)
    fc_lp : number, optional
            cutoff frequency for the low-pass filter (in Hz)

    Returns
    -------
    x     : 1D array_like
            linear envelope of the signal

    Notes
    -----
    A 2nd-order Butterworth filter with zero lag is used for the filtering.

    See this notebook [1]_.

    References
    ----------
    .. [1] https://github.com/demotu/BMC/blob/master/notebooks/Electromyography.ipynb

    """

    if np.size(fc_bp) == 2:
        # band-pass filter
        b, a = scipy.signal.butter(2, np.array(fc_bp)/(freq/2.), btype = 'bandpass')
        x = scipy.signal.filtfilt(b, a, x)
    if np.size(fc_lp) == 1:
        # full-wave rectification
        x = abs(x)
        # low-pass Butterworth filter
        b, a = scipy.signal.butter(2, np.array(fc_lp)/(freq/2.), btype = 'low')
        x = scipy.signal.filtfilt(b, a, x)

    return (x)

threshold=2
window=50
data2 = linear_envelope(x=df["EMG_Filtered"], freq=1000, fc_bp=[20, 400], fc_lp=4)

df["EMG_Filtered"].plot()
pd.Series(data2).plot()