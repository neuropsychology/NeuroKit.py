# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import scipy
import scipy.stats

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def mad(var, constant=1):
    """
    Median Absolute Deviation: a "Robust" version of standard deviation.

    Parameters
    ----------
    var : list or ndarray
        Value array.
    constant : float
        Scale factor. Use 1.4826 for results similar to default R.

    Returns
    ----------
    mad : float
        The MAD.

    Example
    ----------
    >>> import neurokit as nk
    >>> hrv = nk.mad([2, 8, 7, 5, 4, 12, 5, 1])

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - numpy

    References
    -----------
    - https://en.wikipedia.org/wiki/Median_absolute_deviation
    """
    median = np.median(var)
    mad = np.median(np.abs(var - median))
    mad = mad*constant
    return(mad)








# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def z_score(raw_scores, center=True, scale=True):
    """
    Transform an array, serie or list into Z scores (scaled and centered scores).

    Parameters
    ----------
    raw_scores : list, numpy.array or pandas.Series
        ECG signal array.
    centered : bool
        Center the array (mean = 0).
    scale :  bool
        scale the array (sd = 1).

    Returns
    ----------
    z_scores : pandas.DataFrame
        The Z scores.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.z_score([3, 1, 2, 4, 6])

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - pandas

    """
    df = pd.DataFrame(raw_scores)

    mean = df.mean(axis=0)
    sd = df.std(axis=0)
    z_scores = (df - mean)/sd

    return(z_scores)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def dprime(n_Hit=None, n_Miss=None, n_FA=None, n_CR=None):
    """
    Computes the d', beta, aprime, b''d and c parameters based on the signal detection theory (SDT). **Feel free to help me expand the documentation of this function with details and interpretation guides.**

    Parameters
    ----------
    n_Hit : int
        Number of hits.
    n_Miss : int
        Number of misses.
    n_FA : int
        Number of false alarms.
    n_CR : int
       Number of correct rejections.

    Returns
    ----------
    parameters : dict
        A dictionary with the parameters (see details).

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)


    Notes
    ----------
    *Details*

    The Signal Detection Theory (often abridged as SDT) is used in very different domains from psychology (psychophysics, perception, memory), medical diagnostics (do the symptoms match a known diagnostic or can they be dismissed are irrelevant), to statistical decision (do the data indicate that the experiment has an effect or not). It evolved from the development of communications and radar equipment the first half of this century to psychology, as an attempt to understand some features of human behavior that were not well explained by tradition models. SDT is, indeed, used to analyze data coming from experiments where the task is to categorize ambiguous stimuli which can be generated either by a known process (called the *signal*) or be obtained by chance (called the *noise* in the SDT framework). Based on the number of hits, misses, false alarms and correct rejections, it estimates two main parameters from the experimental data: **d' (d-prime, for discriminability index**) and C (a variant of it is called beta). Non parametric variants are aprime and b''d (bppd)

    - **dprime**: The sensitivity index. Indicates the strength of the signal (relative to the noise). More specifically, it is the standardized difference between the means of the Signal Present and Signal Absent distributions.
    - **beta**: Response bias index.
    - **aprime**:  Non-parametric sensitivity index.
    - **bppd**: Non-parametric response bias index.
    - **c**: Response bias index.

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_


    *Dependencies*

    - scipy

    *See Also*

    - `neuropsychology <https://www.rdocumentation.org/packages/neuropsychology/topics/dprime>`_
    - http://lindeloev.net/calculating-d-in-python-and-php/
    """
    n_Hit = 9
    n_Miss = 2
    n_FA = 4
    n_CR = 6

    # Ratios
    hit_rate = n_Hit/(n_Hit + n_Miss)
    fa_rate = n_FA/(n_FA + n_CR)


    # Adjusted ratios
    hit_rate_adjusted = (n_Hit+ 0.5)/((n_Hit+ 0.5) + n_Miss + 1)
    fa_rate_adjusted = (n_FA+ 0.5)/((n_FA+ 0.5) + n_CR + 1)


    # dprime
    dprime = scipy.stats.norm.ppf(hit_rate_adjusted) - scipy.stats.norm.ppf(hit_rate_adjusted)

    # beta
    zhr = scipy.stats.norm.ppf(hit_rate_adjusted)
    zfar = scipy.stats.norm.ppf(fa_rate_adjusted)
    beta = np.exp(-zhr*zhr/2 + zfar*zfar/2)

    # aprime
    a = 1/2+((hit_rate-fa_rate)*(1+hit_rate-fa_rate) / (4*hit_rate*(1-fa_rate)))
    b = 1/2-((fa_rate-hit_rate)*(1+fa_rate-hit_rate) / (4*fa_rate*(1-hit_rate)))

    if fa_rate > hit_rate:
        aprime = b
    elif fa_rate < hit_rate:
        aprime = a
    else:
        aprime = 0.5

    # bppd
    bppd = ((1-hit_rate)*(1-fa_rate)-hit_rate*fa_rate) / ((1-hit_rate)*(1-fa_rate)+hit_rate*fa_rate)

    # c
    c = -(scipy.stats.norm.ppf(hit_rate_adjusted) + scipy.stats.norm.ppf(fa_rate_adjusted))/2

    parameters = dict(dprime=dprime, beta=beta, aprime=aprime, bppd=bppd, c=c)
    return(parameters)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_outliers(data, treshold=2.58):
    """
    Identify outliers (abnormal values).

    Parameters
    ----------
    data : list or ndarray
        Data array
    treshold : float
        Maximum deviation (in terms of standart deviation). Following a gaussian distribution, 2.58 = rejecting 1%, 2.33 = rejecting 2%, 1.96 = 5% and 1.28 = rejecting 10%.

    Returns
    ----------
    outliers : ndarray
        A list of True/False with True being the outliers.

    Example
    ----------
    >>> import neurokit as nk
    >>> outliers = nk.find_outliers([1, 2, 1, 5, 666, 4, 1 ,3, 5])

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    """
    outliers = []
    mean = np.mean(data)
    std = np.std(data)
    for i in data:
        if abs(i - mean)/std < treshold:
            outliers.append(False)
        else:
            outliers.append(True)
    outliers = np.array(outliers)
    return (outliers)






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def normal_range(mean, sd, treshold=1.28):
    """
    Returns a bottom and a top limit based on a treshold.

    Parameters
    ----------
    treshold : float
        maximum deviation (in terms of standart deviation). Following a gaussian distribution, 2.58 = keeping 99%, 2.33 = keeping 98%, 1.96 = 95% and 1.28 = keeping 90%.

    Returns
    ----------
    NA

    Example
    ----------
    NA

    Authors
    ----------
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_


    Dependencies
    ----------
    - numpy
    """
    bottom = mean - sd*treshold
    top = mean + sd*treshold
    return(bottom, top)


