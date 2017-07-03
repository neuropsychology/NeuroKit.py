# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import biosppy
import sklearn
import scipy
import nolds
import mne

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
def ecg_process(ecg, rsp=None, sampling_rate=1000, quality_model="default", age=None, sex=None, position=None):
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
    quality_model : str
        Path to model used to check signal quality. "default" uses the builtin model.
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
    - **RSA**: Respiratory sinus arrhythmia (RSA) is a naturally occurring variation in heart rate that occurs during the breathing cycle, serving as a measure of parasympathetic nervous system activity.
    - **HRV**: Heart-Rate Variability (HRV) is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013). It describes the complex variation of beat-to-beat intervals mainly controlled by the autonomic nervous system (ANS) through the interplay of sympathetic and parasympathetic neural activity at the sinus node. In healthy subjects, the dynamic cardiovascular control system is characterized by its ability to adapt to physiologic perturbations and changing conditions maintaining the cardiovascular homeostasis (Voss, 2015). In general, the HRV is influenced by many several factors like chemical, hormonal and neural modulations, circadian changes, exercise, emotions, posture and preload. There are several procedures to perform HRV analysis, usually classified into three categories: time domain methods, frequency domain methods and non-linear methods. See :func:`neurokit.hrv()` for a description of indices.
    - **Adjusted HRV**: The raw HRV features are normalized :math:`(raw - Mcluster) / sd` according to the participant's age and gender. In data from Voss et al. (2015), HRV analysis was performed on 5-min ECG recordings (lead II and lead V2 simultaneously, 500 Hz sample rate) obtained in supine position after a 5–10 minutes resting phase. The cohort of healthy subjects consisted of 782 women and 1124 men between the ages of 25 and 74 years, clustered into 4 groups: YF (Female, Age = [25-49], n=571), YM (Male, Age = [25-49], n=744), EF (Female, Age = [50-74], n=211) and EM (Male, Age = [50-74], n=571).
    - **Systole/Diastole**: One prominent channel of body and brain communication is that conveyed by baroreceptors, pressure and stretch-sensitive receptors within the heart and surrounding arteries. Within each cardiac cycle, bursts of baroreceptor afferent activity encoding the strength and timing of each heartbeat are carried via the vagus and glossopharyngeal nerve afferents to the nucleus of the solitary tract. This is the principal route that communicates to the brain the dynamic state of the heart, enabling the representation of cardiovascular arousal within viscerosensory brain regions, and influence ascending neuromodulator systems implicated in emotional and motivational behaviour. Because arterial baroreceptors are activated by the arterial pulse pressure wave, their phasic discharge is maximal during and immediately after the cardiac systole, that is, when the blood is ejected from the heart, and minimal during cardiac diastole, that is, between heartbeats (Azevedo, 2017).
    - **ECG Signal Quality**: Using the PTB-Diagnostic dataset available from PhysioNet, we extracted all the ECGs signal from the healthy participants. For each ECG, the 15 leads were available. We extracted all cardiac cycles, for each lead, and downsampled them from 600 to 200 datapoints. Note that we dropped the 8 first values that were NaNs. Then, we fitted a neural network on 2/3 of the dataset (that contains 134392 cardiac cycles) to predict the lead. Model evaluation was done on the remaining 1/3. The model show good performances in predicting the correct recording lead (accuracy=0.91, precision=0.91). In this function, this model is fitted on each cardiac cycle. It returns the probable recording lead (the most common predicted lead), the signal quality of each cardiac cycle (the probability of belonging to the probable recording lead) and the overall signal quality (the mean of signal quality).

    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)
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
    # Convert to DataFrame
    ecg_df = pd.DataFrame({"ECG_Raw": np.array(ecg)})

    # Compute several features using biosppy
    biosppy_ecg = dict(biosppy.signals.ecg.ecg(ecg, sampling_rate=sampling_rate, show=False))

    # Filtered signal
    ecg_df["ECG_Filtered"] = biosppy_ecg["filtered"]

    # Store R peaks indexes
    rpeaks = biosppy_ecg['rpeaks']

    # Transform to markers to add to the main dataframe
    rpeaks_signal = np.array([np.nan]*len(ecg))
    rpeaks_signal[rpeaks] = 1
    ecg_df["ECG_R_peaks"] = rpeaks_signal

    # Heart Rate
    # =============
    heart_rate = biosppy_ecg["heart_rate"]  # Get heart rate values
    heart_rate_times = biosppy_ecg["heart_rate_ts"]  # the time (in sec)
    heart_rate_times = np.round(heart_rate_times*sampling_rate).astype(int)  # Convert to timepoints
    try:
        heart_rate = discrete_to_continuous(heart_rate, heart_rate_times, sampling_rate)  # Interpolation using 3rd order spline
        ecg_df["Heart_Rate"] = heart_rate
    except TypeError:
        print("NeuroKit Warning: ecg_process(): Sequence too short to compute heart rate.")
        ecg_df["Heart_Rate"] = np.nan

    # Heartbeats
    # =============
    heartbeats = pd.DataFrame(biosppy_ecg["templates"]).T
    heartbeats.index = pd.date_range(pd.datetime.today(), periods=len(heartbeats), freq=str(int(1000/sampling_rate)) + "L")

    # Signal quality
    # =============
    quality = ecg_signal_quality(heartbeats, sampling_rate, quality_model=quality_model)

    # Waves
    # =============
    waves = ecg_wave_detector(ecg_df["ECG_Filtered"], rpeaks)

    # Systole
    # =============
    ecg_df["ECG_Systole"] = ecg_systole(ecg_df["ECG_Filtered"], rpeaks, waves["T_Waves"])

    # Store results
    # =============
    processed_ecg = {"df": ecg_df,
                     "ECG": {
                            "Cardiac_Cycles": heartbeats,
                            "R_Peaks": biosppy_ecg["rpeaks"]
                            }
                     }

    processed_ecg["ECG"].update(quality)
    processed_ecg["ECG"].update(waves)

    # HRV
    # =============
    hrv = ecg_hrv(rpeaks, sampling_rate)
    processed_ecg["ECG"]["HRV"] = hrv
    processed_ecg["df"]["ECG_HRV"] = hrv["RR_Interval"]
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
        rsa = ecg_RSA(rpeaks, rsp["df"]["RSP_Filtered"], sampling_rate=sampling_rate)
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
def ecg_find_peaks(signal, sampling_rate=1000):
    """
    Find R peaks indices on the ECG channel.

    Parameters
    ----------
    signal : list or ndarray
        ECG signal (preferably filtered).
    sampling_rate : int
        Sampling rate (samples/second).


    Returns
    ----------
    rpeaks : list
        List of R-peaks location indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> Rpeaks = nk.ecg_find_peaks(signal)

    Notes
    ----------
    *Authors*

    - the bioSSPy dev team (https://github.com/PIA-Group/BioSPPy)

    *Dependencies*

    - biosppy

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy

    """
    rpeaks, = biosppy.ecg.hamilton_segmenter(signal, sampling_rate=sampling_rate)
    rpeaks, = biosppy.ecg.correct_rpeaks(signal=signal, rpeaks=rpeaks, sampling_rate=sampling_rate, tol=0.05)
    return(rpeaks)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_RSA(rpeaks, rsp, sampling_rate=1000):
    """
    Returns Respiratory Sinus Arrhythmia (RSA) features.

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
    >>> rsa = nk.respiratory_sinus_arrhythmia(rpeaks, rsp_cycles, rsp_signal)

    Notes
    ----------
    *Details*

    - **RSA**: Respiratory sinus arrhythmia (RSA) is a naturally occurring variation in heart rate that occurs during the breathing cycle, serving as a measure of parasympathetic nervous system activity.

    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)
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
    rsa["RSA_P2T_Variability"] = pd.Series(rsa["RSA_P2T_Values"]).std()

    # Continuous RSA - Interpolation using a 3rd order spline
    if len(rsp_cycle_center) - len(rsa["RSA_P2T_Values"]) != 0:
        print("NeuroKit Error: ecg_rsp(): Couldn't find clean rsp cycles onsets and centers. Check your RSP signal.")
        return()
    value_times=(np.array(rsp_cycle_center)-rsp_cycle_center[0])/sampling_rate
    rsa_interpolated = nk.discrete_to_continuous(values=np.array(rsa["RSA_P2T_Values"]), value_times=value_times, sampling_rate=sampling_rate)


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
    df["RSA"] = np.nan
    df["RSA"].ix[rsp_cycle_center[0]:rsp_cycle_center[0]+len(rsa_interpolated)-1] = rsa_interpolated.values
    rsa["df"] = df


    # Porges–Bohrer method (RSAP–B)
    # ==============================
    # Need help to implement this method (Lewis, 2012)

    return(rsa)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_signal_quality(cardiac_cycles, sampling_rate, quality_model="default"):
    """
    Attempt to find the recording lead and the overall and individual quality of hearbeats signal.

    Parameters
    ----------
    cardiac_cycles : pd.DataFrame
        DataFrame containing heartbeats. Computed by :function:`neurokit.ecg_process`.
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

    - **ECG Signal Quality**: Using the PTB-Diagnostic dataset available from PhysioNet, we extracted all the ECGs signal from the healthy participants. For each ECG, the 15 leads were available. We extracted all cardiac cycles, for each lead, and downsampled them from 600 to 200 datapoints. Note that we dropped the 8 first values that were NaNs. Then, we fitted a neural network on 2/3 of the dataset (that contains 134392 cardiac cycles) to predict the lead. Model evaluation was done on the remaining 1/3. The model show good performances in predicting the correct recording lead (accuracy=0.91, precision=0.91). In this function, this model is fitted on each cardiac cycle. It returns the probable recording lead (the most common predicted lead), the signal quality of each cardiac cycle (the probability of belonging to the probable recording lead) and the overall signal quality (the mean of signal quality).

    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)

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

    quality = {}

    # Find dominant class
    lead = model.predict(cardiac_cycles)
    lead = pd.Series(lead).value_counts().index[0]
    quality["Probable_Lead"] = lead

    predict = pd.DataFrame(model.predict_proba(cardiac_cycles))
    predict.columns = model.classes_
    quality["Cardiac_Cycles_Signal_Quality"] = predict[lead].as_matrix()
    quality["Average_Signal_Quality"] = predict[lead].mean()

    return(quality)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_hrv(rpeaks, sampling_rate=1000):
    """
    Computes the Heart-Rate Variability (HRV). Shamelessly stolen from the `hrv <https://github.com/rhenanbartels/hrv/blob/develop/hrv>`_ package by Rhenan Bartels. All credits go to him.

    Parameters
    ----------
    rpeaks : list or ndarray
        R-peak location indices.
    sampling_rate : int
        Sampling rate (samples/second).

    Returns
    ----------
    hrv : dict
        Contains hrv features and percentage of detected artifacts.

    Example
    ----------
    >>> import neurokit as nk
    >>> hrv = nk.hrv(rri, 1000)

    Notes
    ----------
    *Details*

    - **HRV**: Heart-Rate Variability (HRV) is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013). It describes the complex variation of beat-to-beat intervals mainly controlled by the autonomic nervous system (ANS) through the interplay of sympathetic and parasympathetic neural activity at the sinus node. In healthy subjects, the dynamic cardiovascular control system is characterized by its ability to adapt to physiologic perturbations and changing conditions maintaining the cardiovascular homeostasis (Voss, 2015). In general, the HRV is influenced by many several factors like chemical, hormonal and neural modulations, circadian changes, exercise, emotions, posture and preload. There are several procedures to perform HRV analysis, usually classified into three categories: time domain methods, frequency domain methods and non-linear methods.

       - **sdNN**: The standard deviation of the time interval between successive normal heart beats (*i.e.*, the RR intervals). Reflects all influences on HRV including slow influences across the day, circadian variations, the effect of hormonal influences such as cortisol and epinephrine. It should be noted that total variance of HRV increases with the length of the analyzed recording.
       - **meanNN**: The the mean RR interval.
       - **CVSD**: The coefficient of variation of successive differences (van
Dellen et al., 1985), the RMSSD divided by meanNN.
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

    - Dominique Makowski (https://dominiquemakowski.github.io/)
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
    # Initialize empty dict
    hrv = {}

    # Preprocessing
    # ==================
    # Extract RR intervals (RRis)
    RRis = np.diff(rpeaks)
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

    # Artifacts treatment
    hrv["n_Artifacts"] = pd.isnull(RRis).sum()/len(RRis)
    artifacts_indices = RRis.index[RRis.isnull()]  # get the artifacts indices
    RRis = RRis.drop(artifacts_indices)  # remove the artifacts

    # Convert to continuous RR interval (RRi)
    beats_times = rpeaks[1:]  # the time at which each beat occured starting from the 2nd beat
    beats_times -= beats_times[0]
    beats_times = np.delete(beats_times, artifacts_indices)  # delete also the artifact beat moments
    try:
        RRi = discrete_to_continuous(RRis, beats_times, 1000)  # Interpolation using 3rd order spline
    except TypeError:
        print("NeuroKit Warning: ecg_hrv(): Sequence too short to compute HRV.")
        return(hrv)

    # Rescale to 1000Hz
    RRis = RRis*1000
    RRi = RRi*1000
    hrv["RR_Intervals"] = RRis  # Values of RRis
    hrv["RR_Interval"] = RRi  # Continuous (interpolated) signal of RRi

    # Time Domain
    # ==================
    hrv["RMSSD"] = np.sqrt(np.mean(np.diff(RRis) ** 2))
    hrv["meanNN"] = np.mean(RRis)
    hrv["sdNN"] = np.std(RRis, ddof=1)  # make it calculate N-1
    hrv["cvNN"] = hrv["sdNN"] / hrv["meanNN"]
    hrv["CVSD"] = hrv["RMSSD"] / hrv["meanNN"] * 100
    hrv["medianNN"] = np.median(abs(RRis))
    hrv["madNN"] = mad(RRis, constant=1)
    hrv["mcvNN"] = hrv["madNN"] / hrv["medianNN"]
    nn50 = sum(abs(np.diff(RRis)) > 50)
    hrv["pNN50"] = nn50 / len(RRis) * 100
    nn20 = sum(abs(np.diff(RRis)) > 20)
    hrv["pNN20"] = nn20 / len(RRis) * 100


    # To Do: This part needs to be checked by an expert. Also, it would be better to have Renyi entropy (a generalization of shannon's), but I don't know how to compute it.
    try:
        bin_number = 32  # Initialize bin_width value
        # find the appropriate number of bins so the class width is approximately 8 ms (Voss, 2015)
        for bin_number_current in range(2, 50):
            bin_width = np.diff(np.histogram(RRi, bins=bin_number_current, density=True)[1])[0]
            if abs(8 - bin_width) < abs(8 - np.diff(np.histogram(RRi, bins=bin_number, density=True)[1])[0]):
                bin_number = bin_number_current
        hrv["Triang"] = len(RRis)/np.max(np.histogram(RRi, bins=bin_number, density=True)[0])
        hrv["Shannon_h"] = entropy_shannon(np.histogram(RRi, bins=bin_number, density=True)[0])
    except ValueError:
        hrv["Triang"] = np.nan
        hrv["Shannon_h"] = np.nan


    # Frequency Domain
    # =================
    # Compute Power Spectral Density (PSD) using multitaper method
    power, freq = mne.time_frequency.psd_array_multitaper(RRi, sfreq=10, fmin=0, fmax=0.5,  adaptive=False, normalization='full')

    def power_in_band(power, freq, low, high):
        power =  np.trapz(y=power[(freq >= low) & (freq < high)], x=freq[(freq >= low) & (freq < high)])
        return(power)

    # Extract Power according to frequency bands
    hrv["ULF"] = power_in_band(power, freq, 0, 0.0033)
    hrv["VLF"] = power_in_band(power, freq, 0.0033, 0.04)
    hrv["LF"] = power_in_band(power, freq, 0.04, 0.15)
    hrv["HF"] = power_in_band(power, freq, 0.15, 0.4)
    hrv["VHF"] = power_in_band(power, freq, 0.4, 0.5)
    hrv["Total_Power"] = power_in_band(power, freq, 0, 0.5)

    hrv["LFn"] = hrv["LF"]/(hrv["LF"]+hrv["HF"])
    hrv["HFn"] = hrv["HF"]/(hrv["LF"]+hrv["HF"])
    hrv["LF/HF"] = hrv["LF"]/hrv["HF"]
    hrv["LF/P"] = hrv["LF"]/hrv["Total_Power"]
    hrv["HF/P"] = hrv["HF"]/hrv["Total_Power"]


    # Non-Linear Dynamics - This also must be checked by an expert - Should it be applied on the interpolated on raw RRis?
    # ======================
    if len(RRis) > 17:
        hrv["DFA_1"] = nolds.dfa(RRis, range(4, 17))
    if len(RRis) > 66:
        hrv["DFA_2"] = nolds.dfa(RRis, range(16, 66))
    hrv["Shannon"] = entropy_shannon(RRis)
    hrv["Sample_Entropy"] = nolds.sampen(RRis, emb_dim=2)
    try:
        hrv["Correlation_Dimension"] = nolds.corr_dim(RRis, emb_dim=2)
    except AssertionError as error:
        print("NeuroKit Warning: ecg_hrv(): Correlation Dimension. Error: " + str(error))
        hrv["Correlation_Dimension"] = np.nan
    hrv["Entropy_Multiscale"] = entropy_multiscale(RRis, emb_dim=2)
    hrv["Entropy_SVD"] = entropy_svd(RRis, emb_dim=2)
    hrv["Entropy_Spectral_VLF"] = entropy_spectral(RRis, 1000, bands=np.arange(0.0033, 0.04, 0.001))
    hrv["Entropy_Spectral_LF"] = entropy_spectral(RRis, 1000, bands=np.arange(0.04, 0.15, 0.001))
    hrv["Entropy_Spectral_HF"] = entropy_spectral(RRis, 1000, bands=np.arange(0.15, 0.40, 0.001))
    hrv["Fisher_Info"] = fisher_info(RRis, tau=1, emb_dim=2)
    try:  # Otherwise travis errors for some reasons :(
        hrv["Lyapunov"] = np.max(nolds.lyap_e(RRis, emb_dim=58, matrix_dim=4))
    except Exception:
        hrv["Lyapunov"] = np.nan
    hrv["FD_Petrosian"] = fd_petrosian(RRis)
    hrv["FD_Higushi"] = fd_higushi(RRis, k_max=16)

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
    >>> hrv = nk.ecg_hrv(rri)
    >>> ecg_hrv_assessment = nk.ecg_hrv(hrv)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)

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
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-3.33)/3.47
            else:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-911)/128
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-33.0)/14.8
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-20.5)/11.0

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-84)/115
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-29.5)/36.6
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-4.29)/4.06
        if sex == "f":
            if age <= 49:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-901)/117
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-44.9)/19.2
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-36.5)/20.1

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-159)/181
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-125)/147
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-2.75)/2.93
            else:
                hrv_adjusted["meanNN_Adjusted"] = (hrv["meanNN"]-880)/115
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-31.6)/13.6
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-22.0)/13.2

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-66)/83
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-41.4)/72.1
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-2.09)/2.05

    return(hrv_adjusted)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_wave_detector(ecg, rpeaks, plot=False):
    """
    Returns the localization of the P, Q, T waves.

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal (preferably filtered).
    rpeaks : list or ndarray
        R peaks localization.
    plot : bool
        Visually check the location.

    Returns
    ----------
    ecg_waves : dict
        Contains wave peaks location indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> ecg_waves = nk.ecg_wave_detector(signal, rpeaks)

    Notes
    ----------
    *Details*

    - **Cardiac Cycle**: A typical ECG showing a heartbeat consists of a P wave, a QRS complex and a T wave.The P wave represents the wave of depolarization that spreads from the SA-node throughout the atria. The QRS complex reflects the rapid depolarization of the right and left ventricles. Since the ventricles are the largest part of the heart, in terms of mass, the QRS complex usually has a much larger amplitude than the P-wave. The T wave represents the ventricular repolarization of the ventricles. On rare occasions, a U wave can be seen following the T wave. The U wave is believed to be related to the last remnants of ventricular repolarization.

    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)






    """
    t_waves = []
    for index, rpeak in enumerate(rpeaks[0:-1]):
        # T wave
        middle = (rpeaks[index+1] - rpeak) / 2
        quarter = middle/2

        epoch = np.array(ecg)
        epoch = epoch[int(rpeak+quarter):int(rpeak+middle)]

        try:
            t_wave = int(rpeak+quarter) + np.argmax(epoch)
            t_waves.append(t_wave)
        except ValueError:
            pass

    p_waves = []
    for index, rpeak in enumerate(rpeaks[1:]):
        index += 1
        # Q wave
        middle = (rpeak - rpeaks[index-1]) / 2
        quarter = middle/2

        epoch = np.array(ecg)
        epoch = epoch[int(rpeak-middle):int(rpeak-quarter)]

        try:
            p_wave = int(rpeak-quarter) + np.argmax(epoch)
            p_waves.append(p_wave)
        except ValueError:
            pass

    q_waves = []
    for index, p_wave in enumerate(p_waves):
        epoch = np.array(ecg)
        epoch = epoch[int(p_wave):int(rpeaks[rpeaks>p_wave][0])]

        try:
            q_wave = p_wave + np.argmin(epoch)
            q_waves.append(q_wave)
        except ValueError:
            pass

    if plot is True:
        plot_events_in_signal(signal, [p_waves, q_waves, list(rpeaks), t_waves], color=["green", "orange", "red", "blue"])

    ecg_waves = {"T_Waves": t_waves, "P_Waves": p_waves, "Q_Waves": q_waves}
    return(ecg_waves)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_systole(ecg, rpeaks, t_waves):
    """
    Returns the localization of systoles and diastoles.

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal (preferably filtered).
    rpeaks : list or ndarray
        R peaks localization.
    t_waves : list or ndarray
        T waves localization.

    Returns
    ----------
    systole : ndarray
        Array indicating where systole (1) and diastole (0).

    Example
    ----------
    >>> import neurokit as nk
    >>> systole = nk.ecg_systole(ecg, rpeaks, t_waves)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)

    *Details*

    - **Systole/Diastole**: One prominent channel of body and brain communication is that conveyed by baroreceptors, pressure and stretch-sensitive receptors within the heart and surrounding arteries. Within each cardiac cycle, bursts of baroreceptor afferent activity encoding the strength and timing of each heartbeat are carried via the vagus and glossopharyngeal nerve afferents to the nucleus of the solitary tract. This is the principal route that communicates to the brain the dynamic state of the heart, enabling the representation of cardiovascular arousal within viscerosensory brain regions, and influence ascending neuromodulator systems implicated in emotional and motivational behaviour. Because arterial baroreceptors are activated by the arterial pulse pressure wave, their phasic discharge is maximal during and immediately after the cardiac systole, that is, when the blood is ejected from the heart, and minimal during cardiac diastole, that is, between heartbeats (Azevedo, 2017).

    References
    -----------
    - Azevedo, R. T., Garfinkel, S. N., Critchley, H. D., & Tsakiris, M. (2017). Cardiac afferent activity modulates the expression of racial stereotypes. Nature communications, 8.
    - Edwards, L., Ring, C., McIntyre, D., & Carroll, D. (2001). Modulation of the human nociceptive flexion reflex across the cardiac cycle. Psychophysiology, 38(4), 712-718.
    - Gray, M. A., Rylander, K., Harrison, N. A., Wallin, B. G., & Critchley, H. D. (2009). Following one's heart: cardiac rhythms gate central initiation of sympathetic reflexes. Journal of Neuroscience, 29(6), 1817-1825.
    """
    waves = np.array([""]*len(ecg))
    waves[rpeaks] = "R"
    waves[t_waves] = "T"

    systole = [0]
    current = 0
    for index, value in enumerate(waves[1:]):
        if waves[index-1] == "R":
            current = 1
        if waves[index-1] == "T":
            current = 0
        systole.append(current)

    return(systole)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_EventRelated(epoch, event_length, sampling_rate=1000, window_post=4):
    """
    Extract event-related ECG changes.

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contains in the epochs dict returned by :function:`neurokit.create_epochs()` on dataframe returned by :function:`neurokit.bio_process()`. Index should range from -4s to +4s (relatively to event onset and end).
    event_length : int
        In seconds.
    sampling_rate : int
        Sampling rate (samples/second).
    window_post : float
        Post-stimulus window size (in seconds) to include eventual responses (usually 3 or 4).

    Returns
    ----------
    ECG_Response : dict
        Event-related ECG response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(ecg=df["ECG"], add=df["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+8000, onset=-4000)
    >>> for epoch in epochs:
    >>>     ECG_Response = nk.ecg_ERP(epoch, event_length=4000)

    Notes
    ----------
    *Details*

    - **Heart_Rate_Baseline**: mean HR before stimulus onset.
    - **Heart_Rate_Min**: Min HR after stimulus onset.
    - **Heart_Rate_MinDiff**: HR mininum - baseline.
    - **Heart_Rate_MinTime**: Time of minimum.
    - **Heart_Rate_Max**: Max HR after stimulus onset.
    - **Heart_Rate_MaxDiff**: Max HR - baseline.
    - **Heart_Rate_MaxTime**: Time of maximum.
    - **Heart_Rate_Mean**: Mean HR after stimulus onset.
    - **Heart_Rate_MeanDiff**: Mean HR - baseline.
    - **Cardiac_Systole**: Cardiac phase on stimulus onset (1 = systole, 0 = diastole).
    - **Cardiac_Systole_Completion**: Percentage of cardiac phase completion on simulus onset.
    - **HRV**: Returns HRV features. See :func:`neurokit.ecg_hrv()`.
    - **HRV_Diff**: HRV post-stimulus - HRV pre-stimulus.



    *Authors*

    - Dominique Makowski (https://dominiquemakowski.github.io/)

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    References
    -----------
    """
    # Initialization
    event_length = event_length/sampling_rate*1000
    ECG_Response = {}

    # Heart Rate
    ECG_Response["Heart_Rate_Baseline"] = epoch["Heart_Rate"].ix[:0].mean()
    ECG_Response["Heart_Rate_Min"] = epoch["Heart_Rate"].ix[0:event_length].min()
    ECG_Response["Heart_Rate_MinDiff"] = ECG_Response["Heart_Rate_Min"] - ECG_Response["Heart_Rate_Baseline"]
    ECG_Response["Heart_Rate_MinTime"] = epoch["Heart_Rate"].ix[0:event_length].idxmin()/sampling_rate*1000
    ECG_Response["Heart_Rate_Max"] = epoch["Heart_Rate"].ix[0:event_length].max()
    ECG_Response["Heart_Rate_MaxDiff"] = ECG_Response["Heart_Rate_Max"] - ECG_Response["Heart_Rate_Baseline"]
    ECG_Response["Heart_Rate_MaxTime"] = epoch["Heart_Rate"].ix[0:event_length].idxmax()/sampling_rate*1000
    ECG_Response["Heart_Rate_Mean"] = epoch["Heart_Rate"].ix[0:event_length].mean()
    ECG_Response["Heart_Rate_MeanDiff"] = ECG_Response["Heart_Rate_Mean"] - ECG_Response["Heart_Rate_Baseline"]


    # Cardiac Phase
    ECG_Response["Cardiac_Systole"] = epoch["ECG_Systole"].ix[0]

    for i in range(0, int(event_length)-1):
        if epoch["ECG_Systole"].ix[i] != ECG_Response["Cardiac_Systole"]:
            systole_end = i
            break

    for i in range(0, epoch.index[0]+1, -1):
        if epoch["ECG_Systole"].ix[i] != ECG_Response["Cardiac_Systole"]:
            systole_beg = i
            break

    try:
        ECG_Response["Cardiac_Systole_Completion"] = -1*systole_beg/(systole_end - systole_beg)*100
    except ZeroDivisionError:
        ECG_Response["Cardiac_Systole_Completion"] = np.nan

    # HRV
    rpeaks_before = epoch[epoch["ECG_Rpeaks"]==1].ix[:0].index/sampling_rate*1000
    rri_before = np.diff(rpeaks_before)
    rpeaks = epoch[epoch["ECG_Rpeaks"]==1].ix[0:event_length].index/sampling_rate*1000
    rri = np.diff(rpeaks)

    try:
        hrv_baseline = ecg_hrv(rri_before, sampling_rate, segment_length=len(rri_before))
        hrv = ecg_hrv(rri, sampling_rate, segment_length=len(rri))

        for key in hrv:
            ECG_Response["HRV_" + key] = hrv[key]
            ECG_Response["HRV_Diff_" + key] = hrv[key] - hrv_baseline[key]
    except IndexError:
        print("NeuroKit Warning: ecg_ERP(): Not enough R peaks to compute HRV.")

    return(ECG_Response)