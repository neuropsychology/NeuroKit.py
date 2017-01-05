"""
Microstates submodule.
"""
from ..signal import fractal_dimensions
from ..miscellaneous import find_following_duplicates
from ..miscellaneous import load_object
from ..statistics import feature_reduction
from ..statistics import z_score

import numpy as np
import pandas as pd
import collections  # Compute frequencies
import scipy
import mne
import PIL
import os

import scipy.signal
import scipy.spatial.distance

import sklearn
import sklearn.preprocessing
import sklearn.decomposition
import sklearn.cluster
import sklearn.metrics


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_gfp_peaks(data, gflp_method='GFPL1', smoothing=False, smoothing_window=100, peak_method="wavelet", normalize=False):
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
    smoothing ({'hamming', 'hanning'}):
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
    gfp_curve = np.zeros((ntf, ))

    if gflp_method == 'GFPL2':
        for i in range(ntf):
            x = data[i,:]
            gfp_curve[i] = np.sqrt(np.sum((x - x.mean())**2 / len(x) ))
    elif gflp_method == 'GFPL1':
        for i in range(ntf):
            x = data[i,:]
            gfp_curve[i] = np.sum(np.abs(x - x.mean())) / len(x)

    if peak_method == "wavelet":
        gfp_peaks = np.asarray(scipy.signal.find_peaks_cwt(gfp_curve, np.arange(1, 10)))  #we would expect a peak at about each 50 ms
    else:
        gfp_peaks = scipy.signal.argrelmax(gfp_curve)[0]


    if smoothing == 'hamming':
        gfp_curve = scipy.signal.convolve(gfp_curve, scipy.signal.hamming(smoothing_window) )
    elif smoothing == 'hanning':
        gfp_curve = scipy.signal.convolve(gfp_curve, scipy.signal.hanning(smoothing_window) )
    else:
        pass

    # Normalize
    if normalize is True:
        for i in range(len(data)):
            data[i,:] = data[i,:]/gfp_curve[i]


    return (data, gfp_curve, gfp_peaks)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_gfp(raws, gflp_method="GFPL1", scale=True, normalize=True, smoothing=None):
    """
    Run the GFP analysis.
    """

    # Load data if necessary
    if isinstance(raws, str):
        raws = load_object(filename=raws)

    # Initialize empty dict
    gfp = {}
    for participant in raws:

        gfp[participant] = {}
        for run in raws[participant]:

            # Generate empty dic
            gfp[participant][run] = {}

            # Assign raw object to raw
            raw = raws[participant][run].copy()

            # Check if MEG or EEG data
            if True in set(["MEG" in ch for ch in raw.info["ch_names"]]):
                meg = True
                eeg = False
            else:
                meg = False
                eeg = True

            # Save ECG channel
            try:
                gfp[participant][run]["ecg"] = np.array(raw.copy().pick_types(meg=False, eeg=False, ecg=True).to_data_frame())
            except ValueError:
                gfp[participant][run]["ecg"] = np.nan

            # Select appropriate channels
            data = raw.copy().pick_types(meg=meg, eeg=eeg)
            gfp[participant][run]["data_info"] = data.info
            gfp[participant][run]["data_freq"] = data.info["sfreq"]
            gfp[participant][run]["run_duration"] = len(data) / data.info["sfreq"]

            # Convert to numpy array
            data = np.array(data.to_data_frame())

            # find GFP peaks
            data, gfp_curve, gfp_peaks = eeg_gfp_peaks(data,
                                                 gflp_method=gflp_method,
                                                 smoothing=smoothing,
                                                 smoothing_window=100,
                                                 peak_method="wavelet",
                                                 normalize=normalize)
            # Store them
            gfp[participant][run]["microstates_times"] = gfp_peaks


            # Select brain state at peaks
            data_peaks = data[gfp_peaks]

            # Store the data and scale parameters
            if scale is True:
                gfp[participant][run]["data"] = z_score(data_peaks)
            else:
                gfp[participant][run]["data"] = data_peaks

            gfp[participant][run]["data_scale"] = scale
            gfp[participant][run]["data_normalize"] = normalize
            gfp[participant][run]["data_smoothing"] = smoothing



    return(gfp)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
