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
    Median Absolute Deviation: a "robust" version of standard deviation.

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

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

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
    raw_scores : list, ndarray or pandas.Series
        ECG signal array.
    centered : bool
        Center the array (mean = 0).
    scale :  bool
        scale the array (sd = 1).

    Returns
    ----------
    z_scores : pandas.DataFrame
        The normalized scores.


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
    Identify outliers (abnormal values) using the standart deviation.

    Parameters
    ----------
    data : list or ndarray
        Data array
    treshold : float
        Maximum deviation (in terms of standart deviation). Rule of thumb of a gaussian distribution: 2.58 = rejecting 1%, 2.33 = rejecting 2%, 1.96 = 5% and 1.28 = rejecting 10%.

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
    Returns a bottom and a top limit on a normal distribution portion based on a treshold.

    Parameters
    ----------
    treshold : float
        maximum deviation (in terms of standart deviation). Rule of thumb of a gaussian distribution: 2.58 = keeping 99%, 2.33 = keeping 98%, 1.96 = 95% and 1.28 = keeping 90%.

    Returns
    ----------
    (bottom, top) : tuple
        Lower and higher range.

    Example
    ----------
    >>> import neurokit as nk
    >>> bottom, top = nk.normal_range(mean=100, sd=15, treshold=2)

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    """
    bottom = mean - sd*treshold
    top = mean + sd*treshold
    return(bottom, top)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_following_duplicates(array):
    """
    Find the duplicates that are following themselves.

    Parameters
    ----------
    array :  list or ndarray
        A list containing duplicates.

    Returns
    ----------
    uniques : list
        A list containing True for each unique and False for following duplicates.

    Example
    ----------
    >>> import neurokit as nk
    >>> mylist = ["a","a","b","a","a","a","c","c","b","b"]
    >>> uniques = nk.find_following_duplicates(mylist)
    >>> indices = np.where(uniques)  # Find indices of uniques

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    """
    array = array[:]


    uniques = []
    for i in range(len(array)):
        if i == 0:
            uniques.append(True)
        else:
            if array[i] == array[i-1]:
                uniques.append(False)
            else:
                uniques.append(True)

    return(uniques)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_closest_in_list(number, array, direction="both", strictly=False):
    """
    Find the closest number in the array from x.

    Parameters
    ----------
    number : float
        The number.
    array : list
        The list to look in.
    direction : str
        "both" for smaller or greater, "greater" for only greater numbers and "smaller" for the closest smaller.
    strictly : bool
        False for stricly superior or inferior or True for including equal.

    Returns
    ----------
    closest : int
        The closest number in the array.

    Example
    ----------
    >>> import neurokit as nk
    >>> nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2])

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    """
    if direction == "both":
        closest = min(array, key=lambda x:abs(x-number))
    if direction == "smaller":
        if strictly is True:
            closest = max(x for x in array if x < number)
        else:
            closest = max(x for x in array if x <= number)
    if direction == "greater":
        if strictly is True:
            closest = min(filter(lambda x: x > number, array))
        else:
            closest = min(filter(lambda x: x >= number, array))

    return(closest)