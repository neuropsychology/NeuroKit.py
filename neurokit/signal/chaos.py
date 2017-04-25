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
def chaos(signal, shannon=True, sampen=True, fractal_dim=True, hurst=True, dfa=True, lyap_r=True, lyap_e=True, emb_dim=2, tolerance="default"):
    """
    Returns several chaos/complexity indices of a signal (including entropy, fractal dimensions, Hurst and Lyapunov exponent etc.).

    Parameters
    ----------
    signal : list or array
        List or array of values.
    sampen : bool
        Compute approximate sample entropy (sampen).
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
    emb_dim : int
        The embedding dimension (length of vectors to compare).
    tolerance : float
        Distance threshold for two template vectors to be considered equal. Default is 0.2*std(signal).

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

    - **shannon entropy**: Entropy is a measure of unpredictability of the state, or equivalently, of its average information content.
    - **sample entropy (sampen)**: Measures the complexity of a time-series, based on approximate entropy. The sample entropy of a time series is defined as the negative natural logarithm of the conditional probability that two sequences similar for emb_dim points remain similar at the next point, excluding self-matches. A lower value for the sample entropy therefore corresponds to a higher probability indicating more self-similarity.
    - **correlation dimension**: A measure of the fractal dimension of a time series which is also related to complexity. The correlation dimension is a characteristic measure that can be used to describe the geometry of chaotic attractors. It is defined using the correlation sum C(r) which is the fraction of pairs of points X_i in the phase space whose distance is smaller than r.
    - **hurst**: The Hurst exponent is a measure of the "long-term memory" of a time series. It can be used to determine whether the time series is more, less, or equally likely to increase if it has increased in previous steps. This property makes the Hurst exponent especially interesting for the analysis of stock data.
    - **dfa**: DFA measures the Hurst parameter H, which is very similar to the Hurst exponent. The main difference is that DFA can be used for non-stationary processes (whose mean and/or variance change over time).
    - **lyap**: Positive Lyapunov exponents indicate chaos and unpredictability. Provides the algorithm of Rosenstein et al. (1993) to estimate the largest Lyapunov exponent and the algorithm of Eckmann et al. (1986) to estimate the whole spectrum of Lyapunov exponents.


    *Authors*

    - Christopher Schölzel (https://github.com/CSchoel)
    - tjugo (https://github.com/nikdon)
    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - nolds

    *See Also*

    - nolds package: https://github.com/CSchoel/nolds

    References
    -----------
    - Richman, J. S., & Moorman, J. R. (2000). Physiological time-series analysis using approximate entropy and sample entropy. American Journal of Physiology-Heart and Circulatory Physiology, 278(6), H2039-H2049.
    - Costa, M., Goldberger, A. L., & Peng, C. K. (2005). Multiscale entropy analysis of biological signals. Physical review E, 71(2), 021906.
    """

    if tolerance == "default":
        tolerance = 0.2*np.std(signal)

    chaos = {}
    if shannon is True:
        try:
            chaos["Shannon"] = entropy_shannon(signal)
        except:
            print("NeuroKit warning: chaos(): Failed to compute Shannon's entropy.")
            chaos["Entropy"] = np.nan
    if sampen is True:
        try:
            chaos["Sample_Entropy"] = nolds.sampen(signal, emb_dim, tolerance)
        except:
            print("NeuroKit warning: chaos(): Failed to compute sampen.")
            chaos["Entropy"] = np.nan
    if fractal_dim is True:
        try:
            chaos["Fractal_Dim"] = nolds.corr_dim(signal, emb_dim)
        except:
            print("NeuroKit warning: chaos(): Failed to compute fractal_dim.")
            chaos["Fractal_Dim"] = np.nan
    if hurst is True:
        try:
            chaos["Hurst"] = nolds.hurst_rs(signal)
        except:
            print("NeuroKit warning: chaos(): Failed to compute hurst.")
            chaos["Hurst"] = np.nan
    if dfa is True:
        try:
            chaos["DFA"] = nolds.dfa(signal)
        except:
            print("NeuroKit warning: chaos(): Failed to compute dfa.")
            chaos["DFA"] = np.nan
    if lyap_r is True:
        try:
            chaos["Lyapunov_R"] = nolds.lyap_r(signal)
        except:
            print("NeuroKit warning: chaos(): Failed to compute lyap_r.")
            chaos["Lyapunov_R"] = np.nan
    if lyap_e is True:
        try:
            chaos["Lyapunov_E"] = nolds.lyap_e(signal)
        except:
            print("NeuroKit warning: chaos(): Failed to compute lyap_e.")
            chaos["Lyapunov_E"] = np.nan

    return(chaos)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def entropy_shannon(signal):
    """
    Returns the shannon entropy. Copied from the `pyEntropy <https://github.com/nikdon/pyEntropy>`_ repo by tjugo.

    Parameters
    ----------
    signal : list or array
        List or array of values.


    Returns
    ----------
    shannon_entropy : float
        The Shannon Entropy as float value.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> signal = [5, 1, 7, 2, 5, 1, 7, 4, 6, 7, 5, 4, 1, 1, 4, 4]
    >>> shannon_entropy = nk.entropy_shannon(signal)

    Notes
    ----------
    *Details*

    - **shannon entropy**: Entropy is a measure of unpredictability of the state, or equivalently, of its average information content.


    *Authors*

    - tjugo (https://github.com/nikdon)

    *Dependencies*

    - None

    *See Also*

    - pyEntropy package: https://github.com/nikdon/pyEntropy

    References
    -----------
    - None
    """

    # Check if string
    if not isinstance(signal, str):
        signal = list(signal)

    # Create a frequency data
    data_set = list(set(signal))
    freq_list = []
    for entry in data_set:
        counter = 0.
        for i in signal:
            if i == entry:
                counter += 1
        freq_list.append(float(counter) / len(signal))

    # Shannon entropy
    shannon_entropy = 0.0
    for freq in freq_list:
        shannon_entropy += freq * np.log2(freq)
    shannon_entropy = -shannon_entropy

    return(shannon_entropy)