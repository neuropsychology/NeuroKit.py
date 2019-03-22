# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import sklearn
import nolds
import mne
import biosppy
import scipy.signal

from .bio_ecg_preprocessing import *
from .bio_rsp import *
from ..signal import *
from ..materials import Path
from ..statistics import *
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_process(ecg, rsp=None, sampling_rate=1000, filter_type="FIR", filter_band="bandpass", filter_frequency=[3, 45], segmenter="hamilton", quality_model="default", hrv_features=["time", "frequency"], age=None, sex=None, position=None):
    """
    Automated processing of ECG and RSP signals.

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal array.
    rsp : list or ndarray
        Respiratory (RSP) signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    filter_type : str
        Can be Finite Impulse Response filter ("FIR"), Butterworth filter ("butter"), Chebyshev filters ("cheby1" and "cheby2"), Elliptic filter ("ellip") or Bessel filter ("bessel").
    filter_band : str
        Band type, can be Low-pass filter ("lowpass"), High-pass filter ("highpass"), Band-pass filter ("bandpass"), Band-stop filter ("bandstop").
    filter_frequency : int or list
        Cutoff frequencies, format depends on type of band: "lowpass" or "bandpass": single frequency (int), "bandpass" or "bandstop": pair of frequencies (list).
    segmenter : str
        The cardiac phase segmenter. Can be "hamilton", "gamboa", "engzee", "christov" or "ssf". See :func:`neurokit.ecg_preprocess()` for details.
    quality_model : str
        Path to model used to check signal quality. "default" uses the builtin model. None to skip this function.
    hrv_features : list
        What HRV indices to compute. Any or all of 'time', 'frequency' or 'nonlinear'. None to skip this function.
    age : float
        Subject's age for adjusted HRV.
    sex : str
        Subject's gender ("m" or "f") for adjusted HRV.
    position : str
        Recording position. To compare with data from Voss et al. (2015), use "supine".

    Returns
    ----------
    processed_ecg : dict
        Dict containing processed ECG features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV features, all the heartbeats, the Heart Rate, the RSP filtered signal (if respiration provided) and the respiratory sinus arrhythmia (RSA).

    Example
    ----------
    >>> import neurokit as nk
    >>> processed_ecg = nk.ecg_process(ecg_signal, resp_signal)

    Notes
    ----------
    *Details*

    - **Cardiac Cycle**: A typical ECG showing a heartbeat consists of a P wave, a QRS complex and a T wave.The P wave represents the wave of depolarization that spreads from the SA-node throughout the atria. The QRS complex reflects the rapid depolarization of the right and left ventricles. Since the ventricles are the largest part of the heart, in terms of mass, the QRS complex usually has a much larger amplitude than the P-wave. The T wave represents the ventricular repolarization of the ventricles. On rare occasions, a U wave can be seen following the T wave. The U wave is believed to be related to the last remnants of ventricular repolarization.
    - **RSA**: Respiratory sinus arrhythmia (RSA) is a naturally occurring variation in heart rate that occurs during the breathing cycle, serving as a measure of parasympathetic nervous system activity. See :func:`neurokit.ecg_rsa()` for details.
    - **HRV**: Heart-Rate Variability (HRV) is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013). It describes the complex variation of beat-to-beat intervals mainly controlled by the autonomic nervous system (ANS) through the interplay of sympathetic and parasympathetic neural activity at the sinus node. In healthy subjects, the dynamic cardiovascular control system is characterized by its ability to adapt to physiologic perturbations and changing conditions maintaining the cardiovascular homeostasis (Voss, 2015). In general, the HRV is influenced by many several factors like chemical, hormonal and neural modulations, circadian changes, exercise, emotions, posture and preload. There are several procedures to perform HRV analysis, usually classified into three categories: time domain methods, frequency domain methods and non-linear methods. See :func:`neurokit.ecg_hrv()` for a description of indices.
    - **Adjusted HRV**: The raw HRV features are normalized :math:`(raw - Mcluster) / sd` according to the participant's age and gender. In data from Voss et al. (2015), HRV analysis was performed on 5-min ECG recordings (lead II and lead V2 simultaneously, 500 Hz sample rate) obtained in supine position after a 5–10 minutes resting phase. The cohort of healthy subjects consisted of 782 women and 1124 men between the ages of 25 and 74 years, clustered into 4 groups: YF (Female, Age = [25-49], n=571), YM (Male, Age = [25-49], n=744), EF (Female, Age = [50-74], n=211) and EM (Male, Age = [50-74], n=571).
    - **Systole/Diastole**: One prominent channel of body and brain communication is that conveyed by baroreceptors, pressure and stretch-sensitive receptors within the heart and surrounding arteries. Within each cardiac cycle, bursts of baroreceptor afferent activity encoding the strength and timing of each heartbeat are carried via the vagus and glossopharyngeal nerve afferents to the nucleus of the solitary tract. This is the principal route that communicates to the brain the dynamic state of the heart, enabling the representation of cardiovascular arousal within viscerosensory brain regions, and influence ascending neuromodulator systems implicated in emotional and motivational behaviour. Because arterial baroreceptors are activated by the arterial pulse pressure wave, their phasic discharge is maximal during and immediately after the cardiac systole, that is, when the blood is ejected from the heart, and minimal during cardiac diastole, that is, between heartbeats (Azevedo, 2017).
    - **ECG Signal Quality**: Using the PTB-Diagnostic dataset available from PhysioNet, we extracted all the ECG signals from the healthy participants, that contained 15 recording leads/subject. We extracted all cardiac cycles, for each lead, and downsampled them from 600 to 200 datapoints. Note that we dropped the 8 first values that were NaNs. Then, we fitted a neural network model on 2/3 of the dataset (that contains 134392 cardiac cycles) to predict the lead. Model evaluation was done on the remaining 1/3. The model show good performances in predicting the correct recording lead (accuracy=0.91, precision=0.91). In this function, this model is fitted on each cardiac cycle of the provided ECG signal. It returns the probable recording lead (the most common predicted lead), the signal quality of each cardiac cycle (the probability of belonging to the probable recording lead) and the overall signal quality (the mean of signal quality). See creation `scripts <https://github.com/neuropsychology/NeuroKit.py/tree/master/utils/ecg_signal_quality_model_creation>`_.

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    - Rhenan Bartels (https://github.com/rhenanbartels)

    *Dependencies*

    - biosppy
    - numpy
    - pandas

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy
    - hrv: https://github.com/rhenanbartels/hrv
    - RHRV: http://rhrv.r-forge.r-project.org/

    References
    ------------
    - Heart rate variability. (1996). Standards of measurement, physiological interpretation, and clinical use. Task Force of the European Society of Cardiology and the North American Society of Pacing and Electrophysiology. Eur Heart J, 17, 354-381.
    - Voss, A., Schroeder, R., Heitmann, A., Peters, A., & Perz, S. (2015). Short-term heart rate variability—influence of gender and age in healthy subjects. PloS one, 10(3), e0118308.
    - Zohar, A. H., Cloninger, C. R., & McCraty, R. (2013). Personality and heart rate variability: exploring pathways from personality to cardiac coherence and health. Open Journal of Social Sciences, 1(06), 32.
    - Smith, A. L., Owen, H., & Reynolds, K. J. (2013). Heart rate variability indices for very short-term (30 beat) analysis. Part 2: validation. Journal of clinical monitoring and computing, 27(5), 577-585.
    - Azevedo, R. T., Garfinkel, S. N., Critchley, H. D., & Tsakiris, M. (2017). Cardiac afferent activity modulates the expression of racial stereotypes. Nature communications, 8.
    - Edwards, L., Ring, C., McIntyre, D., & Carroll, D. (2001). Modulation of the human nociceptive flexion reflex across the cardiac cycle. Psychophysiology, 38(4), 712-718.
    - Gray, M. A., Rylander, K., Harrison, N. A., Wallin, B. G., & Critchley, H. D. (2009). Following one's heart: cardiac rhythms gate central initiation of sympathetic reflexes. Journal of Neuroscience, 29(6), 1817-1825.
    """
    # Preprocessing
    # =============
    processed_ecg = ecg_preprocess(ecg,
                                   sampling_rate=sampling_rate,
                                   filter_type=filter_type,
                                   filter_band=filter_band,
                                   filter_frequency=filter_frequency,
                                   segmenter=segmenter)

    # Signal quality
    # ===============
    if quality_model is not None:
        quality = ecg_signal_quality(cardiac_cycles=processed_ecg["ECG"]["Cardiac_Cycles"], sampling_rate=sampling_rate, rpeaks=processed_ecg["ECG"]["R_Peaks"], quality_model=quality_model)
        processed_ecg["ECG"].update(quality)
        processed_ecg["df"] = pd.concat([processed_ecg["df"], quality["ECG_Signal_Quality"]], axis=1)

    # HRV
    # =============
    if hrv_features is not None:
        hrv = ecg_hrv(rpeaks=processed_ecg["ECG"]["R_Peaks"], sampling_rate=sampling_rate, hrv_features=hrv_features)
        try:
            processed_ecg["df"] = pd.concat([processed_ecg["df"], hrv.pop("df")], axis=1)
        except KeyError:
            pass
        processed_ecg["ECG"]["HRV"] = hrv
        if age is not None and sex is not None and position is not None:
            processed_ecg["ECG"]["HRV_Adjusted"] = ecg_hrv_assessment(hrv, age, sex, position)

    # RSP
    # =============
    if rsp is not None:
        rsp = rsp_process(rsp=rsp, sampling_rate=sampling_rate)
        processed_ecg["RSP"] = rsp["RSP"]
        processed_ecg["df"] = pd.concat([processed_ecg["df"], rsp["df"]], axis=1)

        # RSA
        # =============
        rsa = ecg_rsa(processed_ecg["ECG"]["R_Peaks"], rsp["df"]["RSP_Filtered"], sampling_rate=sampling_rate)
        processed_ecg["ECG"]["RSA"] = rsa
        processed_ecg["df"] = pd.concat([processed_ecg["df"], rsa.pop("df")], axis=1)

    return(processed_ecg)










# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_rsa(rpeaks, rsp, sampling_rate=1000):
    """
    Returns Respiratory Sinus Arrhythmia (RSA) features. Only the Peak-to-trough (P2T) algorithm is currently implemented (see details).

    Parameters
    ----------
    rpeaks : list or ndarray
        List of R peaks indices.
    rsp : list or ndarray
        Filtered RSP signal.
    sampling_rate : int
        Sampling rate (samples/second).


    Returns
    ----------
    rsa : dict
        Contains RSA features.

    Example
    ----------
    >>> import neurokit as nk
    >>> rsa = nk.ecg_rsa(rpeaks, rsp)

    Notes
    ----------
    *Details*

    - **RSA**: Respiratory sinus arrhythmia (RSA) is a naturally occurring variation in heart rate that occurs during the breathing cycle, serving as a measure of parasympathetic nervous system activity. Neurophysiology informs us that the functional output of the myelinated vagus originating from the nucleus ambiguus has a respiratory rhythm. Thus, there would a temporal relation between the respiratory rhythm being expressed in the firing of these efferent pathways and the functional effect on the heart rate rhythm manifested as RSA. Several methods exist to quantify RSA:

        - **P2T**: The peak to trough (P2T) method measures the statistical range in ms of the heart period oscillation associated with synchronous respiration. Operationally, subtracting the shortest heart period during inspiration from the longest heart period during a breath cycle produces an estimate of RSA during each breath. The peak-to-trough method makes no statistical assumption or correction (e.g., adaptive filtering) regarding other sources of variance in the heart period time series that may confound, distort, or interact with the metric such as slower periodicities and baseline trend. Although it has been proposed that the P2T method "acts as a time-domain filter dynamically centered at the exact ongoing respiratory frequency" (Grossman, 1992), the method does not transform the time series in any way, as a filtering process would. Instead the method uses knowledge of the ongoing respiratory cycle to associate segments of the heart period time series with either inhalation or exhalation (Lewis, 2012).

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    - Rhenan Bartels (https://github.com/rhenanbartels)

    *Dependencies*

    - numpy
    - pandas


    References
    ------------
    - Lewis, G. F., Furman, S. A., McCool, M. F., & Porges, S. W. (2012). Statistical strategies to quantify respiratory sinus arrhythmia: Are commonly used metrics equivalent?. Biological psychology, 89(2), 349-364.
    """
    # Preprocessing
    # =================
    rsp_cycles = rsp_find_cycles(rsp)
    rsp_onsets = rsp_cycles["RSP_Cycles_Onsets"]
    rsp_cycle_center = rsp_cycles["RSP_Expiration_Onsets"]
    rsp_cycle_center = np.array(rsp_cycle_center)[rsp_cycle_center > rsp_onsets[0]]
    if len(rsp_cycle_center) - len(rsp_onsets) == 0:
        rsp_cycle_center = rsp_cycle_center[:-1]
    if len(rsp_cycle_center) - len(rsp_onsets) != -1:
        print("NeuroKit Error: ecg_rsp(): Couldn't find clean rsp cycles onsets and centers. Check your RSP signal.")
        return()
    rsa = {}


    # Peak-to-trough algorithm (P2T)
    # ===============================
    # Find all RSP cycles and the Rpeaks within
    cycles_rri = []
    for idx in range(len(rsp_onsets) - 1):
        cycle_init = rsp_onsets[idx]
        cycle_end = rsp_onsets[idx + 1]
        cycles_rri.append(rpeaks[np.logical_and(rpeaks >= cycle_init,
                                                rpeaks < cycle_end)])

    # Iterate over all cycles
    rsa["RSA_P2T_Values"] = []
    for cycle in cycles_rri:
        RRis = np.diff(cycle)/sampling_rate
        if len(RRis) > 1:
            rsa["RSA_P2T_Values"].append(np.max(RRis) - np.min(RRis))
        else:
            rsa["RSA_P2T_Values"].append(np.nan)
    rsa["RSA_P2T_Mean"] = pd.Series(rsa["RSA_P2T_Values"]).mean()
    rsa["RSA_P2T_Mean_log"] = np.log(rsa["RSA_P2T_Mean"])
    rsa["RSA_P2T_Variability"] = pd.Series(rsa["RSA_P2T_Values"]).std()

    # Continuous RSA - Interpolation using a 3rd order spline
    if len(rsp_cycle_center) - len(rsa["RSA_P2T_Values"]) != 0:
        print("NeuroKit Error: ecg_rsp(): Couldn't find clean rsp cycles onsets and centers. Check your RSP signal.")
        return()
    values=pd.Series(rsa["RSA_P2T_Values"])
    NaNs_indices = values.index[values.isnull()]  # get eventual artifacts indices
    values = values.drop(NaNs_indices)  # remove the artifacts
    value_times=(np.array(rsp_cycle_center))
    value_times = np.delete(value_times, NaNs_indices)  # delete also the artifacts from times indices

    rsa_interpolated = interpolate(values=values, value_times=value_times, sampling_rate=sampling_rate)


    # Continuous RSA - Steps
    current_rsa = np.nan

    continuous_rsa = []
    phase_counter = 0
    for i in range(len(rsp)):
        if i == rsp_onsets[phase_counter]:
            current_rsa = rsa["RSA_P2T_Values"][phase_counter]
            if phase_counter < len(rsp_onsets)-2:
                phase_counter += 1
        continuous_rsa.append(current_rsa)

    # Find last phase
    continuous_rsa = np.array(continuous_rsa)
    continuous_rsa[max(rsp_onsets):] = np.nan

    df = pd.DataFrame({"RSP":rsp})
    df["RSA_Values"] = continuous_rsa
    df["RSA"] = rsa_interpolated
    rsa["df"] = df

    # Porges–Bohrer method (RSAP–B)
    # ==============================
    # Need help to implement this method (See Lewis, 2012)

    return(rsa)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_signal_quality(cardiac_cycles, sampling_rate, rpeaks=None, quality_model="default"):
    """
    Attempt to find the recording lead and the overall and individual quality of heartbeats signal. Although used as a routine, this feature is experimental.

    Parameters
    ----------
    cardiac_cycles : pd.DataFrame
        DataFrame containing heartbeats. Computed by :function:`neurokit.ecg_process`.
    sampling_rate : int
        Sampling rate (samples/second).
    rpeaks : None or ndarray
        R-peak location indices. Used for computing an interpolated signal of quality.
    quality_model : str
        Path to model used to check signal quality. "default" uses the builtin model.

    Returns
    ----------
    classification : dict
        Contains classification features.

    Example
    ----------
    >>> import neurokit as nk
    >>> rsa = nk.respiratory_sinus_arrhythmia(rpeaks, rsp_cycles, rsp_signal)

    Notes
    ----------
    *Details*

    - **ECG Signal Quality**: Using the PTB-Diagnostic dataset available from PhysioNet, we extracted all the ECG signals from the healthy participants, that contained 15 recording leads/subject. We extracted all cardiac cycles, for each lead, and downsampled them from 600 to 200 datapoints. Note that we dropped the 8 first values that were NaNs. Then, we fitted a neural network model on 2/3 of the dataset (that contains 134392 cardiac cycles) to predict the lead. Model evaluation was done on the remaining 1/3. The model show good performances in predicting the correct recording lead (accuracy=0.91, precision=0.91). In this function, this model is fitted on each cardiac cycle of the provided ECG signal. It returns the probable recording lead (the most common predicted lead), the signal quality of each cardiac cycle (the probability of belonging to the probable recording lead) and the overall signal quality (the mean of signal quality). See creation `scripts <https://github.com/neuropsychology/NeuroKit.py/tree/master/utils/ecg_signal_quality_model_creation>`_.

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    - pandas
    """
    if len(cardiac_cycles) > 200:
        cardiac_cycles = cardiac_cycles.rolling(20).mean().resample("3L").pad()
    if len(cardiac_cycles) < 200:
        cardiac_cycles = cardiac_cycles.resample("1L").pad()
        cardiac_cycles = cardiac_cycles.rolling(20).mean().resample("3L").pad()

    if len(cardiac_cycles) < 200:
        fill_dict = {}
        for i in cardiac_cycles.columns:
            fill_dict[i] = [np.nan] * (200-len(cardiac_cycles))
        cardiac_cycles = pd.concat([pd.DataFrame(fill_dict), cardiac_cycles], ignore_index=True)

    cardiac_cycles = cardiac_cycles.fillna(method="bfill")
    cardiac_cycles = cardiac_cycles.reset_index(drop=True)[8:200]
    cardiac_cycles = z_score(cardiac_cycles).T
    cardiac_cycles = np.array(cardiac_cycles)

    if quality_model == "default":
        model = sklearn.externals.joblib.load(Path.materials() + 'heartbeat_classification.model')
    else:
        model = sklearn.externals.joblib.load(quality_model)

    # Initialize empty dict
    quality = {}

    # Find dominant class
    lead = model.predict(cardiac_cycles)
    lead = pd.Series(lead).value_counts().index[0]
    quality["Probable_Lead"] = lead

    predict = pd.DataFrame(model.predict_proba(cardiac_cycles))
    predict.columns = model.classes_
    quality["Cardiac_Cycles_Signal_Quality"] = predict[lead].values
    quality["Average_Signal_Quality"] = predict[lead].mean()

    # Interpolate to get a continuous signal
    if rpeaks is not None:
        signal = quality["Cardiac_Cycles_Signal_Quality"]
        signal = interpolate(signal, rpeaks, sampling_rate)  # Interpolation using 3rd order spline
        signal.name = "ECG_Signal_Quality"
        quality["ECG_Signal_Quality"] = signal

    return(quality)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_hrv(rpeaks=None, rri=None, sampling_rate=1000, hrv_features=["time", "frequency", "nonlinear"]):
    """
    Computes the Heart-Rate Variability (HRV). Shamelessly stolen from the `hrv <https://github.com/rhenanbartels/hrv/blob/develop/hrv>`_ package by Rhenan Bartels. All credits go to him.

    Parameters
    ----------
    rpeaks : list or ndarray
        R-peak location indices.
    rri: list or ndarray
        RR intervals in the signal. If this argument is passed, rpeaks should not be passed.
    sampling_rate : int
        Sampling rate (samples/second).
    hrv_features : list
        What HRV indices to compute. Any or all of 'time', 'frequency' or 'nonlinear'.

    Returns
    ----------
    hrv : dict
        Contains hrv features and percentage of detected artifacts.

    Example
    ----------
    >>> import neurokit as nk
    >>> sampling_rate = 1000
    >>> hrv = nk.bio_ecg.ecg_hrv(rpeaks=rpeaks, sampling_rate=sampling_rate)

    Notes
    ----------
    *Details*

    - **HRV**: Heart-Rate Variability (HRV) is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013). It describes the complex variation of beat-to-beat intervals mainly controlled by the autonomic nervous system (ANS) through the interplay of sympathetic and parasympathetic neural activity at the sinus node. In healthy subjects, the dynamic cardiovascular control system is characterized by its ability to adapt to physiologic perturbations and changing conditions maintaining the cardiovascular homeostasis (Voss, 2015). In general, the HRV is influenced by many several factors like chemical, hormonal and neural modulations, circadian changes, exercise, emotions, posture and preload. There are several procedures to perform HRV analysis, usually classified into three categories: time domain methods, frequency domain methods and non-linear methods.

       - **sdNN**: The standard deviation of the time interval between successive normal heart beats (*i.e.*, the RR intervals). Reflects all influences on HRV including slow influences across the day, circadian variations, the effect of hormonal influences such as cortisol and epinephrine. It should be noted that total variance of HRV increases with the length of the analyzed recording.
       - **meanNN**: The the mean RR interval.
       - **CVSD**: The coefficient of variation of successive differences (van Dellen et al., 1985), the RMSSD divided by meanNN.
       - **cvNN**: The Coefficient of Variation, *i.e.* the ratio of sdNN divided by meanNN.
       - **RMSSD** is the root mean square of the RR intervals (*i.e.*, square root of the mean of the squared differences in time between successive normal heart beats). Reflects high frequency (fast or parasympathetic) influences on HRV (*i.e.*, those influencing larger changes from one beat to the next).
       - **medianNN**: Median of the Absolute values of the successive Differences between the RR intervals.
       - **madNN**: Median Absolute Deviation (MAD) of the RR intervals.
       - **mcvNN**: Median-based Coefficient of Variation, *i.e.* the ratio of madNN divided by medianNN.
       - **pNN50**: The proportion derived by dividing NN50 (The number of interval differences of successive RR intervals greater than 50 ms) by the total number of RR intervals.
       - **pNN20**: The proportion derived by dividing NN20 (The number of interval differences of successive RR intervals greater than 20 ms) by the total number of RR intervals.
       - **Triang**: The HRV triangular index measurement is the integral of the density distribution (that is, the number of all RR intervals) divided by the maximum of the density distribution (class width of 8ms).
       - **Shannon_h**: Shannon Entropy calculated on the basis of the class probabilities pi (i = 1,...,n with n—number of classes) of the NN interval density distribution (class width of 8 ms resulting in a smoothed histogram suitable for HRV analysis).
       - **VLF** is the variance (*i.e.*, power) in HRV in the Very Low Frequency (.003 to .04 Hz). Reflect an intrinsic rhythm produced by the heart which is modulated by primarily by sympathetic activity.
       - **LF**  is the variance (*i.e.*, power) in HRV in the Low Frequency (.04 to .15 Hz). Reflects a mixture of sympathetic and parasympathetic activity, but in long-term recordings like ours, it reflects sympathetic activity and can be reduced by the beta-adrenergic antagonist propanolol (McCraty & Atkinson, 1996).
       - **HF**  is the variance (*i.e.*, power) in HRV in the High Frequency (.15 to .40 Hz). Reflects fast changes in beat-to-beat variability due to parasympathetic (vagal) activity. Sometimes called the respiratory band because it corresponds to HRV changes related to the respiratory cycle and can be increased by slow, deep breathing (about 6 or 7 breaths per minute) (Kawachi et al., 1995) and decreased by anticholinergic drugs or vagal blockade (Hainsworth, 1995).
       - **Total_Power**: Total power of the density spectra.
       - **LFHF**: The LF/HF ratio is sometimes used by some investigators as a quantitative mirror of the sympatho/vagal balance.
       - **LFn**: normalized LF power LFn = LF/(LF+HF).
       - **HFn**: normalized HF power HFn = HF/(LF+HF).
       - **LFp**: ratio between LF and Total_Power.
       - **HFp**: ratio between H and Total_Power.
       - **DFA**: Detrended fluctuation analysis (DFA) introduced by Peng et al. (1995) quantifies the fractal scaling properties of time series. DFA_1 is the short-term fractal scaling exponent calculated over n = 4–16 beats, and DFA_2 is the long-term fractal scaling exponent calculated over n = 16–64 beats.
       - **Shannon**: Shannon Entropy over the RR intervals array.
       - **Sample_Entropy**: Sample Entropy (SampEn) over the RR intervals array with emb_dim=2.
       - **Correlation_Dimension**: Correlation Dimension over the RR intervals array with emb_dim=2.
       - **Entropy_Multiscale**: Multiscale Entropy over the RR intervals array  with emb_dim=2.
       - **Entropy_SVD**: SVD Entropy over the RR intervals array with emb_dim=2.
       - **Entropy_Spectral_VLF**: Spectral Entropy over the RR intervals array in the very low frequency (0.003-0.04).
       - **Entropy_Spectral_LF**: Spectral Entropy over the RR intervals array in the low frequency (0.4-0.15).
       - **Entropy_Spectral_HF**: Spectral Entropy over the RR intervals array in the very high frequency (0.15-0.40).
       - **Fisher_Info**: Fisher information over the RR intervals array with tau=1 and emb_dim=2.
       - **Lyapunov**: Lyapunov Exponent over the RR intervals array with emb_dim=58 and matrix_dim=4.
       - **FD_Petrosian**: Petrosian's Fractal Dimension over the RR intervals.
       - **FD_Higushi**: Higushi's Fractal Dimension over the RR intervals array with k_max=16.

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    - Rhenan Bartels (https://github.com/rhenanbartels)

    *Dependencies*

    - scipy
    - numpy

    *See Also*

    - RHRV: http://rhrv.r-forge.r-project.org/

    References
    -----------
    - Heart rate variability. (1996). Standards of measurement, physiological interpretation, and clinical use. Task Force of the European Society of Cardiology and the North American Society of Pacing and Electrophysiology. Eur Heart J, 17, 354-381.
    - Voss, A., Schroeder, R., Heitmann, A., Peters, A., & Perz, S. (2015). Short-term heart rate variability—influence of gender and age in healthy subjects. PloS one, 10(3), e0118308.
    - Zohar, A. H., Cloninger, C. R., & McCraty, R. (2013). Personality and heart rate variability: exploring pathways from personality to cardiac coherence and health. Open Journal of Social Sciences, 1(06), 32.
    - Smith, A. L., Owen, H., & Reynolds, K. J. (2013). Heart rate variability indices for very short-term (30 beat) analysis. Part 2: validation. Journal of clinical monitoring and computing, 27(5), 577-585.
    - Lippman, N. E. A. L., Stein, K. M., & Lerman, B. B. (1994). Comparison of methods for removal of ectopy in measurement of heart rate variability. American Journal of Physiology-Heart and Circulatory Physiology, 267(1), H411-H418.
    - Peltola, M. A. (2012). Role of editing of R–R intervals in the analysis of heart rate variability. Frontiers in physiology, 3.
    """
    # Check arguments: exactly one of rpeaks or rri has to be given as input
    if rpeaks is None and rri is None:
        raise ValueError("Either rpeaks or RRIs needs to be given.")

    if rpeaks is not None and rri is not None:
        raise ValueError("Either rpeaks or RRIs should be given but not both.")

    # Initialize empty dict
    hrv = {}

    # Preprocessing
    # ==================
    # Extract RR intervals (RRis)
    if rpeaks is not None:
        # Rpeaks is given, RRis need to be computed
        RRis = np.diff(rpeaks)
    else:
        # Case where RRis are already given:
        RRis = rri


    # Basic resampling to 1Hz to standardize the scale
    RRis = RRis/sampling_rate
    RRis = RRis.astype(float)


    # Artifact detection - Statistical
    for index, rr in enumerate(RRis):
        # Remove RR intervals that differ more than 25% from the previous one
        if RRis[index] < RRis[index-1]*0.75:
            RRis[index] = np.nan
        if RRis[index] > RRis[index-1]*1.25:
            RRis[index] = np.nan

    # Artifact detection - Physiological (http://emedicine.medscape.com/article/2172196-overview)
    RRis = pd.Series(RRis)
    RRis[RRis < 0.6] = np.nan
    RRis[RRis > 1.3] = np.nan

     # Sanity check
    if len(RRis) <= 1:
        print("NeuroKit Warning: ecg_hrv(): Not enough R peaks to compute HRV :/")
        return(hrv)

    # Artifacts treatment
    hrv["n_Artifacts"] = pd.isnull(RRis).sum()/len(RRis)
    artifacts_indices = RRis.index[RRis.isnull()]  # get the artifacts indices
    RRis = RRis.drop(artifacts_indices)  # remove the artifacts


    # Rescale to 1000Hz
    RRis = RRis*1000
    hrv["RR_Intervals"] = RRis  # Values of RRis

    # Sanity check after artifact removal
    if len(RRis) <= 1:
        print("NeuroKit Warning: ecg_hrv(): Not enough normal R peaks to compute HRV :/")
        return(hrv)

    # Time Domain
    # ==================
    if "time" in hrv_features:
        hrv["RMSSD"] = np.sqrt(np.mean(np.diff(RRis) ** 2))
        hrv["meanNN"] = np.mean(RRis)
        hrv["sdNN"] = np.std(RRis, ddof=1)  # make it calculate N-1
        hrv["cvNN"] = hrv["sdNN"] / hrv["meanNN"]
        hrv["CVSD"] = hrv["RMSSD"] / hrv["meanNN"]
        hrv["medianNN"] = np.median(abs(RRis))
        hrv["madNN"] = mad(RRis, constant=1)
        hrv["mcvNN"] = hrv["madNN"] / hrv["medianNN"]
        nn50 = sum(abs(np.diff(RRis)) > 50)
        nn20 = sum(abs(np.diff(RRis)) > 20)
        hrv["pNN50"] = nn50 / len(RRis) * 100
        hrv["pNN20"] = nn20 / len(RRis) * 100






    # Frequency Domain Preparation
    # ==============================
    if "frequency" in hrv_features:

        # Interpolation
        # =================
        # Convert to continuous RR interval (RRi)
        beats_times = rpeaks[1:].copy()  # the time at which each beat occured starting from the 2nd beat
        beats_times -= list(beats_times)[0]  # So it starts at 0
        beats_times = np.delete(list(beats_times), artifacts_indices)  # delete also the artifact beat moments

        try:
            RRi = interpolate(RRis, beats_times, sampling_rate)  # Interpolation using 3rd order spline
        except TypeError:
            print("NeuroKit Warning: ecg_hrv(): Sequence too short to compute interpolation. Will skip many features.")
            return(hrv)


        hrv["df"] = RRi.to_frame("ECG_RR_Interval")  # Continuous (interpolated) signal of RRi



        # Geometrical Method (actually part of time domain)
        # =========================================
        # TODO: This part needs to be checked by an expert. Also, it would be better to have Renyi entropy (a generalization of shannon's), but I don't know how to compute it.
        try:
            bin_number = 32  # Initialize bin_width value
            # find the appropriate number of bins so the class width is approximately 8 ms (Voss, 2015)
            for bin_number_current in range(2, 50):
                bin_width = np.diff(np.histogram(RRi, bins=bin_number_current, density=True)[1])[0]
                if abs(8 - bin_width) < abs(8 - np.diff(np.histogram(RRi, bins=bin_number, density=True)[1])[0]):
                    bin_number = bin_number_current
            hrv["Triang"] = len(RRis)/np.max(np.histogram(RRi, bins=bin_number, density=True)[0])
            hrv["Shannon_h"] = complexity_entropy_shannon(np.histogram(RRi, bins=bin_number, density=True)[0])
        except ValueError:
            hrv["Triang"] = np.nan
            hrv["Shannon_h"] = np.nan



        # Frequency Domain Features
        # ==========================
        freq_bands = {
          "ULF": [0.0001, 0.0033],
          "VLF": [0.0033, 0.04],
          "LF": [0.04, 0.15],
          "HF": [0.15, 0.40],
          "VHF": [0.4, 0.5]}


        # Frequency-Domain Power over time
        freq_powers = {}
        for band in freq_bands:
            freqs = freq_bands[band]
            # Filter to keep only the band of interest
            filtered, sampling_rate, params = biosppy.signals.tools.filter_signal(signal=RRi, ftype='butter', band='bandpass', order=1, frequency=freqs, sampling_rate=sampling_rate)
            # Apply Hilbert transform
            amplitude, phase = biosppy.signals.tools.analytic_signal(filtered)
            # Extract Amplitude of Envelope (power)
            freq_powers["ECG_HRV_" + band] = amplitude

        freq_powers = pd.DataFrame.from_dict(freq_powers)
        freq_powers.index = hrv["df"].index
        hrv["df"] = pd.concat([hrv["df"], freq_powers], axis=1)


        # Compute Power Spectral Density (PSD) using multitaper method
        power, freq = mne.time_frequency.psd_array_multitaper(RRi, sfreq=sampling_rate, fmin=0, fmax=0.5,  adaptive=False, normalization='length')

        def power_in_band(power, freq, band):
            power =  np.trapz(y=power[(freq >= band[0]) & (freq < band[1])], x=freq[(freq >= band[0]) & (freq < band[1])])
            return(power)

        # Extract Power according to frequency bands
        hrv["ULF"] = power_in_band(power, freq, freq_bands["ULF"])
        hrv["VLF"] = power_in_band(power, freq, freq_bands["VLF"])
        hrv["LF"] = power_in_band(power, freq, freq_bands["LF"])
        hrv["HF"] = power_in_band(power, freq, freq_bands["HF"])
        hrv["VHF"] = power_in_band(power, freq, freq_bands["VHF"])
        hrv["Total_Power"] = power_in_band(power, freq, [0, 0.5])

        hrv["LFn"] = hrv["LF"]/(hrv["LF"]+hrv["HF"])
        hrv["HFn"] = hrv["HF"]/(hrv["LF"]+hrv["HF"])
        hrv["LF/HF"] = hrv["LF"]/hrv["HF"]
        hrv["LF/P"] = hrv["LF"]/hrv["Total_Power"]
        hrv["HF/P"] = hrv["HF"]/hrv["Total_Power"]


    # TODO: THIS HAS TO BE CHECKED BY AN EXPERT - Should it be applied on the interpolated on raw RRis?
    # Non-Linear Dynamics
    # ======================
    if "nonlinear" in hrv_features:
        if len(RRis) > 17:
            hrv["DFA_1"] = nolds.dfa(RRis, range(4, 17))
        if len(RRis) > 66:
            hrv["DFA_2"] = nolds.dfa(RRis, range(16, 66))
        hrv["Shannon"] = complexity_entropy_shannon(RRis)
        hrv["Sample_Entropy"] = nolds.sampen(RRis, emb_dim=2)
        try:
            hrv["Correlation_Dimension"] = nolds.corr_dim(RRis, emb_dim=2)
        except AssertionError as error:
            print("NeuroKit Warning: ecg_hrv(): Correlation Dimension. Error: " + str(error))
            hrv["Correlation_Dimension"] = np.nan
        mse = complexity_entropy_multiscale(RRis, max_scale_factor=20, m=2)
        hrv["Entropy_Multiscale_AUC"] = mse["MSE_AUC"]
        hrv["Entropy_SVD"] = complexity_entropy_svd(RRis, emb_dim=2)
        hrv["Entropy_Spectral_VLF"] = complexity_entropy_spectral(RRis, sampling_rate, bands=np.arange(0.0033, 0.04, 0.001))
        hrv["Entropy_Spectral_LF"] = complexity_entropy_spectral(RRis, sampling_rate, bands=np.arange(0.04, 0.15, 0.001))
        hrv["Entropy_Spectral_HF"] = complexity_entropy_spectral(RRis, sampling_rate, bands=np.arange(0.15, 0.40, 0.001))
        hrv["Fisher_Info"] = complexity_fisher_info(RRis, tau=1, emb_dim=2)
