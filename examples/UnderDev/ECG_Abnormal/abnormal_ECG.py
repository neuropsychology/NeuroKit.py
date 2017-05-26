import neurokit as nk

df = nk.read_acqknowledge("abnormal_ECG.acq")
df['ECG, X, RSPEC-R'].plot()


#events = nk.find_events(df["Photosensor"], cut="lower")
#df = nk.create_epochs(df, events["onsets"], duration=events["durations"])[0]



#df["Photosensor"].plot()
#df = nk.ecg_process(df['ECG, X, RSPEC-R'])
#ecg = df["ECG"]
#df = df["df"]
#rpeaks = nk.ecg_find_peaks(df['ECG_Filtered'])
#nk.plot_events_in_signal(df['ECG_Filtered'], ecg["R_Peaks"])
#df['ECG, X, RSPEC-R'].iloc[104000:140000].plot()