#def eeg_microstates_keypy(confobj, nch, eeg, gfp_peak_indices, gfp_curve):
#    """
#    Keypy algorithm.
#    """
#    nch=len(data)
#    eeg=data
#    gfp_peak_indices=
#    gfp_curve
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_microstates_clustering(data, n_microstates=4, clustering_method="kmeans", n_jobs=1, n_init=25, occurence_rejection_treshold=0.05, max_refitting=5, verbose=True):
    """
    Fit the clustering algorithm.
    """
    # Create training set
    training_set = data.copy()

    if verbose is True:
        print("- Initializing the clustering algorithm...")
    if clustering_method == "kmeans":
        algorithm = sklearn.cluster.KMeans(init='k-means++', n_clusters=n_microstates, n_init=n_init, n_jobs=n_jobs)
    elif clustering_method == "spectral":
        algorithm = sklearn.cluster.SpectralClustering(n_clusters=n_microstates, n_init=n_init, n_jobs=n_jobs)
    elif clustering_method == "agglom":
        algorithm = sklearn.cluster.AgglomerativeClustering(n_clusters=n_microstates, linkage="complete")
    elif clustering_method == "dbscan":
        algorithm = sklearn.cluster.DBSCAN(min_samples=100)
    elif clustering_method == "affinity":
        algorithm = sklearn.cluster.AffinityPropagation(damping=0.5)
    else:
        print("NeuroKit Error: eeg_microstates(): clustering_method must be 'kmeans', 'spectral', 'dbscan', 'affinity' or 'agglom'")


    refitting = 0  # Initialize the number of refittings
    good_fit_achieved = False
    while good_fit_achieved is False:
        good_fit_achieved = True
        if verbose is True:
            print("- Fitting the classifier...")
        # Fit the algorithm
        algorithm.fit(training_set)

        if verbose is True:
            print("- Clustering back the initial data...")
        # Predict the more likely cluster for each observation
        predicted = algorithm.fit_predict(training_set)

        if verbose is True:
            print("- Check for abnormalities...")
        # Check for abnormalities and prune the training set until none found
        occurences = dict(collections.Counter(predicted))
        masks = [np.array([True]*len(training_set))]
        for microstate in occurences:
            # is the frequency of one microstate inferior to a treshold
            if occurences[microstate] < len(data)*occurence_rejection_treshold:
                good_fit_achieved = False
                refitting += 1  # Increment the refitting
                print("NeuroKit Warning: eeg_microstates(): detected some outliers: refitting the classifier (n=" + str(refitting) + ").")
                masks.append(predicted!=microstate)
        mask = np.all(masks, axis=0)
        training_set = training_set[mask]

    return(algorithm)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_microstates_features(results, method, ecg=True, nonlinearity=True, verbose=True):
    """
    Compute statistics and features for/of the microstates.
    """

    for participant in results:
        for run in results[participant]:
            if verbose is True:
                print("- " + participant)

            # Frequencies of each microstate
            occurences = dict(collections.Counter(results[participant][run]["microstates"]))

            # Compute fractal dimensions of the microstate sequence
            if nonlinearity is True:
                results[participant][run]["nonlinearity"] = fractal_dimensions(results[participant][run]["microstates"])

            # ECG coherence
