# -*- coding: utf-8 -*-
import nolds
import numpy as np

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def complexity(signal, shannon=True, sampen=True, multiscale=True, fractal_dim=True, hurst=True, dfa=True, lyap_r=True, lyap_e=False, emb_dim=2, tolerance="default"):
    """
    Returns several chaos/complexity indices of a signal (including entropy, fractal dimensions, Hurst and Lyapunov exponent etc.).

    Parameters
    ----------
    signal : list or array
        List or array of values.
    shannon : bool
        Computes Shannon entropy.
    sampen : bool
        Computes approximate sample entropy (sampen) using Chebychev and Euclidean distances.
    multiscale : bool
        Computes multiscale entropy (MSE). Note that it uses the 'euclidean' distance.
    fractal_dim : bool
        Computes the fractal (correlation) dimension.
    hurst : bool
        Computes the Hurst exponent.
    dfa : bool
        Computes DFA.
    lyap_r : bool
        Computes Positive Lyapunov exponents (Rosenstein et al. (1993) method).
    lyap_e : bool
        Computes Positive Lyapunov exponents (Eckmann et al. (1986) method).
    emb_dim : int
        The embedding dimension (*m*, the length of vectors to compare). Used in sampen and fractal_dim.
    tolerance : float
        Distance *r* threshold for two template vectors to be considered equal. Default is 0.2*std(signal). Used in sampen and fractal_dim.

    Returns
    ----------
    complexity : dict
        Dict containing values for each indices.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> signal = [5, 1, 7, 2, 5, 1, 7, 4, 6, 7, 5, 4, 1, 1, 4, 4]
    >>> complexity = nk.complexity(signal)

    Notes
    ----------
    *Details*

    - **shannon entropy**: Entropy is a measure of unpredictability of the state, or equivalently, of its average information content.
    - **sample entropy (sampen)**: Measures the complexity of a time-series, based on approximate entropy. The sample entropy of a time series is defined as the negative natural logarithm of the conditional probability that two sequences similar for emb_dim points remain similar at the next point, excluding self-matches. A lower value for the sample entropy therefore corresponds to a higher probability indicating more self-similarity.
    - **multiscale entropy**: Multiscale entropy (MSE) analysis is a new method of measuring the complexity of finite length time series.
    - **fractal dimension**: A measure of the fractal (or correlation) dimension of a time series which is also related to complexity. The correlation dimension is a characteristic measure that can be used to describe the geometry of chaotic attractors. It is defined using the correlation sum C(r) which is the fraction of pairs of points X_i in the phase space whose distance is smaller than r.
    - **hurst**: The Hurst exponent is a measure of the "long-term memory" of a time series. It can be used to determine whether the time series is more, less, or equally likely to increase if it has increased in previous steps. This property makes the Hurst exponent especially interesting for the analysis of stock data.
    - **dfa**: DFA measures the Hurst parameter H, which is very similar to the Hurst exponent. The main difference is that DFA can be used for non-stationary processes (whose mean and/or variance change over time).
    - **lyap**: Positive Lyapunov exponents indicate chaos and unpredictability. Provides the algorithm of Rosenstein et al. (1993) to estimate the largest Lyapunov exponent and the algorithm of Eckmann et al. (1986) to estimate the whole spectrum of Lyapunov exponents.


    *Authors*

    - Christopher Schölzel (https://github.com/CSchoel)
    - tjugo (https://github.com/nikdon)
    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - nolds
    - numpy

    *See Also*

    - nolds package: https://github.com/CSchoel/nolds
    - pyEntropy package: https://github.com/nikdon/pyEntropy

    References
    -----------
    - Richman, J. S., & Moorman, J. R. (2000). Physiological time-series analysis using approximate entropy and sample entropy. American Journal of Physiology-Heart and Circulatory Physiology, 278(6), H2039-H2049.
    - Costa, M., Goldberger, A. L., & Peng, C. K. (2005). Multiscale entropy analysis of biological signals. Physical review E, 71(2), 021906.
    """

    if tolerance == "default":
        tolerance = 0.2*np.std(signal)

    # Initialize results storing
    complexity = {}

    # Shannon
    if shannon is True:
        try:
            complexity["Shannon_Entropy"] = entropy_shannon(signal)
        except:
            print("NeuroKit warning: complexity(): Failed to compute Shannon entropy.")
            complexity["Shannon_Entropy"] = np.nan

    # Sampen
    if sampen is True:
        try:
            complexity["Sample_Entropy_Chebychev"] = nolds.sampen(signal, emb_dim, tolerance, dist="chebychev", debug_plot=False, plot_file=None)
        except:
            print("NeuroKit warning: complexity(): Failed to compute sample entropy (sampen) using chebychev distance.")
            complexity["Sample_Entropy_Chebychev"] = np.nan
        try:
            complexity["Sample_Entropy_Euclidean"] = nolds.sampen(signal, emb_dim, tolerance, dist="euclidean", debug_plot=False, plot_file=None)
        except:
            print("NeuroKit warning: complexity(): Failed to compute sample entropy (sampen) using euclidean distance.")
            complexity["Sample_Entropy_Euclidean"] = np.nan

    # multiscale
    if multiscale is True:
        try:
            complexity["Multiscale_Entropy"] = entropy_multiscale(signal, emb_dim, tolerance)
        except:
            print("NeuroKit warning: complexity(): Failed to compute Multiscale Entropy (MSE).")
            complexity["Multiscale_Entropy"] = np.nan


    # fractal_dim
    if fractal_dim is True:
        try:
            complexity["Fractal_Dimension"] = nolds.corr_dim(signal, emb_dim, rvals=None, fit="RANSAC", debug_plot=False, plot_file=None)
        except:
            print("NeuroKit warning: complexity(): Failed to compute fractal_dim.")
            complexity["Fractal_Dimension"] = np.nan

    # Hurst
    if hurst is True:
        try:
            complexity["Hurst"] = nolds.hurst_rs(signal, nvals=None, fit="RANSAC", debug_plot=False, plot_file=None)
        except:
            print("NeuroKit warning: complexity(): Failed to compute hurst.")
            complexity["Hurst"] = np.nan

    # DFA
    if dfa is True:
        try:
            complexity["DFA"] = nolds.dfa(signal, nvals=None, overlap=True, order=1, fit_trend="poly", fit_exp="RANSAC", debug_plot=False, plot_file=None)
        except:
            print("NeuroKit warning: complexity(): Failed to compute dfa.")
            complexity["DFA"] = np.nan

    # Lyap_r
    if lyap_r is True:
        try:
            complexity["Lyapunov_R"] = nolds.lyap_r(signal, emb_dim=10, lag=None, min_tsep=None, tau=1, min_vectors=20, trajectory_len=20, fit="RANSAC", debug_plot=False, plot_file=None)
        except:
            print("NeuroKit warning: complexity(): Failed to compute lyap_r.")
            complexity["Lyapunov_R"] = np.nan

    # Lyap_e
    if lyap_e is True:
        try:
            result = nolds.lyap_e(signal, emb_dim=10, matrix_dim=4, min_nb=None, min_tsep=0, tau=1, debug_plot=False, plot_file=None)
            for i, value in enumerate(result):
                complexity["Lyapunov_E_" + str(i)] = value
        except:
            print("NeuroKit warning: complexity(): Failed to compute lyap_e.")
            complexity["Lyapunov_E"] = np.nan

    return(complexity)


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

    - numpy

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






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def entropy_multiscale(signal, emb_dim=2, tolerance="default"):
    """
    Returns the Multiscale Entropy. Copied from the `pyEntropy <https://github.com/nikdon/pyEntropy>`_ repo by tjugo. Uses sample entropy with 'chebychev' distance.

    Parameters
    ----------
    signal : list or array
        List or array of values.
    emb_dim : int
        The embedding dimension (*m*, the length of vectors to compare).
    tolerance : float
        Distance *r* threshold for two template vectors to be considered equal. Default is 0.2*std(signal).

    Returns
    ----------
    multiscale_entropy : float
        The Multiscale Entropy as float value.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> signal = [5, 1, 7, 2, 5, 1, 7, 4, 6, 7, 5, 4, 1, 1, 4, 4]
    >>> multiscale_entropy = nk.entropy_multiscale(signal)

    Notes
    ----------
    *Details*

    - **multiscale entropy**: Entropy is a measure of unpredictability of the state, or equivalently, of its average information content. Multiscale entropy (MSE) analysis is a new method of measuring the complexity of finite length time series.


    *Authors*

    - tjugo (https://github.com/nikdon)
    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - numpy

    *See Also*

    - pyEntropy package: https://github.com/nikdon/pyEntropy

    References
    -----------
    - Richman, J. S., & Moorman, J. R. (2000). Physiological time-series analysis using approximate entropy and sample entropy. American Journal of Physiology-Heart and Circulatory Physiology, 278(6), H2039-H2049.
    - Costa, M., Goldberger, A. L., & Peng, C. K. (2005). Multiscale entropy analysis of biological signals. Physical review E, 71(2), 021906.
    """
    if tolerance == "default":
        tolerance = 0.2*np.std(signal)

    n = len(signal)
    mse = np.zeros((1, emb_dim))

    for i in range(emb_dim):

        b = int(np.fix(n / (i + 1)))
        temp_ts = [0] * int(b)

        for j in range(b):
            num = sum(signal[j * (i + 1): (j + 1) * (i + 1)])
            den = i + 1
            temp_ts[j] = float(num) / float(den)
        # Replaced the sample entropy computation with nolds' one...
#        se = sample_entropy(temp_ts, 1, tolerance)
        se = nolds.sampen(temp_ts, 1, tolerance, dist="euclidean", debug_plot=False, plot_file=None)

        mse[0, i] = se

    multiscale_entropy = mse[0][emb_dim-1]

    return (multiscale_entropy)