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
def eeg_complexity(eeg, sampling_rate=1000, index=None, include="all", exclude=None, hemisphere="both", central=True, verbose=True, shannon=True, sampen=True, multiscale=True, spectral=True, svd=True, correlation=True, higushi=True, petrosian=True, fisher=True, hurst=True, dfa=True, lyap_r=False, lyap_e=False, name="Complexity"):
    """
    Compute complexity indices of epochs or raw object.
    """
    complexity_features = {}

    data = eeg_to_df(eeg, index=index, include=include, exclude=exclude, hemisphere=hemisphere, central=central)

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
    complexity_features.columns = [name + "_" + s for s in complexity_features.columns]

    return(complexity_features)









