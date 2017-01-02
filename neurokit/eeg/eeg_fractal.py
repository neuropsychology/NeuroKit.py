# -*- coding: utf-8 -*-
from ..miscellaneous import Time
from ..miscellaneous import find_following_duplicates

import numpy as np
import pandas as pd
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








