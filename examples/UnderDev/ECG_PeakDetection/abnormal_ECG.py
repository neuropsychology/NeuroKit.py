import neurokit as nk

df = nk.read_acqknowledge("abnormal_ECG.acq")

events = nk.find_events(df["Photosensor"], cut="lower")
df = nk.create_epochs(df, events["onsets"], duration=events["durations"])[0]



#df["Photosensor"].plot()

rpeaks = nk.ecg_find_peaks(df['ECG, X, RSPEC-R'])
nk.visually_check_events_in_signal()
#df['ECG, X, RSPEC-R'].iloc[104000:140000].plot()
