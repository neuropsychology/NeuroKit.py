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
def process_bio(ecg=None, rsp=None, eda=None, sampling_rate=1000, resampling_method="bfill", cvxEDA=True):
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

    Returns
    ----------
    bio_features = dict
        Dict containing bio extracted features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, and the RSP filtered signal (if respiration provided), the EDA raw signal, the filtered signal, the phasic compnent (if cvxEDA is True), the SCR onsets, peak indexes and amplitudes.



    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> bio_features = nk.process_bio(ecg=ecg_signal, rsp=ecg_signal, eda=eda_signal)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - None
    """
    bio_features = {}

    # ECG & RSP
    if ecg is not None:
        bio_features.update(process_ecg(ecg=ecg, rsp=rsp, sampling_rate=sampling_rate, resampling_method=resampling_method))

    if eda is not None:
        bio_features.update(process_eda(eda=eda, sampling_rate=sampling_rate, cvxEDA=cvxEDA))

    return(bio_features)



