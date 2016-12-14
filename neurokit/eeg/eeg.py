# -*- coding: utf-8 -*-
from ..miscellaneous import Time
from ..miscellaneous import remove_following_duplicates

import numpy as np
import pandas as pd
import mne
import nolds  # Fractal
import re




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_plot_all(raw, events, event_id, eog_reject=600e-6, save=True, name="all", topo=False, path=""):
    """
    """
    reject = {
#        "eeg": 4000e-13,
        "eog": eog_reject  # Adjust with caution
        }
    # picks
    picks = mne.pick_types(raw.info,
                       meg=False,
                       eeg=True,
                       eog=True,
                       stim=False,
                       exclude='bads',
#                       selection=O_cluster + PO_cluster
                       )

    # epochs
    epochs = mne.Epochs(raw,
                        events=events,
                        event_id=event_id,
                        tmin=-0.2,
                        tmax=1,
                        picks=picks,
                        add_eeg_ref=True,
                        reject_by_annotation=True,
                        reject=reject,  # Adjust values carefully
                        proj=True,  # With SSP projections
                        detrend=1,  # "None", 1: Linear detrend, 0 DC detrend,
                        baseline=(None, 0)  #
                        )

    # Drop bads
    epochs.drop_bad()


    # Plot
    if topo is False:
        fig = mne.combine_evoked([epochs.average()]).plot_joint()
        if save is True:
            fig.savefig(path + str(name) +  '.png', format='png', dpi=1000)


    if topo is True:
        fig = mne.viz.plot_evoked_topo([epochs.average()],
        #                                  fig_background="black",
                                          fig_facecolor="black",
        #                                  conditions = ['Negative', 'Neutral'],
    #                                      scalings=dict(eeg=1e1),
                                          layout=mne.channels.find_layout(raw.info),
                                          font_color="black",
                                          axis_facecolor="black",
    #                                      proj = "interactive",
                                          color='red'
        #                                  layout_scale = 2
                                          )
        if save is True:
            fig.savefig(path + str(name) +  '.png', format='png', dpi=1000)







# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_fractal_dim(epochs, entropy=True, hurst=True, dfa=False, lyap_r=False, lyap_e=False):
    """
    """
    clock = Time()

    df = epochs.to_data_frame(index=["epoch", "time", "condition"])

    # Separate indexes
    index = df.index.tolist()
    epochs = []
    times = []
    events = []
    for i in index:
        epochs.append(i[0])
        times.append(i[1])
        events.append(i[2])



    data = {}
    if entropy == True:
        data["Entropy"] = {}
    if hurst == True:
        data["Hurst"] = {}
    if dfa == True:
        data["DFA"] = {}
    if lyap_r == True:
        data["Lyapunov_R"] = {}
    if lyap_e == True:
        data["Lyapunov_E"] = {}


    clock.reset()
    for epoch in set(epochs):
        subset = df.loc[epoch]

        if entropy == True:
            data["Entropy"][epoch] = []
        if hurst == True:
            data["Hurst"][epoch] = []
        if dfa == True:
            data["DFA"][epoch] = []
        if lyap_r == True:
            data["Lyapunov_R"][epoch] = []
        if lyap_e == True:
            data["Lyapunov_E"][epoch] = []



        for channel in subset:
            if entropy == True:
                data["Entropy"][epoch].append(nolds.sampen(subset[channel]))
            if hurst == True:
                data["Hurst"][epoch].append(nolds.hurst_rs(subset[channel]))
            if dfa == True:
                data["DFA"][epoch].append(nolds.dfa(subset[channel]))
            if lyap_r == True:
                data["Lyapunov_R"][epoch].append(nolds.lyap_r(subset[channel]))
            if lyap_e == True:
                data["Lyapunov_E"][epoch].append(nolds.lyap_e(subset[channel]))

        if entropy == True:
            data["Entropy"][epoch] = np.mean(data["Entropy"][epoch])
        if hurst == True:
            data["Hurst"][epoch] = np.mean(data["Hurst"][epoch])
        if dfa == True:
            data["DFA"][epoch] = np.mean(data["DFA"][epoch])
        if lyap_r == True:
            data["Lyapunov_R"][epoch] = np.mean(data["Lyapunov_R"][epoch])
        if lyap_e == True:
            data["Lyapunov_E"][epoch] = np.mean(data["Lyapunov_E"][epoch])


        time = clock.get(reset=False)/1000
        time = time/(epoch+1)
        time = (time * (len(set(epochs))-epoch))/60
        print(str(round((epoch+1)/len(set(epochs))*100,2)) + "% complete, remaining time: " + str(round(time, 2)) + 'min')

    df = pd.DataFrame.from_dict(data)

    list_events = []
    for i in range(len(events)):
        list_events.append(events[i] + "_" + str(epochs[i]))

    list_events = remove_following_duplicates(list_events)
    list_events = [re.sub('_\d+', '', i) for i in list_events]
    df["Epoch"] = list_events
    return(df)








