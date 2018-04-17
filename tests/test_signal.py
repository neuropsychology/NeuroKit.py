import pytest
import doctest
import os
import numpy as np
import pandas as pd
import neurokit as nk
import scipy
import matplotlib




#==============================================================================
# signal
#==============================================================================
def test_interpolate():
    interpolated = nk.interpolate([800, 900, 700, 500], [1000, 2000, 3000, 4000], 1000)
    assert len(interpolated) == 3000

#==============================================================================
# epochs
#==============================================================================
def test_create_epochs():

    df = pd.DataFrame({"Trigger": pd.Series(scipy.signal.square(1 * np.pi * 5 * np.linspace(0, 1, 2000, endpoint=False))),
                   "Signal": pd.Series(np.sin(20 * np.pi * np.linspace(0, 1, 2000, endpoint=False))) * np.random.normal(0,1,2000),
                   "Signal2": pd.Series(np.sin(60 * np.pi * np.linspace(0, 1, 2000, endpoint=False))) * np.random.normal(0,2,2000)})

    events = nk.find_events(df["Trigger"], cut="lower")
    assert len(events) == 2

#    fig = nk.plot_events_in_signal(df, events["onsets"])

    epochs = nk.create_epochs(df, events["onsets"], duration=0.1)
    assert len(epochs) == 2





if __name__ == '__main__':
    pytest.main()
    doctest.testmod()