#        lyap exp doesn't work for some reasons
#        hrv["Lyapunov"] = np.max(nolds.lyap_e(RRis, emb_dim=58, matrix_dim=4))

        hrv["FD_Petrosian"] = complexity_fd_petrosian(RRis)
        hrv["FD_Higushi"] = complexity_fd_higushi(RRis, k_max=16)

    # TO DO:
    # Include many others (see Voss 2015)


    return(hrv)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_hrv_assessment(hrv, age=None, sex=None, position=None):
    """
    Correct HRV features based on normative data from Voss et al. (2015).

    Parameters
    ----------
    hrv : dict
        HRV features obtained by :function:`neurokit.ecg_hrv`.
    age : float
        Subject's age.
    sex : str
        Subject's gender ("m" or "f").
    position : str
        Recording position. To compare with data from Voss et al. (2015), use "supine".


    Returns
    ----------
    hrv_adjusted : dict
        Adjusted HRV features.

    Example
    ----------
    >>> import neurokit as nk
    >>> hrv = nk.bio_ecg.ecg_hrv(rpeaks=rpeaks)
    >>> ecg_hrv_assessment = nk.bio_ecg.ecg_hrv_assessment(hrv)

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Details*

    - **Adjusted HRV**: The raw HRV features are normalized :math:`(raw - Mcluster) / sd` according to the participant's age and gender. In data from Voss et al. (2015), HRV analysis was performed on 5-min ECG recordings (lead II and lead V2 simultaneously, 500 Hz sampling rate) obtained in supine position after a 5–10 minutes resting phase. The cohort of healthy subjects consisted of 782 women and 1124 men between the ages of 25 and 74 years, clustered into 4 groups: YF (Female, Age = [25-49], n=571), YM (Male, Age = [25-49], n=744), EF (Female, Age = [50-74], n=211) and EM (Male, Age = [50-74], n=571).


    References
    -----------
    - Voss, A., Schroeder, R., Heitmann, A., Peters, A., & Perz, S. (2015). Short-term heart rate variability—influence of gender and age in healthy subjects. PloS one, 10(3), e0118308.
    """
    hrv_adjusted = {}

    if position == "supine":
        if sex == "m":
            if age <= 49:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-930)/133
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-45.8)/18.8
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-34.0)/18.3

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-203)/262
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-101)/143
                hrv_adjusted["LF/HF_Adjusted"] = (hrv["LF/HF"]-3.33)/3.47
            else:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-911)/128
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-33.0)/14.8
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-20.5)/11.0

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-84)/115
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-29.5)/36.6
                hrv_adjusted["LF/HF_Adjusted"] = (hrv["LF/HF"]-4.29)/4.06
        if sex == "f":
            if age <= 49:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-901)/117
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-44.9)/19.2
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-36.5)/20.1

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-159)/181
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-125)/147
                hrv_adjusted["LF/HF_Adjusted"] = (hrv["LF/HF"]-2.75)/2.93
            else:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-880)/115
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-31.6)/13.6
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-22.0)/13.2

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-66)/83
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-41.4)/72.1
                hrv_adjusted["LF/HF_Adjusted"] = (hrv["LF/HF"]-2.09)/2.05

    return(hrv_adjusted)






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_EventRelated(epoch, event_length=1, window_post=0, features=["Heart_Rate", "Cardiac_Phase", "RR_Interval", "RSA", "HRV"]):
    """
    Extract event-related ECG changes.

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contained in the epochs dict returned by :function:`neurokit.create_epochs()` on dataframe returned by :function:`neurokit.bio_process()`. Index should range from -4s to +4s (relatively to event onset and end).
    event_length : int
        Event length in seconds.
    window_post : float
        Post-stimulus window size (in seconds) to include late responses (usually 3 or 4).
    features : list
        List of ECG features to compute, can contain "Heart_Rate", "Cardiac_Phase", "RR_Interval", "RSA", "HRV".

    Returns
    ----------
    ECG_Response : dict
        Event-related ECG response features.

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


    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    References
    -----------
    """
    def compute_features(variable, prefix, response):
        """
        Internal function to compute features and avoid spaguetti code.
        """
        response[prefix + "_Baseline"] = epoch[variable][0]
        response[prefix + "_Min"] = epoch[variable][0:window_end].min()
        response[prefix + "_MinDiff"] = response[prefix + "_Min"] - response[prefix + "_Baseline"]
        response[prefix + "_MinTime"] = epoch[variable][0:window_end].idxmin()
        response[prefix + "_Max"] = epoch[variable][0:window_end].max()
        response[prefix + "_MaxDiff"] = response[prefix + "_Max"] - response[prefix + "_Baseline"]
        response[prefix + "_MaxTime"] = epoch[variable][0:window_end].idxmax()
        response[prefix + "_Mean"] = epoch[variable][0:window_end].mean()
        response[prefix + "_MeanDiff"] = response[prefix + "_Mean"] - response[prefix + "_Baseline"]

        return(response)

    # Initialization
    ECG_Response = {}
    window_end = event_length + window_post

    # Heart Rate
    # =============
    if "Heart_Rate" in features:
        if "Heart_Rate" in epoch.columns:
            ECG_Response = compute_features("Heart_Rate", "ECG_Heart_Rate", ECG_Response)
    #
    # Cardiac Phase
    # =============
    if "Cardiac_Phase" in features:
        if "ECG_Systole" in epoch.columns:
            ECG_Response["ECG_Phase_Systole"] = epoch["ECG_Systole"][0]

            # Identify beginning and end
            systole_beg = np.nan
            systole_end = np.nan
            for i in epoch[0:window_end].index:
                if epoch["ECG_Systole"][i] != ECG_Response["ECG_Phase_Systole"]:
                    systole_end = i
                    break
            for i in epoch[:0].index[::-1]:
                if epoch["ECG_Systole"][i] != ECG_Response["ECG_Phase_Systole"]:
                    systole_beg = i
                    break

            # Compute percentage
            ECG_Response["ECG_Phase_Systole_Completion"] = -1*systole_beg/(systole_end - systole_beg)*100


    # RR Interval
    # ==================
    if "RR_Interval" in features:
        if "ECG_RR_Interval" in epoch.columns:
            ECG_Response = compute_features("ECG_RR_Interval", "ECG_RRi", ECG_Response)


    # RSA
    # ==========
    if "RSA" in features:
        if "RSA" in epoch.columns:
            ECG_Response = compute_features("RSA", "ECG_RSA", ECG_Response)

    # HRV
    # ====
    if "HRV" in features:
        if "ECG_R_Peaks" in epoch.columns:
            rpeaks = epoch[epoch["ECG_R_Peaks"]==1][0:event_length].index*1000
            hrv = ecg_hrv(rpeaks=rpeaks, sampling_rate=1000, hrv_features=["time"])

            # HRV time domain feature computation
            for key in hrv:
                if isinstance(hrv[key], float):  # Avoid storing series or dataframes
                    ECG_Response["ECG_HRV_" + key] = hrv[key]

            # Computation for baseline
            if epoch.index[0] > -4:  # Sanity check
                print("NeuroKit Warning: ecg_EventRelated(): your epoch starts less than 4 seconds before stimulus onset. That's too short to compute HRV baseline features.")
            else:
                rpeaks = epoch[epoch["ECG_R_Peaks"]==1][:0].index*1000
                hrv = ecg_hrv(rpeaks=rpeaks, sampling_rate=1000, hrv_features=["time"])

                for key in hrv:
                    if isinstance(hrv[key], float):  # Avoid storing series or dataframes
                        ECG_Response["ECG_HRV_" + key + "_Baseline"] = hrv[key]

                # Compute differences between features and baseline
                keys = [key for key in ECG_Response.keys() if '_Baseline' in key]  # Find keys
                keys = [key for key in keys if 'ECG_HRV_' in key]
                keys = [s.replace('_Baseline', '') for s in keys]  # Remove baseline part
                for key in keys:
                    try:
                        ECG_Response[key + "_Diff"] = ECG_Response[key] - ECG_Response[key + "_Baseline"]
                    except KeyError:
                        ECG_Response[key + "_Diff"] = np.nan



        if "ECG_HRV_VHF" in epoch.columns:
            ECG_Response = compute_features("ECG_HRV_VHF", "ECG_HRV_VHF", ECG_Response)

        if "ECG_HRV_HF" in epoch.columns:
            ECG_Response = compute_features("ECG_HRV_HF", "ECG_HRV_HF", ECG_Response)

        if "ECG_HRV_LF" in epoch.columns:
            ECG_Response = compute_features("ECG_HRV_LF", "ECG_HRV_LF", ECG_Response)

        if "ECG_HRV_VLF" in epoch.columns:
            ECG_Response = compute_features("ECG_HRV_VLF", "ECG_HRV_VLF", ECG_Response)


    return(ECG_Response)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_simulate(duration=10, sampling_rate=1000, bpm=60, noise=0.01):
    """
    Simulates an ECG signal.

    Parameters
    ----------
    duration : int
        Desired recording length.
    sampling_rate : int
        Desired sampling rate.
    bpm : int
        Desired simulated heart rate.
    noise : float
        Desired noise level.


    Returns
    ----------
    ECG_Response : dict
        Event-related ECG response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> import pandas as pd
    >>>
    >>> ecg = nk.ecg_simulate(duration=10, bpm=60, sampling_rate=1000, noise=0.01)
    >>> pd.Series(ecg).plot()

    Notes
    ----------
    *Authors*

    - `Diarmaid O Cualain <https://github.com/diarmaidocualain>`_
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy
    - scipy.signal

    References
    -----------
    """
    # The "Daubechies" wavelet is a rough approximation to a real, single, cardiac cycle
    cardiac = scipy.signal.wavelets.daub(10)
    # Add the gap after the pqrst when the heart is resting.
    cardiac = np.concatenate([cardiac, np.zeros(10)])

    # Caculate the number of beats in capture time period
    num_heart_beats = int(duration * bpm / 60)

    # Concatenate together the number of heart beats needed
    ecg = np.tile(cardiac , num_heart_beats)

    # Add random (gaussian distributed) noise
    noise = np.random.normal(0, noise, len(ecg))
    ecg = noise + ecg

    # Resample
    ecg = scipy.signal.resample(ecg, sampling_rate*duration)

    return(ecg)




