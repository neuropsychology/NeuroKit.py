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


