"""
Preprocessing EEG submodule.
"""
from ..signal import select_events
from ..miscellaneous import read_data

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
def eeg_filter(raw, lowpass=1, highpass=40, notch=True, method="iir"):
    """
    Apply filter.
    """
    if notch == True:
        raw.notch_filter(np.arange(50, 201, 50),
                         phase='zero',
                         method=method
                         )
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
def eeg_eog_ica(raw, method='fastica', n_components=20, random_state=23, plot_sources=False, plot=False):
    """
    Apply ICA.
    """
    ica = mne.preprocessing.ICA(n_components=n_components,
                                method=method,  # for comparison with EEGLAB try "extended-infomax" here
                                random_state=random_state  # random seed
                                )

    picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=True, ecg=False, stim=False, exclude='bads')
    ica.fit(raw, picks=picks, decim=3)

    # create one EOG trials
    eog_epochs = mne.preprocessing.create_eog_epochs(raw,
                                                     picks=picks)
    # find via correlation the ICA components
    eog_inds, scores = ica.find_bads_eog(eog_epochs)

    if plot_sources==True:
        ica.plot_sources(raw)

    ica.exclude.extend(eog_inds)
    raw = ica.apply(raw)

    if plot is True:
        ica.plot_components()[0]
    return(raw)







# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_eog_ssp(raw, plot=False):
    """
    Apply SSP.
    """
    projs, eog_events = mne.preprocessing.compute_proj_eog(raw, average=True, n_grad=0, n_mag=0, n_eeg=2)
    eog_projs = projs[-2:]
    if plot is True:
        mne.viz.plot_projs_topomap(eog_projs, layout=mne.channels.find_layout(raw.info))
    raw.info['projs'] += eog_projs
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
def eeg_select_electrodes(include="all", exclude=None, hemisphere="both", include_central=True):
    """
    Select electrodes by region.
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