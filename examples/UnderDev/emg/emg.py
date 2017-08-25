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

def plot_emg_activation(x, threshold, n_above, n_below, inds, ax):
    """Plot results of the detect_onset function, see its help."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib is not available.')
    else:
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(8, 4))

        if inds.size:
            for (indi, indf) in inds:
                if indi == indf:
                    ax.plot(indf, x[indf], 'ro', mec='r', ms=6)
                else:
                    ax.plot(range(indi, indf+1), x[indi:indf+1], 'r', lw=1)
                    ax.axvline(x=indi, color='b', lw=1, ls='--')
                ax.axvline(x=indf, color='b', lw=1, ls='--')
            inds = np.vstack((np.hstack((0, inds[:, 1])),
                              np.hstack((inds[:, 0], x.size-1)))).T
            for (indi, indf) in inds:
                ax.plot(range(indi, indf+1), x[indi:indf+1], 'k', lw=1)
        else:
            ax.plot(x, 'k', lw=1)
            ax.axhline(y=threshold, color='r', lw=1, ls='-')

        ax.set_xlim(-.02*x.size, x.size*1.02-1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1*yrange, ymax + 0.1*yrange)
        ax.set_xlabel('Data #', fontsize=14)
        ax.set_ylabel('Amplitude', fontsize=14)
        ax.set_title('Onset detection (threshold=%.3g, n_above=%d, n_below=%d)'\
                     % (threshold, n_above, n_below))
        # plt.grid()
        plt.show()


def detect_onset(x, sampling_rate=1000, threshold=0, n_above=0.25, n_below=1, show=False, ax=None):
    """Detects onset in data based on amplitude threshold.

    Parameters
    ----------
    x : 1D array_like
        data.
    threshold : number, optional (default = 0)
        minimum amplitude of `x` to detect.
    n_above : number, optional (default = 1)
        minimum number of continuous samples greater than or equal to
        `threshold` to detect (but see the parameter `n_below`).
    n_below : number, optional (default = 0)
        minimum number of continuous samples below `threshold` that
        will be ignored in the detection of `x` >= `threshold`.
    show  : bool, optional (default = False)
        True (1) plots data in matplotlib figure, False (0) don't plot.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    inds : 1D array_like [indi, indf]
        initial and final indeces of the onset events.

    Notes
    -----
    You might have to tune the parameters according to the signal-to-noise
    characteristic of the data.

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectOnset.ipynb

    Examples
    --------
    >>> from detect_onset import detect_onset
    >>> x = np.random.randn(200)/10
    >>> x[51:151] += np.hstack((np.linspace(0,1,50), np.linspace(1,0,50)))
    >>> detect_onset(x, np.std(x[:50]), n_above=10, n_below=0, show=True)

    >>> x = np.random.randn(200)/10
    >>> x[51:151] += np.hstack((np.linspace(0,1,50), np.linspace(1,0,50)))
    >>> x[80:140:20] = 0
    >>> detect_onset(x, np.std(x[:50]), n_above=10, n_below=0, show=True)

    >>> x = np.random.randn(200)/10
    >>> x[51:151] += np.hstack((np.linspace(0,1,50), np.linspace(1,0,50)))
    >>> x[80:140:20] = 0
    >>> detect_onset(x, np.std(x[:50]), n_above=10, n_below=1, show=True)

    >>> x = [0, 0, 2, 0, np.nan, 0, 2, 3, 3, 0, 1, 1, 0]
    >>> detect_onset(x, threshold=1, n_above=1, n_below=0, show=True)
    """
    n_above = n_above*sampling_rate
    n_below = n_below*sampling_rate


    x = np.atleast_1d(x).astype('float64')
    # deal with NaN's (by definition, NaN's are not greater than threshold)
    x[np.isnan(x)] = -np.inf
    # indices of data greater than or equal to threshold
    inds = np.nonzero(x >= threshold)[0]
    if inds.size:
        # initial and final indexes of continuous data
        inds = np.vstack((inds[np.diff(np.hstack((-np.inf, inds))) > n_below+1], \
                          inds[np.diff(np.hstack((inds, np.inf))) > n_below+1])).T
        # indexes of continuous data longer than or equal to n_above
        inds = inds[inds[:, 1]-inds[:, 0] >= n_above-1, :]
    if not inds.size:
        inds = np.array([])  # standardize inds shape
#    if show and x.size > 1:  # don't waste my time ploting one datum
#        plot_emg_activation(x, threshold, n_above, n_below, inds, ax)
    inds = np.array(inds)
    return (inds)


def emg_tkeo(x):
    r"""Calculates the Teager–Kaiser Energy operator.

    Parameters
    ----------
    x : 1D array_like
        raw signal

    Returns
    -------
    y : 1D array_like
        signal processed by the Teager–Kaiser Energy operator

    Notes
    -----

    See this notebook [1]_.

    References
    ----------
    .. [1] https://github.com/demotu/BMC/blob/master/notebooks/Electromyography.ipynb

    """
    x = np.asarray(x)
    y = np.copy(x)
    # Teager–Kaiser Energy operator
    y[1:-1] = x[1:-1]*x[1:-1] - x[:-2]*x[2:]
    # correct the data in the extremities
    y[0], y[-1] = y[1], y[-2]

    return(y)



def emg_linear_envelope(x, freq=1000, fc_bp=[10, 400], fc_lp=8):
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
    x = emg_tkeo(x)
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







df["EMG_Envelope"] = emg_linear_envelope(x=df["EMG_Filtered"], freq=1000, fc_bp=[20, 400], fc_lp=4)





inds = detect_onset(df["EMG_Envelope"], threshold=1*np.std(df["EMG_Envelope"]), show=True)
inds = np.array(inds)

activation = np.array([0]*len(df))
for i in inds:
    activation[i[0]:i[1]] = 1
df["EMG_Activation"] = activation
df["EMG_Activation"].plot()
#plot_emg_activation(x, threshold, n_above, n_below, inds, ax)

nk.z_score(df).plot()

threshold=2
window=50