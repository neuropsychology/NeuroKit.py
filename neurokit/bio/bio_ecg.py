# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import biosppy
import datetime
import sklearn
import scipy
import nolds

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
def ecg_process(ecg, rsp=None, sampling_rate=1000, resampling_method="bfill", quality_model="default", hrv_segment_length=60, age=None, sex=None, position=None):
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
    resampling_method : str
        "mean", "pad" or "bfill", the resampling method used for ECG and RSP heart rate.
    quality_model : str
        Path to model used to check signal quality. "default" uses the builtin model.
    hrv_segment_length : int
        Number of RR intervals within each sliding window on which to compute frequency-domains power. Particularly important for VLF. Adjust with caution.
    age : float
        Subject's age.
    sex : str
        Subject's gender ("m" or "f").
    position : str
        Recording position. To compare with data from Voss et al. (2015), use "supine".

    Returns
    ----------
    processed_ecg : dict
        Dict containing processed ECG features.

        Contains the ECG raw signal, the filtered signal, the R peaks indexes, HRV characteristics, all the heartbeats, the Heart Rate, the RSP filtered signal (if respiration provided) and the respiratory sinus arrhythmia (RSA) features.

        This function is mainly a wrapper for the biosppy.ecg.ecg() and the hrv.hrv() functions. Credits go to their authors.

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_ecg = nk.ecg_process(ecg_signal, resp_signal)

    Notes
    ----------
    *Details*

    - **Cardiac Cycle**: A typical ECG showing a heartbeat consists of a P wave, a QRS complex and a T wave.The P wave represents the wave of depolarization that spreads from the SA-node throughout the atria. The QRS complex reflects the rapid depolarization of the right and left ventricles. Since the ventricles are the largest part of the heart, in terms of mass, the QRS complex usually has a much larger amplitude than the P-wave. The T wave represents the ventricular repolarization of the ventricles. On rare occasions, a U wave can be seen following the T wave. The U wave is believed to be related to the last remnants of ventricular repolarization.
    - **RSA**: Respiratory sinus arrhythmia (RSA) is a naturally occurring variation in heart rate that occurs during the breathing cycle, serving as a measure of parasympathetic nervous system activity.
    - **HRV**: Heart-Rate Variability (HRV) is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013). It describes the complex variation of beat-to-beat intervals mainly controlled by the autonomic nervous system (ANS) through the interplay of sympathetic and parasympathetic neural activity at the sinus node. In healthy subjects, the dynamic cardiovascular control system is characterized by its ability to adapt to physiologic perturbations and changing conditions maintaining the cardiovascular homeostasis (Voss, 2015). In general, the HRV is influenced by many several factors like chemical, hormonal and neural modulations, circadian changes, exercise, emotions, posture and preload. There are several procedures to perform HRV analysis, usually classified into three categories: time domain methods, frequency domain methods and non-linear methods.

       - **sdNN** is the standard deviation of the time interval between successive normal heart beats (*i.e.*, the RR intervals). Reflects all influences on HRV including slow influences across the day, circadian variations, the effect of hormonal influences such as cortisol and epinephrine. It should be noted that total variance of HRV increases with the length of the analyzed recording.
       - **mRR** is the mean RR interval.
       - **cvNN**: ratio of sdNN divided by mRR.
       - **RMSSD** is the root mean square of the RR intervals (*i.e.*, square root of the mean of the squared differences in time between successive normal heart beats). Reflects high frequency (fast or parasympathetic) influences on HRV (*i.e.*, those influencing larger changes from one beat to the next).
       - **MADRR**: Median of the Absolute values of the successive Differences between the RR intervals.
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

    - **Adjusted HRV**: The raw HRV features are normalized :math:`(raw - Mcluster) / sd` according to the participant's age and gender. In data from Voss et al. (2015), HRV analysis was performed on 5-min ECG recordings (lead II and lead V2 simultaneously, 500 Hz sample rate) obtained in supine position after a 5–10 minutes resting phase. The cohort of healthy subjects consisted of 782 women and 1124 men between the ages of 25 and 74 years, clustered into 4 groups: YF (Female, Age = [25-49], n=571), YM (Male, Age = [25-49], n=744), EF (Female, Age = [50-74], n=211) and EM (Male, Age = [50-74], n=571).
    - **Systole/Diastole**: One prominent channel of body and brain communication is that conveyed by baroreceptors, pressure and stretch-sensitive receptors within the heart and surrounding arteries. Within each cardiac cycle, bursts of baroreceptor afferent activity encoding the strength and timing of each heartbeat are carried via the vagus and glossopharyngeal nerve afferents to the nucleus of the solitary tract. This is the principal route that communicates to the brain the dynamic state of the heart, enabling the representation of cardiovascular arousal within viscerosensory brain regions, and influence ascending neuromodulator systems implicated in emotional and motivational behaviour. Because arterial baroreceptors are activated by the arterial pulse pressure wave, their phasic discharge is maximal during and immediately after the cardiac systole, that is, when the blood is ejected from the heart, and minimal during cardiac diastole, that is, between heartbeats (Azevedo, 2017).
    - **ECG Signal Quality**: Using the PTB-Diagnostic dataset available from PhysioNet, we extracted all the ECGs signal from the healthy participants. For each ECG, the 15 leads were available. We extracted all cardiac cycles, for each lead, and downsampled them from 600 to 200 datapoints. Note that we dropped the 8 first values that were NaNs. Then, we fitted a neural network on 2/3 of the dataset (that contains 134392 cardiac cycles) to predict the lead. Model evaluation was done on the remaining 1/3. The model show good performances in predicting the correct recording lead (accuracy=0.91, precision=0.91). In this function, this model is fitted on each cardiac cycle. It returns the probable recording lead (the most common predicted lead), the signal quality of each cardiac cycle (the probability of belonging to the probable recording lead) and the overall signal quality (the mean of signal quality).

    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)
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
    ecg_df = pd.DataFrame({"ECG_Raw": np.array(ecg)})

    # Compute several features using biosppy
    biosppy_ecg = dict(biosppy.signals.ecg.ecg(ecg, sampling_rate=sampling_rate, show=False))

    # Filtered signal
    ecg_df["ECG_Filtered"] = biosppy_ecg["filtered"]

    # Store R peaks indexes
    r_peaks = np.array([np.nan]*len(ecg))
    r_peaks[biosppy_ecg['rpeaks']] = 1
    ecg_df["ECG_Rpeaks"] = r_peaks


    # Heart rate index creation
    time_now = datetime.datetime.now()
    # Convert seconds to datetime deltas
    time_index = [datetime.timedelta(seconds=x) for x in biosppy_ecg["heart_rate_ts"]]
    time_index = np.array(time_index) + time_now
    heart_rate = pd.Series(biosppy_ecg["heart_rate"], index=time_index)

    # Create resampling factor
    resampling_rate = str(int(1000/sampling_rate)) + "L"

    # Resample
    if resampling_method == "mean":
        heart_rate = heart_rate.resample(resampling_rate).mean()
    if resampling_method == "pad":
        heart_rate = heart_rate.resample(resampling_rate).pad()
    if resampling_method == "bfill":
        heart_rate = heart_rate.resample(resampling_rate).bfill()

    # Store Heart Rate
    if len(heart_rate) >= len(ecg):
        ecg_df["Heart_Rate"] = np.array(heart_rate[0:len(ecg)])
    else:
        ecg_df["Heart_Rate"] = np.array([heart_rate[-1]]*(len(ecg)-len(heart_rate)) + list(heart_rate))
