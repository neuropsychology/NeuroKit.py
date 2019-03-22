# -*- coding: utf-8 -*-
"""
Subsubmodule for ecg processing.
"""
import numpy as np
import pandas as pd
import biosppy
import scipy


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
def ecg_preprocess(ecg, sampling_rate=1000, filter_type="FIR", filter_band="bandpass", filter_frequency=[3, 45], filter_order=0.3, segmenter="hamilton"):
    """
    ECG signal preprocessing.

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    filter_type : str or None
        Can be Finite Impulse Response filter ("FIR"), Butterworth filter ("butter"), Chebyshev filters ("cheby1" and "cheby2"), Elliptic filter ("ellip") or Bessel filter ("bessel").
    filter_band : str
        Band type, can be Low-pass filter ("lowpass"), High-pass filter ("highpass"), Band-pass filter ("bandpass"), Band-stop filter ("bandstop").
    filter_frequency : int or list
        Cutoff frequencies, format depends on type of band: "lowpass" or "bandpass": single frequency (int), "bandpass" or "bandstop": pair of frequencies (list).
    filter_order : float
        Filter order.
    segmenter : str
        The cardiac phase segmenter. Can be "hamilton", "gamboa", "engzee", "christov", "ssf" or "pekkanen".

    Returns
    ----------
    ecg_preprocessed : dict
        Preprocesed ECG.

    Example
    ----------
    >>> import neurokit as nk
    >>> ecg_preprocessed = nk.ecg_preprocess(signal)

    Notes
    ----------
    *Details*

    - **segmenter**: Different methods of segmentation are implemented: **hamilton** (`Hamilton, 2002 <http://www.eplimited.com/osea13.pdf/>`_) , **gamboa** (`gamboa, 2008 <http://www.lx.it.pt/~afred/pub/thesisHugoGamboa.pdf/>`_), **engzee** (Engelse and Zeelenberg, 1979; Lourenco et al., 2012), **christov** (Christov, 2004) or **ssf** (Slope Sum Function), **pekkanen**  (`Kathirvel, 2001) <http://link.springer.com/article/10.1007/s13239-011-0065-3/fulltext.html>`_.


    *Authors*

    - the bioSSPy dev team (https://github.com/PIA-Group/BioSPPy)
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - biosppy
    - numpy

    *See Also*

    - BioSPPY: https://github.com/PIA-Group/BioSPPy

    References
    -----------
    - Hamilton, P. (2002, September). Open source ECG analysis. In Computers in Cardiology, 2002 (pp. 101-104). IEEE.
    - Kathirvel, P., Manikandan, M. S., Prasanna, S. R. M., & Soman, K. P. (2011). An efficient R-peak detection based on new nonlinear transformation and first-order Gaussian differentiator. Cardiovascular Engineering and Technology, 2(4), 408-425.
    - Canento, F., Lourenço, A., Silva, H., & Fred, A. (2013). Review and Comparison of Real Time Electrocardiogram Segmentation Algorithms for Biometric Applications. In Proceedings of the 6th Int’l Conference on Health Informatics (HEALTHINF).
    - Christov, I. I. (2004). Real time electrocardiogram QRS detection using combined adaptive threshold. Biomedical engineering online, 3(1), 28.
    - Engelse, W. A. H., & Zeelenberg, C. (1979). A single scan algorithm for QRS-detection and feature extraction. Computers in cardiology, 6(1979), 37-42.
    - Lourenço, A., Silva, H., Leite, P., Lourenço, R., & Fred, A. L. (2012, February). Real Time Electrocardiogram Segmentation for Finger based ECG Biometrics. In Biosignals (pp. 49-54).
    """
    # Signal Processing
    # =======================
    # Transform to array
    ecg = np.array(ecg)

    # Filter signal
    if filter_type in ["FIR", "butter", "cheby1", "cheby2", "ellip", "bessel"]:
        order = int(filter_order * sampling_rate)
        filtered, _, _ = biosppy.tools.filter_signal(signal=ecg,
                                          ftype=filter_type,
                                          band=filter_band,
                                          order=order,
                                          frequency=filter_frequency,
                                          sampling_rate=sampling_rate)
    else:
        filtered = ecg  # filtered is not-filtered

    # Segment
    if segmenter == "hamilton":
        rpeaks, = biosppy.ecg.hamilton_segmenter(signal=filtered, sampling_rate=sampling_rate)
    elif segmenter == "gamboa":
        rpeaks, = biosppy.ecg.gamboa_segmenter(signal=filtered, sampling_rate=sampling_rate, tol=0.002)
    elif segmenter == "engzee":
        rpeaks, = biosppy.ecg.engzee_segmenter(signal=filtered, sampling_rate=sampling_rate, threshold=0.48)
    elif segmenter == "christov":
        rpeaks, = biosppy.ecg.christov_segmenter(signal=filtered, sampling_rate=sampling_rate)
    elif segmenter == "ssf":
        rpeaks, = biosppy.ecg.ssf_segmenter(signal=filtered, sampling_rate=sampling_rate, threshold=20, before=0.03, after=0.01)
    elif segmenter == "pekkanen":
        rpeaks = segmenter_pekkanen(ecg=filtered, sampling_rate=sampling_rate, window_size=5.0, lfreq=5.0, hfreq=15.0)
    else:
        raise ValueError("Unknown segmenter: %s." % segmenter)


    # Correct R-peak locations
    rpeaks, = biosppy.ecg.correct_rpeaks(signal=filtered,
                             rpeaks=rpeaks,
                             sampling_rate=sampling_rate,
                             tol=0.05)

    # Extract cardiac cycles and rpeaks
    cardiac_cycles, rpeaks = biosppy.ecg.extract_heartbeats(signal=filtered,
                                           rpeaks=rpeaks,
                                           sampling_rate=sampling_rate,
                                           before=0.2,
                                           after=0.4)

    # Compute heart rate
    heart_rate_idx, heart_rate = biosppy.tools.get_heart_rate(beats=rpeaks,
                                   sampling_rate=sampling_rate,
                                   smooth=True,
                                   size=3)

    # Get time indices
    length = len(ecg)
    T = (length - 1) / float(sampling_rate)
    ts = np.linspace(0, T, length, endpoint=False)
    heart_rate_times = ts[heart_rate_idx]
    heart_rate_times = np.round(heart_rate_times*sampling_rate).astype(int)  # Convert heart rate times to timepoints

    # what for is this line in biosppy??
