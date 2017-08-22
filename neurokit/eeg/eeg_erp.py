"""
ERP analysis EEG submodule.
"""
from .eeg_data import eeg_select_electrodes
from .eeg_data import eeg_to_df

import numpy as np
import pandas as pd
import mne
import matplotlib



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_erp(eeg, windows=None, index=None, include="all", exclude=None, hemisphere="both", central=True, verbose=True, names="ERP"):
    """
    """
    erp = {}

    data = eeg_to_df(eeg, index=index, include=include, exclude=exclude, hemisphere=hemisphere, central=central)

    for epoch_index, epoch in data.items():
        # Segment according to window
        if isinstance(windows, list):
            df = epoch[windows[0]:windows[1]]
            value = df.mean().mean()
            erp[epoch_index] = [value]
        elif isinstance(windows, tuple):
            values = {}
            for window_index, window in enumerate(windows):
                df = epoch[window[0]:window[1]]
                value = df.mean().mean()
                values[window_index] = value
            erp[epoch_index] = values
        else:
            df = epoch[0:]
            value = df.mean().mean()
            erp[epoch_index] = [value]

    # Convert to dataframe
    erp = pd.DataFrame.from_dict(erp, orient="index")
    if isinstance(names, str):
        names = [names]
    if len(names) == len(erp.columns):
        erp.columns = names

    return(erp)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def plot_eeg_erp(eeg, colors=None, include="all", exclude=None, hemisphere="both", central=True, title=None):
    """
    """
    all_evokeds = {}
    for participant, epochs in eeg.items():
        for cond, epoch in epochs.items():
            all_evokeds[cond] = []
    for participant, epochs in eeg.items():
        for cond, epoch in epochs.items():
            all_evokeds[cond].append(epoch)


    picks = mne.pick_types(epoch.info, eeg=True, selection=eeg_select_electrodes(epoch, include=include, exclude=exclude, hemisphere=hemisphere, central=central))

    plot = mne.viz.plot_compare_evokeds(all_evokeds, picks=picks, colors=colors, title=title)
    return(plot)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def plot_eeg_erp_topo(eeg, colors=None):
    """
    Plot butterfly plot.
    """
    all_evokeds = {}
    for participant, epochs in eeg.items():
        for cond, epoch in epochs.items():
            all_evokeds[cond] = []
    for participant, epochs in eeg.items():
        for cond, epoch in epochs.items():
            all_evokeds[cond].append(epoch)

    if colors is not None:
        color_list = []
    evokeds = []
    for condition, evoked in all_evokeds.items():
        grand_average = mne.grand_average(evoked)
        grand_average.comment = condition
        evokeds += [grand_average]
        if colors is not None:
            color_list.append(colors[condition])

    plot = mne.viz.plot_evoked_topo(evokeds, background_color="w", color=color_list)
    return(plot)