#        ecg_features["Heart_Rate"] = scipy.signal.resample(heart_rate, len(ecg))  # Looks more badly when resampling with scipy

    # RR intervals (RRis)
    rri = np.diff(biosppy_ecg["rpeaks"])

    # Heartbeats
    heartbeats = pd.DataFrame(biosppy_ecg["templates"]).T
    heartbeats.index = pd.date_range(pd.datetime.today(), periods=len(heartbeats), freq=resampling_rate)

    # Signal quality
    quality = ecg_signal_quality(heartbeats, sampling_rate, quality_model=quality_model)



    # Waves
    waves = ecg_wave_detector(ecg_df["ECG_Filtered"], biosppy_ecg["rpeaks"])

    # Systole
    ecg_df["ECG_Systole"] = ecg_systole(ecg_df["ECG_Filtered"], biosppy_ecg["rpeaks"], waves["T_Waves"])


    # Store results
    processed_ecg = {"df": ecg_df,
                     "ECG": {
                            "RR_Intervals": rri,
                            "Cardiac_Cycles": heartbeats,
                            "R_Peaks": biosppy_ecg["rpeaks"]}
                     }

    processed_ecg["ECG"].update(quality)
    processed_ecg["ECG"].update(waves)

    # HRV
    processed_ecg["ECG"]["HRV"] = ecg_hrv(rri, sampling_rate, segment_length=hrv_segment_length)
    if age is not None and sex is not None and position is not None:
        processed_ecg["ECG"]["HRV_Adjusted"] = ecg_hrv_assessment(processed_ecg["ECG"]["HRV"], age, sex, position)


    # RSP
    if rsp is not None:
        rsp = rsp_process(rsp=rsp, sampling_rate=sampling_rate, resampling_method=resampling_method)
        processed_ecg["RSP"] = rsp["RSP"]
        processed_ecg["df"] = pd.concat([processed_ecg["df"], rsp["df"]], axis=1)

        # RSA
        rpeaks = biosppy_ecg["rpeaks"]
        rsp_cycles = rsp["RSP"]["Cycles_Onsets"]
        rsp_signal = rsp["df"]["RSP_Filtered"]
        rsa = respiratory_sinus_arrhythmia(rpeaks, rsp_cycles, rsp_signal)

        processed_ecg["df"]["RSA"] = rsa["RSA"]

        processed_ecg["ECG"]["RSA"] = {}
        processed_ecg["ECG"]["RSA"]["RSA_Mean"] = rsa["RSA_Mean"]
        processed_ecg["ECG"]["RSA"]["RSA_Variability"] = rsa["RSA_Variability"]
        processed_ecg["ECG"]["RSA"]["RSA_Values"] = rsa["RSA_Values"]


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
def respiratory_sinus_arrhythmia(rpeaks, rsp_cycles, rsp_signal, sampling_rate=1000):
    """
    Returns Respiratory Sinus Arrhythmia (RSA) features.

    Parameters
    ----------
    rpeaks : list or ndarray
        List of R peaks indices.
    rsp_cycles : list or ndarray
        List of respiratory cycles onsets.
    rsp_signal : list or ndarray
        RSP signal.
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

    - Dominique Makowski (https://github.com/DominiqueMakowski)
    - Rhenan Bartels (https://github.com/rhenanbartels)

    *Dependencies*

    - biosppy
    - numpy
    - pandas

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy

    """
    # Find all RSP cycles and the Rpeaks within
    cycles_rri = []
    for idx in range(len(rsp_cycles) - 1):
        cycle_init = rsp_cycles[idx]
        cycle_end = rsp_cycles[idx + 1]
        cycles_rri.append(rpeaks[np.logical_and(rpeaks >= cycle_init,
                                                rpeaks < cycle_end)])

    # Iterate over all cycles
    RSA = []
    for cycle in cycles_rri:
        RRis = np.diff(cycle)/sampling_rate
        if len(RRis) > 1:
            RSA.append(np.max(RRis) - np.min(RRis))
        else:
            RSA.append(np.nan)


    # Continuous RSA
    current_rsa = np.nan

    continuous_rsa = []
    phase_counter = 0
    for i in range(len(rsp_signal)):
        if i == rsp_cycles[phase_counter]:
            current_rsa = RSA[phase_counter]
            if phase_counter < len(rsp_cycles)-2:
                phase_counter += 1
        continuous_rsa.append(current_rsa)

    # Find last phase
    continuous_rsa = np.array(continuous_rsa)
    continuous_rsa[max(rsp_cycles):] = np.nan

    RSA = {"RSA": continuous_rsa,
           "RSA_Values": RSA,
           "RSA_Mean": pd.Series(RSA).mean(),
           "RSA_Variability": pd.Series(RSA).std()}

    return(RSA)


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

    - Dominique Makowski (https://github.com/DominiqueMakowski)

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
def ecg_hrv(rri, sampling_rate=1000, segment_length=60, LF=True, VLF=True):
    """
    Computes the Heart-Rate Variability (HRV). Shamelessly stolen from the `hrv <https://github.com/rhenanbartels/hrv/blob/develop/hrv>`_ package by Rhenan Bartels. All credits go to him.

    Parameters
    ----------
    rri : list or ndarray
        RR intervals.
    sampling_rate : int
        Sampling rate (samples/second).
    segment_length : int
        Number of RR intervals within each sliding window on which to compute frequency-domains power. Particularly important for VLF. Adjust with caution.
    LF : bool
        Computes HRV in the Low Frequency.
    VLF : bool
        Computes HRV in the Very Low Frequency.

    Returns
    ----------
    hrv : dict
        Contains hrv features.

    Example
    ----------
    >>> import neurokit as nk
    >>> hrv = nk.hrv(rri, 1000)

    Notes
    ----------
    *Details*

    - **HRV**: Heart-Rate Variability (HRV) is a finely tuned measure of heart-brain communication, as well as a strong predictor of morbidity and death (Zohar et al., 2013). It describes the complex variation of beat-to-beat intervals mainly controlled by the autonomic nervous system (ANS) through the interplay of sympathetic and parasympathetic neural activity at the sinus node. In healthy subjects, the dynamic cardiovascular control system is characterized by its ability to adapt to physiologic perturbations and changing conditions maintaining the cardiovascular homeostasis (Voss, 2015). In general, the HRV is influenced by many several factors like chemical, hormonal and neural modulations, circadian changes, exercise, emotions, posture and preload. There are several procedures to perform HRV analysis, usually classified into three categories: time domain methods, frequency domain methods and non-linear methods.

       - **sdNN** is the standard deviation of the time interval between successive normal heart beats (*i.e.*, the RR intervals). Reflects all influences on HRV including slow influences across the day, circadian variations, the effect of hormonal influences such as cortisol and epinephrine. It should be noted that total variance of HRV increases with the length of the analyzed recording.
       - **mRR** is the mean RR interval.
       - **cvNN**: ratio of sdNN divided by mRR.
       - **RMSSD** is the root mean square of the RR intervals (*i.e.*, square root of the mean of the squared differences in time between successive normal heart beats). Reflects high frequency (fast or parasympathetic) influences on HRV (*i.e.*, those influencing larger changes from one beat to the next).
       - **MADRR**: Median of the Absolute values of the successive Differences between the RR intervals.
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

    - Dominique Makowski (https://github.com/DominiqueMakowski)
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
    """
    # Resample RRis as if the sampling rate was 1000Hz
    rri = rri*1000/sampling_rate
    rri = rri.astype(float)

    # Preprocessing
    outliers = np.array(identify_outliers(rri, treshold=2.58))
    rri[outliers] = np.nan
    rri = pd.Series(rri).interpolate()

    # Initialize empty dict
    hrv = {}

    # Time Domain
    # ==================
    hrv["RMSSD"] = np.sqrt(np.mean(np.diff(rri) ** 2))
    hrv["mRR"] = np.mean(rri)
    hrv["sdNN"] = np.std(rri, ddof=1)  # make it calculate N-1
    hrv["cvNN"] = hrv["sdNN"] / hrv["mRR"]
    hrv["MADRR"] = np.median(abs(rri))
    nn50 = sum(abs(np.diff(rri)) > 50)
    hrv["pNN50"] = nn50 / len(rri) * 100
    nn20 = sum(abs(np.diff(rri)) > 20)
    hrv["pNN20"] = nn20 / len(rri) * 100

    bin_number = 32  # Initialize bin_width value
    for bin_number_current in range(2, 50):
        bin_width = np.diff(np.histogram(rri, bins=bin_number_current, density=True)[1])[0]
        if abs(8 - bin_width) < abs(8 - np.diff(np.histogram(rri, bins=bin_number, density=True)[1])[0]):
            bin_number = bin_number_current
    hrv["Triang"] = len(rri)/np.max(np.histogram(rri, bins=bin_number, density=True)[0])
    hrv["Shannon_h"] = entropy_shannon(np.histogram(rri, bins=bin_number, density=True)[0])


    # Frequency Domain
    # =================
    # Sanity check
    if segment_length > len(rri):
        print("NeuroKit warning: ecg_hrv(): Number of RR intervals smaller than segment size... setting segment_size to %i." %(len(rri)))
        segment_length = len(rri)

    # Parameters
    vlf_band=(0.003, 0.04)
    lf_band=(0.04, 0.15)
    hf_band=(0.15, 0.40)

    #size = 300, shift = 30, sizesp = 2048
    # Computation
    freq, power = scipy.signal.welch(x=rri, fs=1, window="blackmanharris", nperseg=segment_length, noverlap=segment_length/2, detrend="constant")

    vlf_indexes = np.logical_and(freq >= vlf_band[0], freq < vlf_band[1])
    lf_indexes = np.logical_and(freq >= lf_band[0], freq < lf_band[1])
    hf_indexes = np.logical_and(freq >= hf_band[0], freq < hf_band[1])

    hrv["HF"] = np.trapz(y=power[hf_indexes], x=freq[hf_indexes])

    if LF is True:
        if segment_length >= 20:
            hrv["LF"] = np.trapz(y=power[lf_indexes], x=freq[lf_indexes])
            hrv["LFHF"] = hrv["LF"] / hrv["HF"]
            hrv["LFNU"] = (hrv["LF"] / (hrv["LF"] + hrv["HF"])) * 100
            hrv["HFNU"] = (hrv["HF"] / (hrv["LF"] + hrv["HF"])) * 100
            if VLF is True:
                if segment_length >= 60:
                    hrv["VLF"] = np.trapz(y=power[vlf_indexes], x=freq[vlf_indexes])
                    hrv["Total_Power"] = hrv["VLF"] + hrv["LF"] + hrv["HF"]
                    hrv["HFp"] = hrv["HF"] / hrv["Total_Power"]
                    hrv["LFp"] = hrv["LF"] / hrv["Total_Power"]
                else:
                    print("NeuroKit warning: ecg_hrv(): Segment size too small to compute HRV in the very low frequency (VLF) and the low frequency (LF) domain.")
                    hrv["VLF"] = np.nan
                    hrv["Total_Power"] = np.nan
                    hrv["HFp"] = np.nan
                    hrv["LFp"] = np.nan
        else:
            print("NeuroKit warning: ecg_hrv(): Segment size too small to compute HRV in the low frequency (LF) domain.")
            hrv["VLF"] = np.nan
            hrv["LF"] = np.nan
            hrv["Total_Power"] = np.nan
            hrv["LFHF"] = np.nan
            hrv["LFn"] = np.nan
            hrv["HFn"] = np.nan
            hrv["HFp"] = np.nan
            hrv["LFp"] = np.nan



    # Non-Linear Dynamics
    # ======================
    if len(rri) > 17:
        hrv["DFA_1"] = nolds.dfa(rri, range(4, 17))
    if len(rri) > 66:
        hrv["DFA_2"] = nolds.dfa(rri, range(16, 66))
    hrv["Shannon"] = entropy_shannon(rri)
    hrv["Sample_Entropy"] = nolds.sampen(rri, emb_dim=2)
    hrv["Correlation_Dimension"] = nolds.corr_dim(rri, emb_dim=2)
    hrv["Entropy_Multiscale"] = entropy_multiscale(rri, emb_dim=2)
    hrv["Entropy_SVD"] = entropy_svd(rri, emb_dim=2)
    hrv["Entropy_Spectral_VLF"] = entropy_spectral(rri, 1000, bands=np.arange(0.003, 0.04, 0.001))
    hrv["Entropy_Spectral_LF"] = entropy_spectral(rri, 1000, bands=np.arange(0.04, 0.15, 0.001))
    hrv["Entropy_Spectral_HF"] = entropy_spectral(rri, 1000, bands=np.arange(0.15, 0.40, 0.001))
    hrv["Fisher_Info"] = fisher_info(rri, tau=1, emb_dim=2)
    hrv["Lyapunov"] = np.max(nolds.lyap_e(rri, emb_dim=58, matrix_dim=4))
    hrv["FD_Petrosian"] = fd_petrosian(rri)
    hrv["FD_Higushi"] = fd_higushi(rri, k_max=16)

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

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Details*

    - **Adjusted HRV**: The raw HRV features are normalized :math:`(raw - Mcluster) / sd` according to the participant's age and gender. In data from Voss et al. (2015), HRV analysis was performed on 5-min ECG recordings (lead II and lead V2 simultaneously, 500 Hz sample rate) obtained in supine position after a 5–10 minutes resting phase. The cohort of healthy subjects consisted of 782 women and 1124 men between the ages of 25 and 74 years, clustered into 4 groups: YF (Female, Age = [25-49], n=571), YM (Male, Age = [25-49], n=744), EF (Female, Age = [50-74], n=211) and EM (Male, Age = [50-74], n=571).


    References
    -----------
    - Voss, A., Schroeder, R., Heitmann, A., Peters, A., & Perz, S. (2015). Short-term heart rate variability—influence of gender and age in healthy subjects. PloS one, 10(3), e0118308.
    """
    hrv_adjusted = {}

    if position == "supine":
        if sex == "m":
            if age <= 49:
                hrv_adjusted["mRR_Adjusted"] = (hrv["mRR"]-930)/133
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-45.8)/18.8
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-34.0)/18.3

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-203)/262
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-101)/143
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-3.33)/3.47
            else:
                hrv_adjusted["mRR_Adjusted"] = (hrv["mRR"]-911)/128
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-33.0)/14.8
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-20.5)/11.0

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-84)/115
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-29.5)/36.6
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-4.29)/4.06
        if sex == "f":
            if age <= 49:
                hrv_adjusted["mRR_Adjusted"] = (hrv["mRR"]-901)/117
                hrv_adjusted["sdNN_Adjusted"] = (hrv["sdNN"]-44.9)/19.2
                hrv_adjusted["RMSSD_Adjusted"] = (hrv["RMSSD"]-36.5)/20.1

                hrv_adjusted["LF_Adjusted"] = (hrv["LF"]-159)/181
                hrv_adjusted["HF_Adjusted"] = (hrv["HF"]-125)/147
                hrv_adjusted["LFHF_Adjusted"] = (hrv["LFHF"]-2.75)/2.93
            else:
                hrv_adjusted["mRR_Adjusted"] = (hrv["mRR"]-880)/115
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

    - Dominique Makowski (https://github.com/DominiqueMakowski)






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

    - Dominique Makowski (https://github.com/DominiqueMakowski)

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