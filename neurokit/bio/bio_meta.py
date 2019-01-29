# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from .bio_ecg import *
from .bio_rsp import *
from .bio_eda import *
from .bio_emg import *


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def bio_process(ecg=None, rsp=None, eda=None, emg=None, add=None, sampling_rate=1000, age=None, sex=None, position=None, ecg_filter_type="FIR", ecg_filter_band="bandpass", ecg_filter_frequency=[3, 45], ecg_segmenter="hamilton", ecg_quality_model="default", ecg_hrv_features=["time", "frequency"], eda_alpha=8e-4, eda_gamma=1e-2, scr_method="makowski", scr_treshold=0.1, emg_names=None, emg_envelope_freqs=[10, 400], emg_envelope_lfreq=4, emg_activation_treshold="default", emg_activation_n_above=0.25, emg_activation_n_below=1):
    """
    Automated processing of bio signals. Wrapper for other bio processing functions.

    Parameters
    ----------
    ecg : list or array
        ECG signal array.
    rsp : list or array
        Respiratory signal array.
    eda :  list or array
        EDA signal array.
    emg :  list, array or DataFrame
        EMG signal array. Can include multiple channels.
    add : pandas.DataFrame
        Dataframe or channels to add by concatenation to the processed dataframe.
    sampling_rate : int
        Sampling rate (samples/second).
    age : float
        Subject's age.
    sex : str
        Subject's gender ("m" or "f").
    position : str
        Recording position. To compare with data from Voss et al. (2015), use "supine".
    ecg_filter_type : str
        Can be Finite Impulse Response filter ("FIR"), Butterworth filter ("butter"), Chebyshev filters ("cheby1" and "cheby2"), Elliptic filter ("ellip") or Bessel filter ("bessel").
    ecg_filter_band : str
        Band type, can be Low-pass filter ("lowpass"), High-pass filter ("highpass"), Band-pass filter ("bandpass"), Band-stop filter ("bandstop").
    ecg_filter_frequency : int or list
        Cutoff frequencies, format depends on type of band: "lowpass" or "bandpass": single frequency (int), "bandpass" or "bandstop": pair of frequencies (list).
    ecg_quality_model : str
        Path to model used to check signal quality. "default" uses the builtin model. None to skip this function.
    ecg_hrv_features : list
        What HRV indices to compute. Any or all of 'time', 'frequency' or 'nonlinear'. None to skip this function.
    ecg_segmenter : str
        The cardiac phase segmenter. Can be "hamilton", "gamboa", "engzee", "christov" or "ssf". See :func:`neurokit.ecg_preprocess()` for details.
    eda_alpha : float
        cvxEDA penalization for the sparse SMNA driver.
    eda_gamma : float
        cvxEDA penalization for the tonic spline coefficients.
    scr_method : str
        SCR extraction algorithm. "makowski" (default), "kim" (biosPPy's default; See Kim et al., 2004) or "gamboa" (Gamboa, 2004).
    scr_treshold : float
        SCR minimum treshold (in terms of signal standart deviation).
    emg_names : list
        List of EMG channel names.


    Returns
    ----------
    processed_bio : dict
        Dict containing processed bio features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, and the RSP filtered signal (if respiration provided), respiratory sinus arrhythmia (RSA) features, the EDA raw signal, the filtered signal, the phasic component (if cvxEDA is True), the SCR onsets, peak indexes and amplitudes, the EMG raw signal, the filtered signal and pulse onsets.



    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> bio_features = nk.bio_process(ecg=ecg_signal, rsp=ecg_signal, eda=eda_signal)

    Notes
    ----------
    *Details*

    - **ECG Features**: See :func:`neurokit.ecg_process()`.
    - **EDA Features**: See :func:`neurokit.eda_process()`.
    - **RSP Features**: See :func:`neurokit.rsp_process()`.
    - **EMG Features**: See :func:`neurokit.emg_process()`.


    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - pandas

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy
    - hrv: https://github.com/rhenanbartels/hrv
    - cvxEDA: https://github.com/lciti/cvxEDA

    References
    -----------
    - Heart rate variability. (1996). Standards of measurement, physiological interpretation, and clinical use. Task Force of the European Society of Cardiology and the North American Society of Pacing and Electrophysiology. Eur Heart J, 17, 354-381.
    - Voss, A., Schroeder, R., Heitmann, A., Peters, A., & Perz, S. (2015). Short-term heart rate variability—influence of gender and age in healthy subjects. PloS one, 10(3), e0118308.
    - Greco, A., Valenza, G., & Scilingo, E. P. (2016). Evaluation of CDA and CvxEDA Models. In Advances in Electrodermal Activity Processing with Applications for Mental Health (pp. 35-43). Springer International Publishing.
    - Greco, A., Valenza, G., Lanata, A., Scilingo, E. P., & Citi, L. (2016). cvxEDA: A convex optimization approach to electrodermal activity processing. IEEE Transactions on Biomedical Engineering, 63(4), 797-804.
    - Zohar, A. H., Cloninger, C. R., & McCraty, R. (2013). Personality and heart rate variability: exploring pathways from personality to cardiac coherence and health. Open Journal of Social Sciences, 1(06), 32.
    - Smith, A. L., Owen, H., & Reynolds, K. J. (2013). Heart rate variability indices for very short-term (30 beat) analysis. Part 2: validation. Journal of clinical monitoring and computing, 27(5), 577-585.
    - Azevedo, R. T., Garfinkel, S. N., Critchley, H. D., & Tsakiris, M. (2017). Cardiac afferent activity modulates the expression of racial stereotypes. Nature communications, 8.
    - Edwards, L., Ring, C., McIntyre, D., & Carroll, D. (2001). Modulation of the human nociceptive flexion reflex across the cardiac cycle. Psychophysiology, 38(4), 712-718.
    - Gray, M. A., Rylander, K., Harrison, N. A., Wallin, B. G., & Critchley, H. D. (2009). Following one's heart: cardiac rhythms gate central initiation of sympathetic reflexes. Journal of Neuroscience, 29(6), 1817-1825.
    - Kim, K. H., Bang, S. W., & Kim, S. R. (2004). Emotion recognition system using short-term monitoring of physiological signals. Medical and biological engineering and computing, 42(3), 419-427.
    - Gamboa, H. (2008). Multi-Modal Behavioral Biometrics Based on HCI and Electrophysiology (Doctoral dissertation, PhD thesis, Universidade Técnica de Lisboa, Instituto Superior Técnico).
    """
    processed_bio = {}
    bio_df = pd.DataFrame({})

    # ECG & RSP
    if ecg is not None:
        ecg = ecg_process(ecg=ecg, rsp=rsp, sampling_rate=sampling_rate, filter_type=ecg_filter_type, filter_band=ecg_filter_band, filter_frequency=ecg_filter_frequency, segmenter=ecg_segmenter, quality_model=ecg_quality_model, hrv_features=ecg_hrv_features, age=age, sex=sex, position=position)
        processed_bio["ECG"] = ecg["ECG"]
        if rsp is not None:
            processed_bio["RSP"] = ecg["RSP"]
        bio_df = pd.concat([bio_df, ecg["df"]], axis=1)

    if rsp is not None and ecg is None:
        rsp = rsp_process(rsp=rsp, sampling_rate=sampling_rate)
        processed_bio["RSP"] = rsp["RSP"]
        bio_df = pd.concat([bio_df, rsp["df"]], axis=1)


    # EDA
    if eda is not None:
        eda = eda_process(eda=eda, sampling_rate=sampling_rate, alpha=eda_alpha, gamma=eda_gamma, scr_method=scr_method, scr_treshold=scr_treshold)
        processed_bio["EDA"] = eda["EDA"]
        bio_df = pd.concat([bio_df, eda["df"]], axis=1)

    # EMG
    if emg is not None:
        emg = emg_process(emg=emg, sampling_rate=sampling_rate, emg_names=emg_names, envelope_freqs=emg_envelope_freqs, envelope_lfreq=emg_envelope_lfreq, activation_treshold=emg_activation_treshold, activation_n_above=emg_activation_n_above, activation_n_below=emg_activation_n_below)
        bio_df = pd.concat([bio_df, emg.pop("df")], axis=1)
        for i in emg:
            processed_bio[i] = emg[i]


    if add is not None:
        add = add.reset_index(drop=True)
        bio_df = pd.concat([bio_df, add], axis=1)
    processed_bio["df"] = bio_df

    return(processed_bio)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def bio_EventRelated(epoch, event_length, window_post_ecg=0, window_post_rsp=4, window_post_eda=4, ecg_features=["Heart_Rate", "Cardiac_Phase", "RR_Interval", "RSA", "HRV"]):
    """
    Extract event-related bio (EDA, ECG and RSP) changes.

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contains in the epochs dict returned by :function:`neurokit.create_epochs()` on dataframe returned by :function:`neurokit.bio_process()`.
    event_length : int
        In seconds.
    sampling_rate : int
        Sampling rate (samples/second).
    window_post_ecg : float
        Post-stimulus window size (in seconds) for ECG.
    window_post_rsp : float
        Post-stimulus window size (in seconds) for RSP.
    window_post_eda : float
        Post-stimulus window size (in seconds) for EDA.
    ecg_features : list
        List of ECG features to compute, can contain "Heart_Rate", "Cardiac_Phase", "RR_Interval", "RSA", "HRV".

    Returns
    ----------
    RSP_Response : dict
        Event-locked bio response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(ecg=data["ECG"], rsp=data["RSP"], eda=data["EDA"], sampling_rate=1000, add=data["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=7, onset=-0.5)
    >>> for epoch in epochs:
    >>>     bio_response = nk.bio_EventRelated(epoch, event_length=4, window_post=3)

    Notes
    ----------
    *Details*

    - **ECG Features**

        - ***_Baseline**: Signal at onset.
        - ***_Min**: Mininmum of signal after stimulus onset.
        - ***_MinDiff**: Signal mininum - baseline.
        - ***_MinTime**: Time of signal minimum.
        - ***_Max**: Maximum of signal after stimulus onset.
        - ***_MaxDiff**: Signal maximum - baseline.
        - ***_MaxTime**: Time of signal maximum.
        - ***_Mean**: Mean signal after stimulus onset.
        - ***_MeanDiff**: Mean signal - baseline.
        - **ECG_Phase_Systole**: Cardiac phase on stimulus onset (1 = systole, 0 = diastole).
        - **ECG_Phase_Systole_Completion**: Percentage of cardiac phase completion on simulus onset.
        - **ECG_HRV_***: Time-domain HRV features. See :func:`neurokit.ecg_hrv()`.

    - **Respiration Features**

        - **RSP_Rate_Baseline**: mean RSP Rate before stimulus onset.
        - **RSP_Rate_Min**: Min RSP Rate after stimulus onset.
        - **RSP_Rate_MinDiff**: RSP Rate mininum - baseline.
        - **RSP_Rate_MinTime**: Time of minimum.
        - **RSP_Rate_Max**: Max RSP Rate after stimulus onset.
        - **RSP_Rate_MaxDiff**: Max RSP Rate - baseline.
        - **RSP_Rate_MaxTime**: Time of maximum.
        - **RSP_Rate_Mean**: Mean RSP Rate after stimulus onset.
        - **RSP_Rate_MeanDiff**: Mean RSP Rate - baseline.
        - **RSP_Min**: Value in standart deviation (normalized by baseline) of the lowest point.
        - **RSP_MinTime**: Time of RSP Min.
        - **RSP_Max**: Value in standart deviation (normalized by baseline) of the highest point.
        - **RSP_MaxTime**: Time of RSP Max.
        - **RSP_Inspiration**: Respiration phase on stimulus onset (1 = inspiration, 0 = expiration).
        - **RSP_Inspiration_Completion**: Percentage of respiration phase on stimulus onset.

    - **EDA Features**

        - **EDA_Peak**: Max of EDA (in a window starting 1s after the stim onset) minus baseline.
        - **SCR_Amplitude**: Peak of SCR. If no SCR, returns NA.
        - **SCR_Magnitude**: Peak of SCR. If no SCR, returns 0.
        - **SCR_Amplitude_Log**: log of 1+amplitude.
        - **SCR_Magnitude_Log**: log of 1+magnitude.
        - **SCR_PeakTime**: Time of peak.
        - **SCR_Latency**: Time between stim onset and SCR onset.
        - **SCR_RiseTime**: Time between SCR onset and peak.
        - **SCR_Strength**: *Experimental*: peak divided by latency. Angle of the line between peak and onset.
        - **SCR_RecoveryTime**: Time between peak and recovery point (half of the amplitude).


    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    References
    -----------
    - Gomez, P., Stahel, W. A., & Danuser, B. (2004). Respiratory responses during affective picture viewing. Biological Psychology, 67(3), 359-373.
    - Schneider, R., Schmidt, S., Binder, M., Schäfer, F., & Walach, H. (2003). Respiration-related artifacts in EDA recordings: introducing a standardized method to overcome multiple interpretations. Psychological reports, 93(3), 907-920.
    """
    bio_response = {}

    ECG_Response = ecg_EventRelated(epoch, event_length, window_post=window_post_ecg, features=ecg_features)
    bio_response.update(ECG_Response)

    RSP_Response = rsp_EventRelated(epoch, event_length, window_post=window_post_rsp)
    bio_response.update(RSP_Response)

    EDA_Response = eda_EventRelated(epoch, event_length, window_post=window_post_eda)
    bio_response.update(EDA_Response)

    return(bio_response)