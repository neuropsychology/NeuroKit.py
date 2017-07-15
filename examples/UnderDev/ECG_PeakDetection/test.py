# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import biosppy
import matplotlib.pyplot as plt
import scipy



df = pd.read_csv('data.csv')
df = df.loc[10000:20000]


sampling_rate=1000
df = nk.ecg_preprocess(ecg=df["ECG"], sampling_rate=sampling_rate)["df"]
#df.plot()

#df["df"]["ECG_Filtered"].plot()




import numpy as np
import scipy.signal
import scipy.ndimage

def segmenter_pekkanen(ecg, sampling_rate, window_size=5.0, lfreq=5.0, hfreq=15.0,):
    """
    ECG R peak detection based on `Kathirvel et al. (2001) <http://link.springer.com/article/10.1007/s13239-011-0065-3/fulltext.html>`_ with some tweaks (mainly robust estimation of the rectified signal cutoff threshold).

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    window_size : float
        Ransac window size.
    lfreq : float
        Low frequency of the band pass filter.
    hfreq : float
        High frequency of the band pass filter.

    Returns
    ----------
    rpeaks : ndarray
        R peaks location.

    Example
    ----------
    >>> import neurokit as nk
    >>> rpeaks = nk.segmenter_pekkanen(ecg_signal, 1000)

    *Authors*

    - `Jami Pekkanen <https://github.com/jampekka>`_
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - scipy
    - numpy

    *See Also*

    - rpeakdetect: https://github.com/tru-hy/rpeakdetect
    """

    window_size = int(window_size*sampling_rate)

    lowpass = scipy.signal.butter(1, hfreq/(sampling_rate/2.0), 'low')
    highpass = scipy.signal.butter(1, lfreq/(sampling_rate/2.0), 'high')

    # TODO: Could use an actual bandpass filter
    ecg_low = scipy.signal.filtfilt(*lowpass, x=ecg)
    ecg_band = scipy.signal.filtfilt(*highpass, x=ecg_low)

    # Square (=signal power) of the first difference of the signal
    decg = np.diff(ecg_band)
    decg_power = decg**2

    # Robust threshold and normalizator estimation
    thresholds = []
    max_powers = []
    for i in range(int(len(decg_power)/window_size)):
        sample = slice(i*window_size, (i+1)*window_size)
        d = decg_power[sample]
        thresholds.append(0.5*np.std(d))
        max_powers.append(np.max(d))

    threshold = 0.5*np.std(decg_power)
    threshold = np.median(thresholds)
    max_power = np.median(max_powers)
    decg_power[decg_power < threshold] = 0

    decg_power = decg_power/max_power
    decg_power[decg_power > 1.0] = 1.0
    square_decg_power = decg_power**2

#    shannon_energy = -square_decg_power*np.log(square_decg_power)  # This errors
#    shannon_energy[np.where(np.isfinite(shannon_energy) == False)] = 0.0
    shannon_energy = -square_decg_power*np.log(square_decg_power.clip(min=1e-6))
    shannon_energy[np.where(shannon_energy <= 0)] = 0.0


    mean_window_len = int(sampling_rate*0.125+1)
    lp_energy = np.convolve(shannon_energy, [1.0/mean_window_len]*mean_window_len, mode='same')
    #lp_energy = scipy.signal.filtfilt(*lowpass2, x=shannon_energy)

    lp_energy = scipy.ndimage.gaussian_filter1d(lp_energy, sampling_rate/8.0)
    lp_energy_diff = np.diff(lp_energy)

    rpeaks = (lp_energy_diff[:-1] > 0) & (lp_energy_diff[1:] < 0)
    rpeaks = np.flatnonzero(rpeaks)
    rpeaks -= 1

    return(rpeaks)

rpeaks = segmenter_pekkanen(df["ECG_Raw"], 1000)
nk.plot_events_in_signal(df["ECG_Raw"], rpeaks)