#    cardiac_cycles_tmpl = np.linspace(-0.2, 0.4, cardiac_cycles.shape[1], endpoint=False)

    # Prepare Output Dataframe
    # ==========================
    ecg_df = pd.DataFrame({"ECG_Raw": np.array(ecg)})  # Create a dataframe
    ecg_df["ECG_Filtered"] = filtered  # Add filtered signal

    # Add R peaks
    rpeaks_signal = np.array([np.nan]*len(ecg))
    rpeaks_signal[rpeaks] = 1
    ecg_df["ECG_R_Peaks"] = rpeaks_signal


    # Heart Rate
    try:
        heart_rate = interpolate(heart_rate, heart_rate_times, sampling_rate)  # Interpolation using 3rd order spline
        ecg_df["Heart_Rate"] = heart_rate
    except TypeError:
        print("NeuroKit Warning: ecg_process(): Sequence too short to compute heart rate.")
        ecg_df["Heart_Rate"] = np.nan

    # Store Additional Feature
    # ========================
    processed_ecg = {"df": ecg_df,
                     "ECG": {
                            "R_Peaks": rpeaks
                            }
                     }

    # Heartbeats
    heartbeats = pd.DataFrame(cardiac_cycles).T
    heartbeats.index = pd.date_range(pd.datetime.today(), periods=len(heartbeats), freq=str(int(1000000/sampling_rate)) + "us")
    processed_ecg["ECG"]["Cardiac_Cycles"] = heartbeats

    # Waves
    waves = ecg_wave_detector(ecg_df["ECG_Filtered"], rpeaks)
    processed_ecg["ECG"].update(waves)

    # Systole
    processed_ecg["df"]["ECG_Systole"] = ecg_systole(ecg_df["ECG_Filtered"], rpeaks, waves["T_Waves_Ends"])


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
    rpeaks, = biosppy.ecg.hamilton_segmenter(np.array(signal), sampling_rate=sampling_rate)
    rpeaks, = biosppy.ecg.correct_rpeaks(signal=np.array(signal), rpeaks=rpeaks, sampling_rate=sampling_rate, tol=0.05)
    return(rpeaks)






# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_wave_detector(ecg, rpeaks):
    """
    Returns the localization of the P, Q, T waves. This function needs massive help!

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal (preferably filtered).
    rpeaks : list or ndarray
        R peaks localization.

    Returns
    ----------
    ecg_waves : dict
        Contains wave peaks location indices.

    Example
    ----------
    >>> import neurokit as nk
    >>> ecg =  nk.ecg_simulate(duration=5, sampling_rate=1000)
    >>> ecg = nk.ecg_preprocess(ecg=ecg, sampling_rate=1000)
    >>> rpeaks = ecg["ECG"]["R_Peaks"]
    >>> ecg = ecg["df"]["ECG_Filtered"]
    >>> ecg_waves = nk.ecg_wave_detector(ecg=ecg, rpeaks=rpeaks)
    >>> nk.plot_events_in_signal(ecg, [ecg_waves["P_Waves"], ecg_waves["Q_Waves_Onsets"], ecg_waves["Q_Waves"], list(rpeaks), ecg_waves["S_Waves"], ecg_waves["T_Waves_Onsets"], ecg_waves["T_Waves"], ecg_waves["T_Waves_Ends"]], color=["green", "yellow", "orange", "red", "black", "brown", "blue", "purple"])

    Notes
    ----------
    *Details*

    - **Cardiac Cycle**: A typical ECG showing a heartbeat consists of a P wave, a QRS complex and a T wave.The P wave represents the wave of depolarization that spreads from the SA-node throughout the atria. The QRS complex reflects the rapid depolarization of the right and left ventricles. Since the ventricles are the largest part of the heart, in terms of mass, the QRS complex usually has a much larger amplitude than the P-wave. The T wave represents the ventricular repolarization of the ventricles. On rare occasions, a U wave can be seen following the T wave. The U wave is believed to be related to the last remnants of ventricular repolarization.

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    """
    q_waves = []
    p_waves = []
    q_waves_starts = []
    s_waves = []
    t_waves = []
    t_waves_starts = []
    t_waves_ends = []
    for index, rpeak in enumerate(rpeaks[:-3]):

        try:
            epoch_before = np.array(ecg)[int(rpeaks[index-1]):int(rpeak)]
            epoch_before = epoch_before[int(len(epoch_before)/2):len(epoch_before)]
            epoch_before = list(reversed(epoch_before))

            q_wave_index = np.min(find_peaks(epoch_before))
            q_wave = rpeak - q_wave_index
            p_wave_index = q_wave_index + np.argmax(epoch_before[q_wave_index:])
            p_wave = rpeak - p_wave_index

            inter_pq = epoch_before[q_wave_index:p_wave_index]
            inter_pq_derivative = np.gradient(inter_pq, 2)
            q_start_index = find_closest_in_list(len(inter_pq_derivative)/2, find_peaks(inter_pq_derivative))
            q_start = q_wave - q_start_index

            q_waves.append(q_wave)
            p_waves.append(p_wave)
            q_waves_starts.append(q_start)
        except ValueError:
            pass
        except IndexError:
            pass

        try:
            epoch_after = np.array(ecg)[int(rpeak):int(rpeaks[index+1])]
            epoch_after = epoch_after[0:int(len(epoch_after)/2)]

            s_wave_index = np.min(find_peaks(epoch_after))
            s_wave = rpeak + s_wave_index
            t_wave_index = s_wave_index + np.argmax(epoch_after[s_wave_index:])
            t_wave = rpeak + t_wave_index

            inter_st = epoch_after[s_wave_index:t_wave_index]
            inter_st_derivative = np.gradient(inter_st, 2)
            t_start_index = find_closest_in_list(len(inter_st_derivative)/2, find_peaks(inter_st_derivative))
            t_start = s_wave + t_start_index
            t_end = np.min(find_peaks(epoch_after[t_wave_index:]))
            t_end = t_wave + t_end

            s_waves.append(s_wave)
            t_waves.append(t_wave)
            t_waves_starts.append(t_start)
            t_waves_ends.append(t_end)
        except ValueError:
            pass
        except IndexError:
            pass

