# -*- coding: utf-8 -*-
import nolds  # Fractal
import numpy as np

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def fractal_dimensions(signal, entropy=True, hurst=True, dfa=True, lyap_r=True, lyap_e=True):
    """
    Returns several fractal/chaos/complexity indices of a signal.

    Parameters
    ----------
    signal = list or array
        List or array of values.
    entropy = bool
        Measures the complexity of a time-series, based on approximate entropy.
    hurst = bool
        The hurst exponent is a measure of the "long-term memory" of a time series. It can be used to determine whether the time series is more, less, or equally likely to increase if it has increased in previous steps. This property makes the Hurst exponent especially interesting for the analysis of stock data.
    dfa = bool
        DFA measures the Hurst parameter H, which is very similar to the Hurst exponent. The main difference is that DFA can be used for non-stationary processes (whose mean and/or variance change over time).
    lyap_r = bool
        Positive Lyapunov exponents indicate chaos and unpredictability following the algorithm of Rosenstein et al. to estimate the largest Lyapunov exponent.
    lyap_e = bool
        Positive Lyapunov exponents indicate chaos and unpredictability following the algorithm of Rosenstein et al. to estimate the whole spectrum of Lyapunov exponents.

    Returns
    ----------
    dic
        A dictionary containing values for each indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> signal = [5, 1, 7, 2, 5, 1, 7, 4, 6, 7, 5, 4, 1, 1, 4, 4]
    >>> results = nk.fractal_dimensions(signal)
    >>> print(results["Entropy"])

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - nolds
    """
    results = {}
    if entropy == True:
        try:
            results["Entropy"] = nolds.sampen(signal)
        except:
            results["Entropy"] = np.nan
#    if corr == True:
#        try:
#            results["Corr"] = nolds.corr_dim(signal, 10)
#        except:
#            results["Corr"] = np.nan
    if hurst == True:
        try:
            results["Hurst"] = nolds.hurst_rs(signal)
        except:
            results["Hurst"] = np.nan
    if dfa == True:
        try:
            results["DFA"] = nolds.dfa(signal)
        except:
            results["DFA"] = np.nan
    if lyap_r == True:
        try:
            results["Lyapunov_R"] = nolds.lyap_r(signal)
        except:
            results["Lyapunov_R"] = np.nan
    if lyap_e == True:
        try:
            results["Lyapunov_E"] = nolds.lyap_e(signal)
        except:
            results["Lyapunov_E"] = np.nan

    return(results)
