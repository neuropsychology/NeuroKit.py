# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from .bio_ecg import *
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
def bio_process(ecg=None, rsp=None, eda=None, emg=None, sampling_rate=1000, age=None, sex=None, position=None, resampling_method="bfill", ecg_quality_model="default", hrv_segment_length=60, use_cvxEDA=True, add=None, emg_names=None, scr_min_amplitude=0.1):
    """
    Automated processing of bio signals. Wrapper function for :func:`neurokit.ecg_process()` and :func:`neurokit.eda_process()`.

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
    sampling_rate : int
        Sampling rate (samples/second).
    age : float
        Subject's age.
    sex : str
        Subject's gender ("m" or "f").
    position : str
        Recording position. To compare with data from Voss et al. (2015), use "supine".
    resampling_method : str
        "mean", "pad" or "bfill", the resampling method used for ECG and RSP heart rate.
    ecg_quality_model : str
        Path to model used to check signal quality. "default" uses the builtin model.
    hrv_segment_length : int
        Number of RR intervals within each sliding window on which to compute frequency-domains power. Particularly important for VLF. Adjust with caution.
    use_cvxEDA : bool
        Use convex optimization (CVXEDA) described in "cvxEDA: a Convex Optimization Approach to Electrodermal Activity Processing" (Greco et al., 2015).
    add : pandas.DataFrame
        Dataframe or channels to add by concatenation to the processed dataframe.
    emg_names : list
        List of EMG channel names.
    scr_min_amplitude : float
        Minimum treshold by which to exclude Skin Conductance Responses (SCRs).

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
    - **cvxEDA**: Based on a model which describes EDA as the sum of three terms: the phasic component, the tonic component, and an additive white Gaussian noise term incorporating model prediction errors as well as measurement errors and artifacts. This model is physiologically inspired and fully explains EDA through a rigorous methodology based on Bayesian statistics, mathematical convex optimization and sparsity.


    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

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
    """
    processed_bio = {}
    bio_df = pd.DataFrame({})

    # ECG & RSP
    if ecg is not None:
        ecg = ecg_process(ecg=ecg, rsp=rsp, sampling_rate=sampling_rate, resampling_method=resampling_method, quality_model=ecg_quality_model, hrv_segment_length=hrv_segment_length, age=age, sex=sex, position=position)
        processed_bio["ECG"] = ecg["ECG"]
        if rsp is not None:
            processed_bio["RSP"] = ecg["RSP"]
        bio_df = pd.concat([bio_df, ecg["df"]], axis=1)

    if rsp is not None and ecg is None:
        rsp = rsp_process(rsp=rsp, sampling_rate=sampling_rate, resampling_method=resampling_method)
        processed_bio["RSP"] = rsp["RSP"]
        bio_df = pd.concat([bio_df, rsp["df"]], axis=1)


    # EDA
    if eda is not None:
        eda = eda_process(eda=eda, sampling_rate=sampling_rate, use_cvxEDA=use_cvxEDA, scr_min_amplitude=scr_min_amplitude)
        processed_bio["EDA"] = eda["EDA"]
        bio_df = pd.concat([bio_df, eda["df"]], axis=1)

    # EMG
    if emg is not None:
        emg = emg_process(emg=emg, sampling_rate=sampling_rate, emg_names=emg_names)
        bio_df = pd.concat([bio_df, emg.pop("df")], axis=1)
        for i in emg:
            processed_bio[i] = emg[i]


    if add is not None:
        add = add.reset_index(drop=True)
        bio_df = pd.concat([bio_df, add], axis=1)
    processed_bio["df"] = bio_df

    return(processed_bio)



