import numpy as np
import pandas as pd
import neurokit as nk
import matplotlib.pyplot as plt
import scipy
import biosppy
import mne
import seaborn as sns




df = pd.read_csv("https://raw.githubusercontent.com/neuropsychology/NeuroKit.py/master/examples/Bio/bio_100Hz.csv")
ecg=df["ECG"]
rsp=df["RSP"]
sampling_rate=100
df = nk.ecg_process(ecg=df["ECG"], rsp=df["RSP"], sampling_rate=100)

rpeaks = df["ECG"]["R_Peaks"]
dfhrv = df["ECG"]["HRV"]["df"]
dfhrv.plot()
#sampling_rate=100
#df["df"].plot()
#rpeaks = df["ECG"]["R_Peaks"]

#
#rri = df["ECG_RR_Interval"]
#rri = rri.dropna()
##df.plot()
#
#fbands = {
#      "ULF": [0.0001, 0.0033],
#      "VLF": [0.0033, 0.04],
#      "LF": [0.04, 0.15],
#      "HF": [0.15, 0.40],
#      "VHF": [0.4, 0.5]
#      }
#
#power, freq = mne.time_frequency.psd_array_multitaper(rri, sfreq=100, fmin=0, fmax=0.5,  adaptive=False, normalization='length')
#
#freq, power = biosppy.signals.tools.power_spectrum(signal=rri, sampling_rate=sampling_rate)
#plt.plot(freq,power)
#
#tf = {}
#for band in fbands:
#    freqs = fbands[band]
#
#    filtered, sampling_rate, params = biosppy.signals.tools.filter_signal(signal=rri, ftype='butter', band='bandpass', order=1, frequency=freqs, sampling_rate=sampling_rate)
#    amplitude, phase = biosppy.signals.tools.analytic_signal(filtered)
#
#    tf[band] = amplitude
#
#
#
#tf = pd.DataFrame.from_dict(tf)
#tf["RRi"] = rri.values
#nk.z_score(tf).plot()
#
#
#import numpy as np
#import pandas as pd
#import mne
#import scipy
#import biosppy
#import neurokit as nk
#import matplotlib.pyplot as plt
#signal = pd.read_csv("signal_100Hz.txt")["Signal"]
#sampling_rate=100
#
## Set frequencies with variable step to have approximately the same amount of values in each band
#fbands = {
##      "ULF": [0, 0.0033],
#      "VLF": [0.0033, 0.04],
##      "LF": [0.04, 0.15],
#      "HF": [0.15, 0.42]
##      "VHF": np.arange(0.4, 0.51, 0.01)
#      }
#
#
#
#freqs, power = biosppy.signals.tools.power_spectrum(signal=signal, sampling_rate=sampling_rate, pad=2)
#
#plt.plot(freqs, power)
#biosppy.signals.tools.filter_signal(signal=None, ftype='FIR', band='lowpass',
#
# Initialize empty dict
#    hrv = {}
#
#    # Preprocessing
#    # ==================
#    # Extract RR intervals (RRis)
#    RRis = np.diff(rpeaks)
#    # Basic resampling to 1Hz to standardize the scale
#    RRis = RRis/sampling_rate
#    RRis = RRis.astype(float)
#
#
#    # Artifact detection - Statistical
#    for index, rr in enumerate(RRis):
#        # Remove RR intervals that differ more than 25% from the previous one
#        if RRis[index] < RRis[index-1]*0.75:
#            RRis[index] = np.nan
#        if RRis[index] > RRis[index-1]*1.25:
#            RRis[index] = np.nan
#
#    # Artifact detection - Physiological (http://emedicine.medscape.com/article/2172196-overview)
#    RRis = pd.Series(RRis)
#    RRis[RRis < 0.6] = np.nan
#    RRis[RRis > 1.3] = np.nan
#
#    # Artifacts treatment
#    hrv["n_Artifacts"] = pd.isnull(RRis).sum()/len(RRis)
#    artifacts_indices = RRis.index[RRis.isnull()]  # get the artifacts indices
#    RRis = RRis.drop(artifacts_indices)  # remove the artifacts
#
#    # Convert to continuous RR interval (RRi)
#    beats_times = rpeaks[1:]  # the time at which each beat occured starting from the 2nd beat
#    beats_times -= beats_times[0]
#    beats_times = np.delete(beats_times, artifacts_indices)  # delete also the artifact beat moments
#    try:
#        RRi = discrete_to_continuous(RRis, beats_times, sampling_rate)  # Interpolation using 3rd order spline
#    except TypeError:
#        print("NeuroKit Warning: ecg_hrv(): Sequence too short to compute HRV.")
#        return(hrv)
#
#
#    # Rescale to 1000Hz
#    RRis = RRis*1000
#    RRi = RRi*1000
#    hrv["RR_Intervals"] = RRis  # Values of RRis
#    hrv["df"] = RRi.to_frame("ECG_RR_Interval")  # Continuous (interpolated) signal of RRi
#
#    # Time Domain
#    # ==================
#    hrv["RMSSD"] = np.sqrt(np.mean(np.diff(RRis) ** 2))
#    hrv["meanNN"] = np.mean(RRis)
#    hrv["sdNN"] = np.std(RRis, ddof=1)  # make it calculate N-1
#    hrv["cvNN"] = hrv["sdNN"] / hrv["meanNN"]
#    hrv["CVSD"] = hrv["RMSSD"] / hrv["meanNN"] * 100
#    hrv["medianNN"] = np.median(abs(RRis))
#    hrv["madNN"] = mad(RRis, constant=1)
#    hrv["mcvNN"] = hrv["madNN"] / hrv["medianNN"]
#    nn50 = sum(abs(np.diff(RRis)) > 50)
#    hrv["pNN50"] = nn50 / len(RRis) * 100
#    nn20 = sum(abs(np.diff(RRis)) > 20)
#    hrv["pNN20"] = nn20 / len(RRis) * 100
#
#    # Geometrical Method
#    # ====================
#    # TODO: This part needs to be checked by an expert. Also, it would be better to have Renyi entropy (a generalization of shannon's), but I don't know how to compute it.
#    try:
#        bin_number = 32  # Initialize bin_width value
#        # find the appropriate number of bins so the class width is approximately 8 ms (Voss, 2015)
#        for bin_number_current in range(2, 50):
#            bin_width = np.diff(np.histogram(RRi, bins=bin_number_current, density=True)[1])[0]
#            if abs(8 - bin_width) < abs(8 - np.diff(np.histogram(RRi, bins=bin_number, density=True)[1])[0]):
#                bin_number = bin_number_current
#        hrv["Triang"] = len(RRis)/np.max(np.histogram(RRi, bins=bin_number, density=True)[0])
#        hrv["Shannon_h"] = entropy_shannon(np.histogram(RRi, bins=bin_number, density=True)[0])
#    except ValueError:
#        hrv["Triang"] = np.nan
#        hrv["Shannon_h"] = np.nan
#
#
#    # Frequency Domain
#    # =================
#    freq_bands = {
#      "ULF": [0.0001, 0.0033],
#      "VLF": [0.0033, 0.04],
#      "LF": [0.04, 0.15],
#      "HF": [0.15, 0.40],
#      "VHF": [0.4, 0.5]}
#
#
#    # Frequency-Domain Power over Time
#    freq_powers = {}
#    for band in freq_bands:
#        freqs = freq_bands[band]
#        # Filter to keep only the band of interest
#        filtered, sampling_rate, params = biosppy.signals.tools.filter_signal(signal=RRi, ftype='butter', band='bandpass', order=1, frequency=freqs, sampling_rate=sampling_rate)
#        # Apply Hilbert transform
#        amplitude, phase = biosppy.signals.tools.analytic_signal(filtered)
#        # Extract Amplitude of Envolope (power)
#        freq_powers["ECG_HRV_" + band] = amplitude
#
#    freq_powers = pd.DataFrame.from_dict(freq_powers)
#    freq_powers.index = hrv["df"].index
#    hrv["df"] = pd.concat([hrv["df"], freq_powers])
#
#
#    # Compute Power Spectral Density (PSD) using multitaper method
#    power, freq = mne.time_frequency.psd_array_multitaper(RRi, sfreq=sampling_rate, fmin=0, fmax=0.5,  adaptive=False, normalization='length')
#
#    def power_in_band(power, freq, band):
#        power =  np.trapz(y=power[(freq >= band[0]) & (freq < band[1])], x=freq[(freq >= band[0]) & (freq < band[1])])
#        return(power)
#
#    # Extract Power according to frequency bands
#    hrv["ULF"] = power_in_band(power, freq, freq_bands["ULF"])
#    hrv["VLF"] = power_in_band(power, freq, freq_bands["VLF"])
#    hrv["LF"] = power_in_band(power, freq, freq_bands["LF"])
#    hrv["HF"] = power_in_band(power, freq, freq_bands["HF"])
#    hrv["VHF"] = power_in_band(power, freq, freq_bands["VHF"])
#    hrv["Total_Power"] = power_in_band(power, freq, [0, 0.5])
#
#    hrv["LFn"] = hrv["LF"]/(hrv["LF"]+hrv["HF"])
#    hrv["HFn"] = hrv["HF"]/(hrv["LF"]+hrv["HF"])
#    hrv["LF/HF"] = hrv["LF"]/hrv["HF"]
#    hrv["LF/P"] = hrv["LF"]/hrv["Total_Power"]
#    hrv["HF/P"] = hrv["HF"]/hrv["Total_Power"]
#
#
#    # TODO: THIS HAS TO BE CHECKED BY AN EXPERT - Should it be applied on the interpolated on raw RRis?
#    # Non-Linear Dynamics
#    # ======================
#    if len(RRis) > 17:
#        hrv["DFA_1"] = nolds.dfa(RRis, range(4, 17))
#    if len(RRis) > 66:
#        hrv["DFA_2"] = nolds.dfa(RRis, range(16, 66))
#    hrv["Shannon"] = entropy_shannon(RRis)
#    hrv["Sample_Entropy"] = nolds.sampen(RRis, emb_dim=2)
#    try:
#        hrv["Correlation_Dimension"] = nolds.corr_dim(RRis, emb_dim=2)
#    except AssertionError as error:
#        print("NeuroKit Warning: ecg_hrv(): Correlation Dimension. Error: " + str(error))
#        hrv["Correlation_Dimension"] = np.nan
#    hrv["Entropy_Multiscale"] = entropy_multiscale(RRis, emb_dim=2)
#    hrv["Entropy_SVD"] = entropy_svd(RRis, emb_dim=2)
#    hrv["Entropy_Spectral_VLF"] = entropy_spectral(RRis, sampling_rate, bands=np.arange(0.0033, 0.04, 0.001))
#    hrv["Entropy_Spectral_LF"] = entropy_spectral(RRis, sampling_rate, bands=np.arange(0.04, 0.15, 0.001))
#    hrv["Entropy_Spectral_HF"] = entropy_spectral(RRis, sampling_rate, bands=np.arange(0.15, 0.40, 0.001))
#    hrv["Fisher_Info"] = fisher_info(RRis, tau=1, emb_dim=2)
#    try:  # Otherwise travis errors for some reasons :(
#        hrv["Lyapunov"] = np.max(nolds.lyap_e(RRis, emb_dim=58, matrix_dim=4))
#    except Exception:
#        hrv["Lyapunov"] = np.nan
#    hrv["FD_Petrosian"] = fd_petrosian(RRis)
#    hrv["FD_Higushi"] = fd_higushi(RRis, k_max=16)
#
#    # TO DO:
#    # Include many others (see Voss 2015)
#
#    return(hrv)
#
#
#tf = {}
#for band in fbands:
#    freqs = fbands[band]
#    amplitude, phase = biosppy.signals.tools.analytic_signal(signal)
##    filtered = mne.filter.filter_data(np.array([[signal]]), sfreq=sampling_rate, l_freq=freqs[0], h_freq=freqs[1], method="fir", verbose="CRITICAL")[0][0]
##    analytic = scipy.signal.hilbert(filtered)
##    amplitude_envelope = np.abs(analytic)
##    instantaneous_phase = np.unwrap(np.angle(analytic))
##    instantaneous_frequency = (np.diff(instantaneous_phase) / (2.0*np.pi) * sampling_rate)
#
#
##    tf[band + "_Signal"] = filtered
#    tf[band + "_Amplitude"] = amplitude
#    tf[band + "_Phase"] = phase
#
#
##    freqs = tf[freqs_range]
##    signal = mne.time_frequency.tfr_array_multitaper(np.array([[signal]]), sampling_rate, freqs, n_cycles=freqs/2, zero_mean=False, time_bandwidth=7)[0][0]
##    signal = np.mean(signal, 0)  # Average
##    tf[freqs_range] = signal  # Replace data in dict
#
#tf = pd.DataFrame.from_dict(tf)
#tf["Raw_Signal"] = signal
#nk.z_score(tf).plot()
#
#
##
##
#
#
#