#            results[participant][run]["ecg"]
#            statsmodels.tsa.stattools.grangercausalitytests([])

            results[participant][run]["parameters"] = {}
            # Compute parameters for each microstates:
            for microstate in set(method["microstates"]):

                results[participant][run]["parameters"][microstate] = {}

                try:
                    # Coverage
                    results[participant][run]["parameters"][microstate]["coverage"] = occurences[microstate]/len(results[participant][run]["microstates"])

                    # Duration
                    uniques = find_following_duplicates(results[participant][run]["microstates"])
                    uniques_times = results[participant][run]["microstates_times"][np.where(uniques)]
                    uniques_ms = results[participant][run]["microstates"][np.where(uniques)]
                    times = uniques_times[np.array(np.where(uniques_ms==microstate))]
                    times_1 = np.take(uniques_times, np.array(np.where(uniques_ms==microstate)) + 1, mode='clip')
                    results[participant][run]["parameters"][microstate]["duration"] = np.mean(times_1 - times)/results[participant][run]["data_sfreq"]*1000

                    # Occurence
                    results[participant][run]["parameters"][microstate]["occurence"] = occurences[microstate] / results[participant][run]["run_duration"]

                except KeyError:
                    results[participant][run]["parameters"][microstate]["coverage"] = 0
                    results[participant][run]["parameters"][microstate]["duration"] = np.nan
                    results[participant][run]["parameters"][microstate]["occurence"] = 0
    return(results)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_microstates(gfp, n_microstates=4, clustering_method="kmeans", n_jobs=1, n_init=25, occurence_rejection_treshold=0.05, max_refitting=5, clustering_metrics=True, good_fit_treshold=0, feature_reduction_method="PCA", n_features=32, nonlinearity=True, verbose=True):
    """
    Run the full microstates analysis.

    Parameters
    ----------
    raws = dict
        Two levels dictionary containing the participants, within which the run(s), associated with an mne.io.Raw class object.
    method ({'GFPL1', 'GFPL2'}):
        `GFPL1` : use L1-Norm to compute GFP peaks
        `GFPL2` : use L2-Norm to compute GFP peaks
    smoothing ({'hamming', 'hanning'}):
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

    Example
    ----------
    NA

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - pygame 1.9.2
    """
    if isinstance(gfp, str):
        results = load_object(filename=gfp)
    else:
        results = gfp

    if verbose is True:
        print("""
    STARTING MICROSTATES ANALYSIS...
    # ===================================
    Infering microstates pattern from all data points...
    # -----------------------------------------
        """)

    # Create empty dict to store all info about the method used
    method = {}

    # Merge all data at peaks
    # Also, extract some info about the GFP method
    data_all = []
    for participant in results:
        for run in results[participant]:
            data_all.append(results[participant][run]["data"])

            # GFP method
            method["data_scale"] = results[participant][run]["data_scale"]
            method["data_normalize"] = results[participant][run]["data_normalize"]
            method["data_smoothing"] = results[participant][run]["data_smoothing"]
    data_all = np.concatenate(data_all, axis=0)


    # Feature reduction
    if verbose is True:
        print("- Applying Feature Reduction...")
    data_processed = feature_reduction(data_all,
                                       method=feature_reduction_method,
                                       n_features=n_features)

    try:
        # Fit clustering aglorithm
        algorithm = eeg_microstates_clustering(data=data_processed,
                                   n_microstates=n_microstates,
                                   clustering_method=clustering_method,
                                   n_jobs=n_jobs,
                                   n_init=n_init,
                                   occurence_rejection_treshold=occurence_rejection_treshold,
                                   max_refitting=max_refitting,
                                   verbose=verbose)
    except:
        print("NeuroKit Error: eeg_microstates(): error in clustering.")
        return(data_processed, method)


    if verbose is True:
        print("- Storing the algorithm...")
    # Store results on a global level

    method["algorithm"] = algorithm
    method["raw.info_example"] = results[participant][run]["data_info"]  # Take the info of the last participant nad last run
    method["feature_reduction_method"] = feature_reduction_method
    method["n_features"] = n_features
    method["data"] = data_all
    method["clustering_method"] = clustering_method
    method["n_microstates"] = len(data_all)

    if verbose is True:
        print("""
    Computing microstates features on a global level...
    # ----------------------------------------------------
        """)
    # Predict the more likely cluster for each observation on the initial set
    predicted = algorithm.fit_predict(data_processed)
    method["microstates"] = predicted



    # -------------------------------------------------------------------------
    if clustering_metrics is True:
        if verbose is True:
            print("""
    Computing microstates metrics...
    # ----------------------------------------------------
            """)
        # Get metrics about the clustering
        method["silhouette_coefs"] = sklearn.metrics.silhouette_samples(data_processed, predicted)  #  compute the silhouette coefficient for each data point
        method["calinski_harabaz"] = sklearn.metrics.calinski_harabaz_score(data_processed, predicted)

        # Mark as Bad the data points with bad fit index
        method["microstates_good_fit"] = np.where(method["silhouette_coefs"]>good_fit_treshold, predicted, "Bad")
        method["percentage_bad_fit"] = dict(collections.Counter(method["microstates_good_fit"]))["Bad"]/len(predicted)


    # -------------------------------------------------------------------------
    if verbose is True:
        print("""
    Computing microstates features on a local level...
    # ---------------------------------------------------
        """)
    # Store results for each run
    # Generate index attributing each point of the predicted data to its subject number
    index_participant = []
    index_run = []
    for participant in results:
        for run in results[participant]:
            index_participant += [participant] * len(results[participant][run]["data"])
            index_run += [run] * len(results[participant][run]["data"])

    # For each subject, select the appropriate part of the predicted sequence and store it
    for participant in results:
        for run in results[participant]:
            # Create appropriate bool masks, combine them then select appropriate chunk of data
            mask1 = np.array(index_participant)==participant
            mask2 = np.array(index_run)==run
            mask = np.all([mask1, mask2], axis=0)
            results[participant][run]["microstates"] = method["microstates"][mask]

    results = eeg_microstates_features(results, method, nonlinearity=nonlinearity, verbose=verbose)

    if verbose is True:
        print("""
    Done.
    # ------
        """)
    return(results, method)




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_microstates_plot(method, path="", extension=".png", show_sensors_position=False, show_sensors_name=False, plot=True, save=True, dpi=150, contours=0, colorbar=False, separate=False):
    """
    Plot the microstates.
    """
    # Generate and store figures
    figures = []
    names = []

    # Check if microstates metrics available
    try:
        microstates = method["microstates_good_fit"]
    except KeyError:
        microstates = method["microstates"]

    # Create individual plot for each microstate
    for microstate in set(microstates):
        if microstate != "Bad":
            values = np.mean(method["data"][np.where(microstates == microstate)], axis=0)
            values = np.array(values, ndmin=2).T
            evoked = mne.EvokedArray(values, method["raw.info_example"], 0)

            fig = evoked.plot_topomap(times=0, title=microstate, size=6, contours=contours, time_format="", show=plot, colorbar=colorbar, show_names=show_sensors_name, sensors=show_sensors_position)

            figures.append(fig)

            # Save separate figures
            name = path + "microstate_%s_%s%s%s_%s%i_%s%s" %(microstate, method["data_scale"],  method["data_normalize"], method["data_smoothing"], method["feature_reduction_method"], method["n_features"], method["clustering_method"], extension)

            fig.savefig(name, dpi=dpi)
            names.append(name)

    # Save Combined plot
    if save is True:
        # Combine all plots
        image_template = PIL.Image.open(names[0])
        X, Y = image_template.size
        image_template.close()

        combined = PIL.Image.new('RGB', (int(X*len(set(microstates))/2), int( Y*len(set(microstates))/2)))
        fig = 0
        for x in np.arange(0, len(set(microstates))/2*int(X), int(X)):
            for y in np.arange(0, len(set(microstates))/2*int(Y), int(Y)):
                try:
                    newfig = PIL.Image.open(names[fig])
                    combined.paste(newfig, (int(x), int(y)))
                    newfig.close()
                except:
                    pass
                fig += 1
#combined.show()
        combined_name = path + "microstates_%s%s%s_%s%i_%s%s" %(method["data_scale"],  method["data_normalize"], method["data_smoothing"], method["feature_reduction_method"], method["n_features"], method["clustering_method"], extension)
        combined.save(combined_name)

    # Detete separate plots in needed
    if separate is False or save is False:
        for name in names:
            os.remove(name)

    return(figures)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_microstates_relabel(method, results, microstates_labels, reverse_microstates=None):
    """
    Relabel the microstates.
    """

    microstates = list(method['microstates'])

    for index, microstate in enumerate(method['microstates']):

        if microstate in list(reverse_microstates.keys()):
            microstates[index] = reverse_microstates[microstate]
            method["data"][index] = -1*method["data"][index]

        if microstate in list(microstates_labels.keys()):
            microstates[index] = microstates_labels[microstate]

    method['microstates'] = np.array(microstates)

    return(results, method)