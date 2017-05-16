# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import neurokit as nk
import pyrem
import nolds



df = pd.read_csv('data.csv')
df = nk.ecg_process(ecg=df["ECG"])


rri = df["ECG"]["RR_Intervals"]

signal=rri
tolerance = "default"
emb_dim=2
#chaos = nk.complexity(signal, lyap_r=False, lyap_e=False)

#==============================================================================
#
#==============================================================================
def spectral_entropy(a, sampling_freq, bands=None):

    r"""
    Compute spectral entropy of a  signal with respect to frequency bands.
    The power spectrum is computed through fft. Then, it is normalised and assimilated to a probability density function.
    The entropy of the signal :math:`x` can be expressed by:
    .. math::
        H(x) =  -\sum_{f=0}^{f = f_s/2} PSD(f) log_2[PSD(f)]
    Where:
    :math:`PSD` is the normalised power spectrum (Power Spectrum Density), and
    :math:`f_s` is the sampling frequency
    :param a: a one dimensional floating-point array representing a time series.
    :type a: :class:`~numpy.ndarray` or :class:`~pyrem.time_series.Signal`
    :param sampling_freq: the sampling frequency
    :type sampling_freq:  float
    :param bands: a list of numbers delimiting the bins of the frequency bands. If None the entropy is computed over the whole range of the DFT (from 0 to :math:`f_s/2`)
    :return: the spectral entropy; a scalar
    """



    psd = np.abs(np.fft.rfft(a))**2
    psd /= np.sum(psd) # psd as a pdf (normalised to one)

    if bands is None:
        power_per_band= psd[psd>0]
    else:
        freqs = np.fft.rfftfreq(a.size, 1/float(sampling_freq))
        bands = np.asarray(bands)

        freq_limits_low = np.concatenate([[0.0],bands])
        freq_limits_up = np.concatenate([bands, [np.Inf]])

        power_per_band = [np.sum(psd[np.bitwise_and(freqs >= low, freqs<up)])
                for low,up in zip(freq_limits_low, freq_limits_up)]

        power_per_band= power_per_band[ power_per_band > 0]

    return - np.sum(power_per_band * np.log2(power_per_band))
spectral_entropy(signal, 1000)
#==============================================================================
#
#==============================================================================


def hfd(a, k_max):

    r"""
    Compute Higuchi Fractal Dimension of a time series.
    Vectorised version of the eponymous [PYEEG]_ function.
    .. note::
        **Difference with PyEEG:**
        Results is different from [PYEEG]_ which appears to have implemented an erroneous formulae.
        [HIG88]_ defines the normalisation factor as:
        .. math::
            \frac{N-1}{[\frac{N-m}{k} ]\dot{} k}
        [PYEEG]_ implementation uses:
        .. math::
            \frac{N-1}{[\frac{N-m}{k}]}
        The latter does *not* give the expected fractal dimension of approximately `1.50` for brownian motion (see example bellow).
    :param a: a one dimensional floating-point array representing a time series.
    :type a: :class:`~numpy.ndarray` or :class:`~pyrem.time_series.Signal`
    :param k_max: the maximal value of k
    :type k_max: int
    :return: Higuchi's fractal dimension; a scalar
    :rtype: float
    Example from [HIG88]_. This should produce a result close to `1.50`:
    >>> import numpy as np
    >>> import pyrem as pr
    >>> i = np.arange(2 ** 15) +1001
    >>> z = np.random.normal(size=int(2 ** 15) + 1001)
    >>> y = np.array([np.sum(z[1:j]) for j in i])
    >>> pr.univariate.hfd(y,2**8)
    """

    L = []
    x = []
    N = a.size

    km_idxs = np.triu_indices(k_max - 1)
    km_idxs = k_max - np.flipud(np.column_stack(km_idxs)) -1
    km_idxs[:,1] -= 1


    for k in range(1,k_max):
        Lk = 0
        for m in range(0,k):
            #we pregenerate all idxs
            idxs = np.arange(1,int(np.floor((N-m)/k)),dtype=np.int32)

            Lmk = np.sum(np.abs(a[m+idxs*k] - a[m+k*(idxs-1)]))
            Lmk = (Lmk*(N - 1)/(((N - m)/ k)* k)) / k
            Lk += Lmk


        L.append(np.log(Lk/(m+1)))
        x.append([np.log(1.0/ k), 1])

    (p, r1, r2, s)=np.linalg.lstsq(x, L)
    return p[0]

higushi = []
for i in range(2, 250):
    higushi.append(hfd(signal, i))
pd.Series(higushi).plot()

#==============================================================================
#
#==============================================================================
def fisher_info(a, tau, de):
    r"""
    Compute the Fisher information of a signal with embedding dimension "de" and delay "tau" [PYEEG]_.
    Vectorised (i.e. faster) version of the eponymous PyEEG function.
    :param a: a one dimensional floating-point array representing a time series.
    :type a: :class:`~numpy.ndarray` or :class:`~pyrem.time_series.Signal`
    :param tau: the delay
    :type tau: int
    :param de: the embedding dimension
    :type de: int
    :return: the Fisher information, a scalar
    :rtype: float
    """

    mat =  _embed_seq(a, tau, de)
    W = np.linalg.svd(mat, compute_uv = False)
    W /= sum(W) # normalize singular values
    FI_v = (W[1:] - W[:-1]) **2 / W[:-1]

    return np.sum(FI_v)