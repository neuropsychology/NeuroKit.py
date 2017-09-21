"""
ERP analysis EEG submodule.
"""
from .eeg_data import eeg_select_electrodes
from .eeg_data import eeg_to_df
from .eeg_data import eeg_to_all_evokeds


import numpy as np
import pandas as pd
import mne




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_erp(eeg, times=None, index=None, include="all", exclude=None, hemisphere="both", central=True, verbose=True, names="ERP", method="mean"):
    """
    DOCS INCOMPLETE :(
    """
    erp = {}

    data = eeg_to_df(eeg, index=index, include=include, exclude=exclude, hemisphere=hemisphere, central=central)

    for epoch_index, epoch in data.items():
        # Segment according to window
        if isinstance(times, list):
            if isinstance(times[0], list):
                values = {}
                for window_index, window in enumerate(times):
                    df = epoch[window[0]:window[1]]
                    value = df.mean().mean()
                    values[window_index] = value
                erp[epoch_index] = values
            else:
                df = epoch[times[0]:times[1]]
                value = df.mean().mean()
                erp[epoch_index] = [value]
        elif isinstance(times, tuple):
            values = {}
            for window_index, window in enumerate(times):
                df = epoch[window[0]:window[1]]
                if method == "max":
                    value = df.mean().max()
                elif method == "min":
                    value = df.mean().min()
                else:
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
def plot_eeg_erp(all_epochs, conditions=None, times=None, include="all", exclude=None, hemisphere="both", central=True, name=None, colors=None, gfp=False, ci=0.95, ci_alpha=0.333, invert_y=False, linewidth=1, linestyle="-", filter_hfreq=None):
    """
    DOCS INCOMPLETE :(
    """
    # Preserve original
    all_epochs_current = all_epochs.copy()

    # Filter using Savitzky-Golay polynomial method
    if (filter_hfreq is not None) and (isinstance(filter_hfreq, int)):
        for participant, epochs in all_epochs_current.items():
            all_epochs_current[participant] = epochs.savgol_filter(filter_hfreq, copy=True)

    # Crop
    if isinstance(times, list) and len(times) == 2:
        for participant, epochs in all_epochs_current.items():
            all_epochs_current[participant] = epochs.copy().crop(times[0], times[1])


    # Transform to evokeds
    all_evokeds = eeg_to_all_evokeds(all_epochs_current, conditions=conditions)

    data = {}
    for participant, epochs in all_evokeds.items():
        for condition, epoch in epochs.items():
            data[condition] = []
    for participant, epochs in all_evokeds.items():
        for condition, epoch in epochs.items():
            data[condition].append(epoch)


    conditions = list(data.keys())

    # Line styles
    if isinstance(linestyle, str):
        linestyle = [linestyle] * len(conditions)
    elif isinstance(linestyle, list) and len(linestyle) >= len(conditions):
        pass
    elif isinstance(linestyle, dict) and len(linestyle.keys()) >= len(conditions):
        linestyle = [linestyle[cond] for cond in conditions]
    else:
        print("NeuroKit Warning: plot_eeg_erp(): linestyle must be either a str, a list or a dict.")


    # Colors
    if isinstance(colors, str):
        colors = {condition: colors for condition in conditions}
    elif isinstance(colors, list) and len(colors) >= len(conditions):
        colors=  {condition: colors[index] for index, condition in enumerate(conditions)}
    elif isinstance(colors, dict) and len(colors.keys()) >= len(conditions):
        pass
    elif colors is None:
        pass
    else:
        print("NeuroKit Warning: plot_eeg_erp(): colors must be either a str, a list, a dict or None.")


    # Modify styles
    styles = {}
    for index, condition in enumerate(conditions):
        styles[condition] = {"linewidth": linewidth, "linestyle": linestyle[index]}


    # Select electrodes
    picks = mne.pick_types(epoch.info, eeg=True, selection=eeg_select_electrodes(epoch, include=include, exclude=exclude, hemisphere=hemisphere, central=central))

    # Plot
    try:
        plot = mne.viz.plot_compare_evokeds(data, picks=picks, colors=colors, styles=styles, title=name, gfp=gfp, ci=ci, invert_y=invert_y, ci_alpha=ci_alpha)
    except TypeError:
        print("NeuroKit Warning: plot_eeg_erp(): You're using a version of mne that does not support ci_alpha or ci_method parameters. Leaving defaults.")
        plot = mne.viz.plot_compare_evokeds(data, picks=picks, colors=colors, styles=styles, title=name, gfp=gfp, ci=ci, invert_y=invert_y)

    return(plot)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def plot_eeg_erp_topo(all_epochs, colors=None):
    """
    Plot butterfly plot.

    DOCS INCOMPLETE :(
    """
    all_evokeds = eeg_to_all_evokeds(all_epochs)

    data = {}
    for participant, epochs in all_evokeds.items():
        for cond, epoch in epochs.items():
            data[cond] = []
    for participant, epochs in all_evokeds.items():
        for cond, epoch in epochs.items():
            data[cond].append(epoch)

    if colors is not None:
        color_list = []
    else:
        color_list = None

    evokeds = []
    for condition, evoked in data.items():
        grand_average = mne.grand_average(evoked)
        grand_average.comment = condition
        evokeds += [grand_average]
        if colors is not None:
            color_list.append(colors[condition])

    plot = mne.viz.plot_evoked_topo(evokeds, background_color="w", color=color_list)
    return(plot)




