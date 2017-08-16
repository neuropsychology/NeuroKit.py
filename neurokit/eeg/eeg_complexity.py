# -*- coding: utf-8 -*-
from ..miscellaneous import Time
from ..miscellaneous import find_following_duplicates

from ..signal import complexity

from .eeg_data import eeg_to_df

import mne
import numpy as np
import pandas as pd
import nolds
import re


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_complexity(eeg_data, sampling_rate=1000, index=None, include="all", exclude=None, hemisphere="both", include_central=True, verbose=True, shannon=True, sampen=True, multiscale=True, spectral=True, svd=True, correlation=True, higushi=True, petrosian=True, fisher=True, hurst=True, dfa=True, lyap_r=False, lyap_e=False):
    """
    Compute complexity indices of epochs or raw object.
    """
    complexity = {}

    data = eeg_to_df(eeg_data, index=index, include=include, exclude=exclude, hemisphere=hemisphere, include_central=include_central)

    # if data was Raw, make as if it was an Epoch so the following routine is only written once
    if isinstance(data, dict) is False:
        data = {0: data}


    # Compute complexity for each channel for each epoch
    index = 0
    for epoch_index, epoch in data.items():
        if verbose is True:
            print("Computing complexity features... " + str(round(index/len(data.items())*100, 2)) + "%")
        index +=1

        df = epoch[0:]

        complexity[epoch_index] = {}
        for channel in df:
            signal = df[channel].values

            features = complexity(signal, sampling_rate=sampling_rate, shannon=shannon, sampen=sampen, multiscale=multiscale, spectral=spectral, svd=svd, correlation=correlation, higushi=higushi, petrosian=petrosian, fisher=fisher, hurst=hurst, dfa=dfa, lyap_r=lyap_r, lyap_e=lyap_e)

            for key, feature in features.items():
                if key in complexity[epoch_index].keys():
                    complexity[epoch_index][key].append(feature)
                else:
                    complexity[epoch_index][key] = [feature]

    for epoch_index, epoch in complexity.items():
        for feature in epoch:
            complexity[epoch_index][feature] = pd.Series(complexity[epoch_index][feature]).mean()

    if len(data) == 1:
        data = data[0]

    return(complexity)




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

    list_events = list_events[np.where(find_following_duplicates(list_events))]
    list_events = [re.sub('_\d+', '', i) for i in list_events]
    df["Epoch"] = list_events
    return(df)








