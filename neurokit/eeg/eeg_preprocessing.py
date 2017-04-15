"""
Preprocessing EEG submodule.
"""
import numpy as np
import mne


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_filter(raw, lowpass=1, highpass=40, notch=True, method="fir"):
    """
    Applies a zero-phase filter on EEG/MEG data.

    Parameters
    ----------
    raw : mne.io.Raw
        Raw EEG data.
    lowpass : int
        Lowpass filter frequency in Hz.
    highpass : int
        Highpass filter frequency in Hz.
    notch : bool
        Apply additional notch filter on the 50Hz band.
    method : str
        'fir' will use overlap-add FIR filtering, 'iir' will use IIR forward-backward filtering (via filtfilt).


    Returns
    ----------
    raw : mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw = nk.eeg_filter(raw)

    Notes
    ----------
    *Authors*

    - MNE dev team (http://martinos.org/mne/dev/index.html)

    *Dependencies*

    - mne

    *See Also*

    - mne package: http://martinos.org/mne/dev/index.html
    """
    if notch == True:
        raw.notch_filter(np.arange(50, 451, 50),
                         method=method)

    if lowpass is not None and highpass is not None:
        raw.filter(lowpass,
                   highpass,
                   method=method)
    return(raw)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_ica(raw, eog=True, eog_treshold=3.0, ecg=True, ecg_treshold=3.0, method='fastica', random_state=23, n_components=0.95, plot=False, decim=3, reject=None):
    """
    Applies ICA to remove eog and/or ecg artifacts.

    Parameters
    ----------
    raw : mne.io.Raw
        Raw EEG data.
    eog : bool
        Remove EOG's artifacts.
    eog_treshold : float
        The value above which a feature is classified as outlier.
    ecg : bool
        Remove ECG's artifacts.
    ecg_treshold : float
        The value above which a feature is classified as outlier. If no existing ECG channel, decrease it around 0.25.
    method : str
        ICA method. 'fastica', 'infomax' or 'extended-infomax'.
    n_components : int
        The number of components used for ICA decomposition. If int, it must be smaller then max_pca_components. If None, all PCA components will be used. If float between 0 and 1 components will be selected by the cumulative percentage of explained variance.
    random_state : int
        Seed used to initialize the FastICA estimation.
    plot : bool
        Plot results.
    decim : int
        Increment for selecting each nth time slice. If None, all samples within start and stop are used.
    reject : dict or None
        Rejection parameters based on peak-to-peak amplitude.


    Returns
    ----------
    raw : mne.io.Raw
        Raw data in FIF format.

    Example
    ----------
    >>> import neurokit as nk
    >>> raw, ica = nk.eeg_ica(raw)

    Notes
    ----------
    *Authors*

    - MNE dev team (http://martinos.org/mne/dev/index.html)

    *Dependencies*

    - mne

    *See Also*

    - mne package: http://martinos.org/mne/dev/index.html
    """
    ica = mne.preprocessing.ICA(method=method,  # for comparison with EEGLAB try "extended-infomax" here
                                random_state=random_state,  # random seed
                                n_components=n_components
                                )
    # Check if MEG or EEG data
    if True in set(["MEG" in ch for ch in raw.info["ch_names"]]):
        meg = True
        eeg = False
    else:
        meg = False
        eeg = True

    picks = mne.pick_types(raw.info, meg=meg, eeg=eeg, eog=False, ecg=False, stim=False, exclude='bads', bio=False)

    ica.fit(raw, picks=picks, decim=decim, reject=reject)

    if eog is True:
        eog_inds, scores = ica.find_bads_eog(raw, threshold=eog_treshold)
        eog_inds = eog_inds[0:2]  # Exclude max 2 components
        if plot is True:
            ica.plot_scores(scores, exclude=eog_inds, title='eog components', labels='eog')
            ica.plot_sources(raw, exclude=eog_inds, title='eog components')
            ica.plot_components(eog_inds, title='eog components', colorbar=True)

        ica.exclude += eog_inds


    if ecg is True:
        # If existing ECG channel
        try:
            raw.copy().pick_types(meg=False, eeg=False, ecg=True)
            ecg_inds, scores = ica.find_bads_ecg(raw, method='correlation', threshold=ecg_treshold)
        except ValueError:
            ecg_epochs = mne.preprocessing.create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=picks)
            ecg_inds, scores = ica.find_bads_ecg(ecg_epochs, method='ctps', threshold=0.8)
        ecg_inds = ecg_inds[0:3]  # Exclude max 3 components
        if plot is True:
            ica.plot_scores(scores, exclude=ecg_inds, title='ecg components', labels='ecg')
            ica.plot_sources(raw, exclude=ecg_inds, title='eog')
            ica.plot_components(ecg_inds, title='eog', colorbar=True)
        ica.exclude += eog_inds


    if plot is True:
        # estimate average artifact
        eog_evoked = mne.preprocessing.create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=picks).average()
        ica.plot_sources(eog_evoked, exclude=eog_inds)  # plot EOG sources + selection
        ica.plot_overlay(eog_evoked, exclude=eog_inds)  # plot EOG cleaning

        ecg_evoked = mne.preprocessing.create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=picks).average()
        ica.plot_sources(ecg_evoked, exclude=ecg_inds)  # plot ECG sources + selection
        ica.plot_overlay(ecg_evoked, exclude=ecg_inds)  # plot ECG cleaning


        # check the amplitudes do not change
        ica.plot_overlay(raw)  # EOG artifacts remain


    raw =ica.apply(raw)
    return(raw, ica)






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_ssp(raw, eog=True, ecg= True, plot=False):
    """
    Apply SSP artifacts correction.
    """
    if eog is True:
        projs, events = mne.preprocessing.compute_proj_eog(raw, average=True)
        eog_projs = projs[-2:]
        if plot is True:
            mne.viz.plot_projs_topomap(eog_projs, layout=mne.channels.find_layout(raw.info))

    if ecg is True:
        projs, events = mne.preprocessing.compute_proj_ecg(raw, average=True)
        ecg_projs = projs[-2:]
        if plot is True:
            mne.viz.plot_projs_topomap(ecg_projs, layout=mne.channels.find_layout(raw.info))

    raw.info['projs'] += eog_projs + ecg_projs

    return(raw)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_eog_window(raw, duration=0.5):
    """
    Cover the whole blink with full duration.
    """
    average_eog = mne.preprocessing.create_eog_epochs(raw).average()
    print('We found %i EOG events' % average_eog.nave)

    eog_events = mne.preprocessing.find_eog_events(raw)
    n_blinks = len(eog_events)
    onset = eog_events[:, 0] / raw.info['sfreq'] - (duration/2)
    duration = np.repeat(duration, n_blinks)
    raw.annotations = mne.Annotations(onset,
                                      duration,
                                      ['bad blink'] * n_blinks,
                                      orig_time=raw.info['meas_date'])
    return(raw)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_epoching(raw, events, event_id, tmin=-0.2, tmax=1, eog_reject=600e-6, proj=True, detrend=1, drop_bad=True, remove_eog_channels=True, baseline=(None, 0)):
    """
    """
    if eog_reject is not None:
        # Peak-to-peak rejection parameters (amplitude ranges as floats)
        reject = {"eog": eog_reject}
    else:
        reject = None

    picks = mne.pick_types(raw.info,
                           meg=False,
                           eeg=True,
                           eog=True,
                           stim=False,
                           exclude='bads'
                           )

    epochs = mne.Epochs(raw,
                        events=events,
                        event_id=event_id,
                        tmin=tmin,
                        tmax=tmax,
                        picks=picks,
                        add_eeg_ref=True,
                        reject=reject,  # Adjust values carefully
                        reject_by_annotation=drop_bad,
                        proj=proj,  # With SSP projections
                        detrend=detrend,  # "None", 1: Linear detrend, 0 DC detrend,
                        baseline=baseline,
                        preload = True
                        )
    # Drop bads
    if drop_bad == True:
        epochs.drop_bad()

    if remove_eog_channels == True:
        epochs.pick_types(meg=False, eeg=True)
    return(epochs)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_select_sensor_area(include="all", exclude=None, hemisphere="both", include_central=True):
    """
    Returns list of electrodes names (according to a 10-20 EEG montage). This function is probably not very flexibile. Looking for help to improve it.

    Parameters
    ----------
    include : str
        Sensor area to include.
    exclude : str or None
        Sensor area to exclude.
    hemisphere : both
        Select both hemispheres?
    include_central : bool
        if `hemisphere != "both"`, select the central line?

    Returns
    ----------
    sensors : list
        List of sensors corresponding to the selected area.

    Example
    ----------
    >>> import neurokit as nk
    >>> nk.eeg_select_sensor_area(include="F", exclude="C")


    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    References
    ------------
    - None
    """
    sensors = ['AF3', 'AF4', 'AF7', 'AF8', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6', 'CPz', 'Cz', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'FC1', 'FC2', 'FC3', 'FC4', 'FC5', 'FC6', 'Fp1', 'Fp2', 'FT10', 'FT7', 'FT8', 'FT9', 'O1', 'O2', 'Oz', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'PO3', 'PO4', 'PO7', 'PO8', 'POz', 'Pz', 'FCz', 'T7', 'T8', 'TP10', 'TP7', 'TP8', 'TP9', 'AFz']

    if include != "all":
        sensors = [s for s in sensors if include in s]

    if exclude != None:
        if isinstance(exclude, str):
            exclude = [exclude]
        for to_exclude in exclude:
            sensors = [s for s in sensors if to_exclude not in s]

    if hemisphere != "both":
        if include_central == False:
            if hemisphere == "left":
                sensors = [s for s in sensors if "1" in s or "3" in s or "5" in s or "7" in s or "9" in s]
            if hemisphere == "right":
                sensors = [s for s in sensors if "2" in s or "4" in s or "6" in s or "8" in s or "10" in s]
        else:
            if hemisphere == "left":
                sensors = [s for s in sensors if "1" in s or "3" in s or "5" in s or "7" in s or "9" in s or "z" in s]
            if hemisphere == "right":
                sensors = [s for s in sensors if "2" in s or "4" in s or "6" in s or "8" in s or "10" in s or "z" in s]


    return(sensors)