#
#
#
##df = pd.read_csv('normal_ECG.csv')
##df = df.loc[10000:100000].reset_index(drop=True)  # Select 10s of signal
#sampling_rate=100
#ecg=df["ECG"]
#
#
#df = nk.ecg_process(ecg=ecg, sampling_rate=100)["df"]
#df["ECG_RR_Interval"].to_csv("signal_100Hz.txt", index=False)
#
#rri = df["ECG_RR_Interval"]
#rri = rri.dropna()
#
#signal = pd.read_csv("signal_100Hz.txt")
#sampling_rate=100
## Set frequencies with variable step to have approximately the same amount of values in each band
#tf = {"ULF": np.arange(0.0001, 0.0033, 0.001),
#      "VLF": np.arange(0.0033, 0.045, 0.005),
#      "LF": np.arange(0.04, 0.16, 0.01),
#      "HF": np.arange(0.15, 0.42, 0.02),
#      "VHF": np.arange(0.4, 0.51, 0.01)}
#
#
#for freqs_range in tf:
#    freqs = tf[freqs_range]*1000
#    signal = mne.time_frequency.tfr_array_multitaper(np.array([[signal]]), sampling_rate, freqs, n_cycles=freqs/2, zero_mean=False, time_bandwidth=7)[0][0]
#    signal = np.mean(signal, 0)
#    tf[freqs_range] = signal
#
#tf = pd.DataFrame.from_dict(tf)
#tf["RRI"] = signal
#nk.z_score(tf).plot()
#
#tf_HF = mne.time_frequency.tfr_array_morlet(np.array([[rri]]), 100, np.arange(0.15, 0.42, 0.2 ), n_cycles=np.arange(0.15, 0.42, 0.2)/2)[0][0]
#tf_LF = mne.time_frequency.tfr_array_morlet(np.array([[rri]]), 100, np.arange(0.04, 0.16, 0.1), n_cycles=np.arange(0.04, 0.16, 0.1)/2)[0][0]
#tf_LF = np.mean(tf_LF, 0)
#tf_HF = np.mean(tf_HF, 0)
###tf_HF20 = np.mean(tf_HF20, 0)
###
###
#pd.Series(tf_LF).plot()
#pd.Series(tf_HF).plot()
#pd.Series(tf_HF20).plot()
#pd.Series(rri).plot()
#hrv["VLF"] = power_in_band(power, freq, 0.0033, 0.04)
#hrv["LF"] = power_in_band(power, freq, 0.04, 0.15)
#hrv["HF"] = power_in_band(power, freq, 0.15, 0.4)
#hrv["VHF"] = power_in_band(power, freq, 0.4, 0.5)



#tfr = pd.DataFrame(tfr)
#tfr.plot()
#len(pd.Series(tfr[])).plot()
#
#sns.heatmap(tfr)


#rsp=dict(biosppy.resp.resp(df["RSP"], sampling_rate, show=False))["filtered"]
#rpeaks = dict(biosppy.ecg.ecg(ecg, sampling_rate, show=False))["rpeaks"]
#
#
#bio = nk.bio_process(ecg=df["ECG"], rsp=df["RSP"], sampling_rate=1000)
##rsa_interpolated = nk.discrete_to_continuous(values=np.array(bio["ECG"]["RSA"]["RSA_P2T_Values"]), value_times=bio["ECG"]["RSA"]["value_times"], sampling_rate=sampling_rate)
##rsp = pd.Series(dict(biosppy.resp.resp(rsp, 100, show=False))["filtered"])
#bio["df"].plot()
#
##nk.plot_events_in_signal(rsp, rsp_onsets)
##nk.z_score(df).plot()
#