# pd.Series(epoch_before).plot()
#    t_waves = []
#    for index, rpeak in enumerate(rpeaks[0:-1]):
#
#        epoch = np.array(ecg)[int(rpeak):int(rpeaks[index+1])]
#        pd.Series(epoch).plot()
#
#        # T wave
#        middle = (rpeaks[index+1] - rpeak) / 2
#        quarter = middle/2
#
#        epoch = np.array(ecg)[int(rpeak+quarter):int(rpeak+middle)]
#
#        try:
#            t_wave = int(rpeak+quarter) + np.argmax(epoch)
#            t_waves.append(t_wave)
#        except ValueError:
#            pass
#
#    p_waves = []
#    for index, rpeak in enumerate(rpeaks[1:]):
#        index += 1
#        # Q wave
#        middle = (rpeak - rpeaks[index-1]) / 2
#        quarter = middle/2
#
#        epoch = np.array(ecg)[int(rpeak-middle):int(rpeak-quarter)]
#
#        try:
#            p_wave = int(rpeak-quarter) + np.argmax(epoch)
#            p_waves.append(p_wave)
#        except ValueError:
#            pass
#
#    q_waves = []
#    for index, p_wave in enumerate(p_waves):
#        epoch = np.array(ecg)[int(p_wave):int(rpeaks[rpeaks>p_wave][0])]
#
#        try:
#            q_wave = p_wave + np.argmin(epoch)
#            q_waves.append(q_wave)
#        except ValueError:
#            pass
#
#    # TODO: manage to find the begininng of the Q and the end of the T wave so we can extract the QT interval


    ecg_waves = {"T_Waves": t_waves,
                 "P_Waves": p_waves,
                 "Q_Waves": q_waves,
                 "S_Waves": s_waves,
                 "Q_Waves_Onsets": q_waves_starts,
                 "T_Waves_Onsets": t_waves_starts,
                 "T_Waves_Ends": t_waves_ends}
    return(ecg_waves)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def ecg_systole(ecg, rpeaks, t_waves_ends):
    """
    Returns the localization of systoles and diastoles.

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal (preferably filtered).
    rpeaks : list or ndarray
        R peaks localization.
    t_waves_ends : list or ndarray
        T waves localization.

    Returns
    ----------
    systole : ndarray
        Array indicating where systole (1) and diastole (0).

    Example
    ----------
    >>> import neurokit as nk
    >>> systole = nk.ecg_systole(ecg, rpeaks, t_waves_ends)

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

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
    waves[t_waves_ends] = "T"

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
def segmenter_pekkanen(ecg, sampling_rate, window_size=5.0, lfreq=5.0, hfreq=15.0):
    """
    ECG R peak detection based on `Kathirvel et al. (2001) <http://link.springer.com/article/10.1007/s13239-011-0065-3/fulltext.html>`_ with some tweaks (mainly robust estimation of the rectified signal cutoff threshold).

    Parameters
    ----------
    ecg : list or ndarray
        ECG signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    window_size : float
        Ransac window size.
    lfreq : float
        Low frequency of the band pass filter.
    hfreq : float
        High frequency of the band pass filter.

    Returns
    ----------
    rpeaks : ndarray
        R peaks location.

    Example
    ----------
    >>> import neurokit as nk
    >>> rpeaks = nk.segmenter_pekkanen(ecg_signal, 1000)

    *Authors*

    - `Jami Pekkanen <https://github.com/jampekka>`_
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - scipy
    - numpy

    *See Also*

    - rpeakdetect: https://github.com/tru-hy/rpeakdetect
    """

    window_size = int(window_size*sampling_rate)

    lowpass = scipy.signal.butter(1, hfreq/(sampling_rate/2.0), 'low')
    highpass = scipy.signal.butter(1, lfreq/(sampling_rate/2.0), 'high')

    # TODO: Could use an actual bandpass filter
    ecg_low = scipy.signal.filtfilt(*lowpass, x=ecg)
    ecg_band = scipy.signal.filtfilt(*highpass, x=ecg_low)

    # Square (=signal power) of the first difference of the signal
    decg = np.diff(ecg_band)
    decg_power = decg**2

    # Robust threshold and normalizator estimation
    thresholds = []
    max_powers = []
    for i in range(int(len(decg_power)/window_size)):
        sample = slice(i*window_size, (i+1)*window_size)
        d = decg_power[sample]
        thresholds.append(0.5*np.std(d))
        max_powers.append(np.max(d))

    threshold = 0.5*np.std(decg_power)
    threshold = np.median(thresholds)
    max_power = np.median(max_powers)
    decg_power[decg_power < threshold] = 0

    decg_power = decg_power/max_power
    decg_power[decg_power > 1.0] = 1.0
    square_decg_power = decg_power**2

#    shannon_energy = -square_decg_power*np.log(square_decg_power)  # This errors
#    shannon_energy[np.where(np.isfinite(shannon_energy) == False)] = 0.0
    shannon_energy = -square_decg_power*np.log(square_decg_power.clip(min=1e-6))
    shannon_energy[np.where(shannon_energy <= 0)] = 0.0


    mean_window_len = int(sampling_rate*0.125+1)
    lp_energy = np.convolve(shannon_energy, [1.0/mean_window_len]*mean_window_len, mode='same')
    #lp_energy = scipy.signal.filtfilt(*lowpass2, x=shannon_energy)

    lp_energy = scipy.ndimage.gaussian_filter1d(lp_energy, sampling_rate/8.0)
    lp_energy_diff = np.diff(lp_energy)

    rpeaks = (lp_energy_diff[:-1] > 0) & (lp_energy_diff[1:] < 0)
    rpeaks = np.flatnonzero(rpeaks)
    rpeaks -= 1

    return(rpeaks)