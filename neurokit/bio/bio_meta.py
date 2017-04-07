# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from .bio_ecg import *
from .bio_eda import *

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def bio_process(ecg=None, rsp=None, eda=None, sampling_rate=1000, resampling_method="bfill", use_cvxEDA=True, add=None):
    """
    Automated processing of bio signal.

    Parameters
    ----------
    ecg =  array
        ECG signal array.
    rsp =  array
        Respiratory signal array.
    eda =  array
        EDA signal array.
    sampling_rate = int
        Sampling rate (samples/second).
    resampling_method = str
        "mean", "pad" or "bfill", the resampling method used for ECG and RSP heart rate.
    cvxEDA = bool
        Use convex optimization (CVXEDA) described in "cvxEDA: a Convex Optimization Approach to Electrodermal Activity Processing" (Greco et al., 2015).
    add = pandas.DataFrame
        Dataframe or channels to add by concatenation to the processed dataframe.

    Returns
    ----------
    processed_bio = dict
        Dict containing processed bio features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, and the RSP filtered signal (if respiration provided), the EDA raw signal, the filtered signal, the phasic compnent (if cvxEDA is True), the SCR onsets, peak indexes and amplitudes.



    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> bio_features = nk.bio_process(ecg=ecg_signal, rsp=ecg_signal, eda=eda_signal)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - None
    """
    processed_bio = {}
    bio_df = pd.DataFrame({})

    # ECG & RSP
    if ecg is not None:
        ecg = ecg_process(ecg=ecg, rsp=rsp, sampling_rate=sampling_rate, resampling_method=resampling_method)
        processed_bio["ECG_Features"] = ecg["ECG_Features"]
        bio_df = pd.concat([bio_df, ecg["ECG"]], axis=1)

    # EDA
    if eda is not None:
        eda = eda_process(eda=eda, sampling_rate=sampling_rate, use_cvxEDA=use_cvxEDA)
        processed_bio["EDA_Features"] = eda["EDA_Features"]
        bio_df = pd.concat([bio_df, eda["EDA"]], axis=1)

    if add is not None:
        bio_df = pd.concat([bio_df, add], axis=1)
    processed_bio["Bio"] = bio_df


    return(processed_bio)



