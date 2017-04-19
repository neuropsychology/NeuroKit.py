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
def chaos(signal, entropy=True, fractal_dim=True, hurst=True, dfa=True, lyap_r=True, lyap_e=True):
    """
    Returns several chaos/complexity indices of a signal (including entropy, fractal dimensions, Hurst and Lyapunov exponent etc.).

    Parameters
    ----------
    signal : list or array
        List or array of values.
    entropy : bool
        Compute approximate entropy.
    fractal_dim : bool
        Compute the fractal dimension.
    hurst : bool
        Compute the Hurst exponent.
    dfa : bool
        Compute DFA.
    lyap_r : bool
        Compute Positive Lyapunov exponents (Rosenstein et al. (1993) method).
    lyap_e : bool
        Compute Positive Lyapunov exponents (Eckmann et al. (1986) method).

    Returns
    ----------
    chaos : dict
        Dict containing values for each indices.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> signal = [5, 1, 7, 2, 5, 1, 7, 4, 6, 7, 5, 4, 1, 1, 4, 4]
    >>> chaos_features = nk.chaos(signal)

    Notes
    ----------
    *Details*

    - **entropy**: Measures the complexity of a time-series, based on approximate entropy. The sample entropy of a time series is defined as the negative natural logarithm of the conditional probability that two sequences similar for emb_dim points remain similar at the next point, excluding self-matches. A lower value for the sample entropy therefore corresponds to a higher probability indicating more self-similarity.
    - **correlation dimension**: A measure of the fractal dimension of a time series which is also related to complexity. The correlation dimension is a characteristic measure that can be used to describe the geometry of chaotic attractors. It is defined using the correlation sum C(r) which is the fraction of pairs of points X_i in the phase space whose distance is smaller than r.
    - **hurst**: The Hurst exponent is a measure of the "long-term memory" of a time series. It can be used to determine whether the time series is more, less, or equally likely to increase if it has increased in previous steps. This property makes the Hurst exponent especially interesting for the analysis of stock data.
    - **dfa**: DFA measures the Hurst parameter H, which is very similar to the Hurst exponent. The main difference is that DFA can be used for non-stationary processes (whose mean and/or variance change over time).
    - **lyap**: Positive Lyapunov exponents indicate chaos and unpredictability. Provides the algorithm of Rosenstein et al. (1993) to estimate the largest Lyapunov exponent and the algorithm of Eckmann et al. (1986) to estimate the whole spectrum of Lyapunov exponents.


    *Authors*

    - Christopher Schölzel (https://github.com/CSchoel)
    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - nolds

    *See Also*

    - nolds package: https://github.com/CSchoel/nolds

    References
    -----------
    - Richman, J. S., & Moorman, J. R. (2000). Physiological time-series analysis using approximate entropy and sample entropy. American Journal of Physiology-Heart and Circulatory Physiology, 278(6), H2039-H2049.
    """
    chaos = {}
    if entropy == True:
        try:
            chaos["Entropy"] = nolds.sampen(signal)
        except:
            print("NeuroKit warning: fractal_dimensions(): Failed to compute entropy.")
            chaos["Entropy"] = np.nan
    if fractal_dim == True:
        try:
            chaos["Fractal_Dim"] = nolds.corr_dim(signal, 2)
        except:
            print("NeuroKit warning: fractal_dimensions(): Failed to compute entropy.")
            chaos["Fractal_Dim"] = np.nan
    if hurst == True:
        try:
            chaos["Hurst"] = nolds.hurst_rs(signal)
        except:
            print("NeuroKit warning: fractal_dimensions(): Failed to compute entropy.")
            chaos["Hurst"] = np.nan
    if dfa == True:
        try:
            chaos["DFA"] = nolds.dfa(signal)
        except:
            print("NeuroKit warning: fractal_dimensions(): Failed to compute entropy.")
            chaos["DFA"] = np.nan
    if lyap_r == True:
        try:
            chaos["Lyapunov_R"] = nolds.lyap_r(signal)
        except:
            print("NeuroKit warning: fractal_dimensions(): Failed to compute entropy.")
            chaos["Lyapunov_R"] = np.nan
    if lyap_e == True:
        try:
            chaos["Lyapunov_E"] = nolds.lyap_e(signal)
        except:
            print("NeuroKit warning: fractal_dimensions(): Failed to compute entropy.")
            chaos["Lyapunov_E"] = np.nan

    return(chaos)
