"""
Microstates submodule.
"""
from ..signal import fractal_dimensions

import numpy as np
import pandas as pd
import random
import collections  # Compute frequencies
import scipy
import scipy.signal

import sklearn
import sklearn.preprocessing
import sklearn.decomposition
import sklearn.cluster
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_gfp_features(data, gfp_peaks, freq, verbose=True):
    """
    Compute GFP features.
    """
    duration = len(data)/freq
    gfp_mean_peak_frequency = len(gfp_peaks)/duration
    gfp_mean_peak_duration = 1000/gfp_mean_peak_frequency
    if verbose is True:
        print("Approximately " + str(round(gfp_mean_peak_frequency, 2)) + " GFP peaks (average peak duration: " + str(round(gfp_mean_peak_duration, 2)) + " ms) per second.")
    return(gfp_mean_peak_frequency)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_gfp_peaks(data, method='GFPL1', smoothing_method=None, smoothing_window=100, peak_method="wavelet", normalize=False):
    """
    The Global Field Power (GFP) is a scalar measure of the strength of the scalp potential field and is calculated as the standard deviation of all electrodes at a given time point (Lehmann and Skrandies, 1980; Michel et al., 1993; Murray et al., 2008; Brunet et al., 2011). Between two GFP troughs, the strength of the potential field varies but the topography remains generally stable. The local maxima of the GFP are thus the best representative of a given microstate in terms of signal-to-noise ratio (Pascual-Marqui et al., 1995), corresponding to moments of high global neuronal synchronization (Skrandies, 2007).

    Parameters
    ----------
    X (ndarray):
        Array containing values for all time frames and channels.
        Dimension: number of time frames x number of channels
    method ({'GFPL1', 'GFPL2'}):
        `GFPL1` : use L1-Norm to compute GFP peaks
        `GFPL2` : use L2-Norm to compute GFP peaks
    smoothing_method ({'hamming', 'hanning'}):
            `hamming` : use hamming window to smooth
            `hanning` : use hanning window to smooth
    smoothing_window = int
        about 100
    peak_method = str
        "relative" or "wavelet"

    Returns
    ----------
        ret : ndarray
            GFP curve
    """
    ntf = data.shape[0]
    gfp = np.zeros((ntf, ))

    if method == 'GFPL2':
        for i in range(ntf):
            x = data[i,:]
            gfp[i] = np.sqrt(np.sum((x - x.mean())**2 / len(x) ))
    elif method == 'GFPL1':
        for i in range(ntf):
            x = data[i,:]
            gfp[i] = np.sum(np.abs(x - x.mean())) / len(x)

    if peak_method == "wavelet":
        gfp_peaks = np.asarray(scipy.signal.find_peaks_cwt(gfp, np.arange(1, 10)))  #we would expect a peak at about each 50 ms
    else:
        gfp_peaks = scipy.signal.argrelmax( gfp )[0]


    if smoothing_method == 'hamming':
        gfp = scipy.signal.convolve(gfp, scipy.signal.hamming(smoothing_window) )
    elif smoothing_method == 'hanning':
        gfp = scipy.signal.convolve(gfp, scipy.signal.hanning(smoothing_window) )


#    if normalize is True:
#        for i in range(data.shape[0]):
#            data[i,:] = data[i,:]/gfp[i]

    return (data, gfp, gfp_peaks)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_gfp_process(raws_list, names=None, scale=True):
    """
    """

    # If no names given, generate a range of ints
    if names is None:
        names = range(len(raws_list))

    # Initialize empty dict
    results = {}
    for subject in enumerate(raws_list):
        # Initialize an empty dict for each observation of the list
        results[names[subject[0]]] = {}

        # Convert to numpy array
        data = np.array(subject[1].to_data_frame())

        # find GFP peaks
        data, gfp, gfp_peaks = eeg_gfp_peaks(data)
        results[names[subject[0]]]["microstates_times"] = gfp_peaks

        # Compute and store mean GFP peak frequency
        results[names[subject[0]]]["microstates_frequency"] = eeg_gfp_features(data, gfp_peaks, freq=subject[1].info["sfreq"], verbose=False)
        results[names[subject[0]]]["data_sfreq"] = subject[1].info["sfreq"]

        # Select brain state at peaks
        data_peaks = data[gfp_peaks]
        # Store the data and scale parameters
        results[names[subject[0]]]["data_scaled"] = scale
        if scale is True:
            results[names[subject[0]]]["data"] = sklearn.preprocessing.scale(data_peaks)
        else:
            results[names[subject[0]]]["data"] = data_peaks

    return(results)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_ms_statistics(results, nonlinearity=True):
    """
    """
    for subject in results:

        # Frequencies of each microstate
        occurences = dict(collections.Counter(results[subject]["microstates"]))
        for microstate in occurences:

            results[subject]["frequency_" + str(microstate)] = occurences[microstate]/len(results[subject]["microstates"])

        # Compute fractal dimensions of the microstate sequence
        if nonlinearity is True:
            results[subject]["Nonlinearity"] = fractal_dimensions(results[subject]["microstates"])

    return(results)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_microstates(raws_list, names=None, scale=True, n_pca_comp=25, n_microstates=4, occurence_rejection_treshold=0.05, verbose=True):
    """
    """

    # 1. Compute GFP peaks for each subject
    # -------------------------------------------------------------------------
    results = eeg_gfp_process(raws_list, names=names, scale=scale)


    # 2. LEARNING FROM ALL DATA POINTS MICROSTATES PATTERN
    # -------------------------------------------------------------------------

    # Merge all data at peaks
    data_all = []
    for subject in results:
        data_all.append(results[subject]["data"])
    data_all = np.concatenate(data_all, axis=0)

    # Apply PCA to decompose the data
    data_all_pca = sklearn.decomposition.PCA(n_components=n_pca_comp).fit_transform(data_all)
    training_set = data_all_pca.copy()

     # Initalize clustering algorithm
    method = sklearn.cluster.KMeans(init='k-means++', n_clusters=n_microstates)


    everything_alright = False
    while everything_alright is False:
        everything_alright = True

        # Fit the algorithm
        method.fit(training_set)

    # 3. CLASSIFY FROM ALGORITHM EACH DATA POINT AND STORE IT
    # -------------------------------------------------------------------------

        # Predict the more likely cluster for each observation
        predicted = method.predict(training_set)


        # Check for abnormalities and prune the training set until none found
        occurences = dict(collections.Counter(predicted))
        for microstate in occurences:
            # is the frequency of one microstate inferior to a treshold
            if occurences[microstate] < len(data_all_pca)*occurence_rejection_treshold:
                print("NeuroKit Warning: eeg_microstates(): detected some outliers: refitting the classifier.")
                everything_alright = False
                training_set = training_set[np.where(predicted!=microstate)]


    # Predict the more likely cluster for each observation on the initial set
    predicted = method.predict(data_all_pca)

    # Store cluster data
    clusters = {}
    for microstate in range(n_microstates):
        clusters[microstate] = data_all[np.where(predicted==microstate)]

    # Store results for each run
    # Generate index attributing each point of the predicted data to its subject number
    index = []
    for subject in results:
        index += [subject] * len(results[subject]["data"])

    # For each subject, select the appropriate part of the predicted sequence and store it
    for subject in results:
        results[subject]["microstates"] = predicted[np.where(np.array(index)==subject)]


    # 3. COMPUTE INDICES AND STATISTICS
    # -------------------------------------------------------------------------
    results = eeg_ms_statistics(results, fractal_dim=True)


    return(results, method)