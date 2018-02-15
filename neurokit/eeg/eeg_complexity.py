# -*- coding: utf-8 -*-
from ..miscellaneous import Time
from ..statistics import find_following_duplicates

from ..signal import complexity

from .eeg_data import eeg_to_df

import pandas as pd


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eeg_complexity(eeg, sampling_rate, times=None, index=None, include="all", exclude=None, hemisphere="both", central=True, verbose=True, shannon=True, sampen=True, multiscale=True, spectral=True, svd=True, correlation=True, higushi=True, petrosian=True, fisher=True, hurst=True, dfa=True, lyap_r=False, lyap_e=False, names="Complexity"):
    """
    Compute complexity indices of epochs or raw object.

    DOCS INCOMPLETE :(
    """


    data = eeg_to_df(eeg, index=index, include=include, exclude=exclude, hemisphere=hemisphere, central=central)

    # if data was Raw, make as if it was an Epoch so the following routine is only written once
    if isinstance(data, dict) is False:
        data = {0: data}

    # Create time windows
    if isinstance(times, tuple):
        times = list(times)
    if isinstance(times, list):
        if isinstance(times[0], list) is False:
            times = [times]
    else:
        times = [[0, None]]


    # Deal with names
    if isinstance(names, str):
        prefix = [names] * len(times)
        if len(times) > 1:
            for time_index, time_window in enumerate(times):
                prefix[time_index] = prefix[time_index] + "_%.2f_%.2f" %(time_window[0], time_window[1])
    else:
        prefix = names


    # Iterate
    complexity_all = pd.DataFrame()
    for time_index, time_window in enumerate(times):
        if len(times) > 1 and verbose is True:
            print("Computing complexity features... window " + str(time_window) + "/" + str(len(times)))

        complexity_features = {}
        # Compute complexity for each channel for each epoch
        index = 0
        for epoch_index, epoch in data.items():
            if len(times) == 1 and verbose is True:
                print("Computing complexity features... " + str(round(index/len(data.items())*100, 2)) + "%")
            index +=1

            df = epoch[time_window[0]:time_window[1]].copy()

            complexity_features[epoch_index] = {}
            for channel in df:
                signal = df[channel].values

                features = complexity(signal, sampling_rate=sampling_rate, shannon=shannon, sampen=sampen, multiscale=multiscale, spectral=spectral, svd=svd, correlation=correlation, higushi=higushi, petrosian=petrosian, fisher=fisher, hurst=hurst, dfa=dfa, lyap_r=lyap_r, lyap_e=lyap_e)

                for key, feature in features.items():
                    if key in complexity_features[epoch_index].keys():
                        complexity_features[epoch_index][key].append(feature)
                    else:
                        complexity_features[epoch_index][key] = [feature]

        for epoch_index, epoch in complexity_features.items():
            for feature in epoch:
                complexity_features[epoch_index][feature] = pd.Series(complexity_features[epoch_index][feature]).mean()

        # Convert to dataframe
        complexity_features = pd.DataFrame.from_dict(complexity_features, orient="index")
        complexity_features.columns = [prefix[time_index] + "_" + s for s in complexity_features.columns]


        complexity_all = pd.concat([complexity_all, complexity_features], axis=1)
    return(complexity_all)









