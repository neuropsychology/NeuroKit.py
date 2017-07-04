import neurokit as nk


# Read data
df = nk.read_acqknowledge("data_bio.acq")
# Resample to 50Hz
df = df.resample("10L").mean()
df.columns = ['ECG', 'EDA', 'PPG', 'Photosensor', 'RSP']
df = df.drop(["PPG"], axis=1)

#nk.z_score(df[102000:122000][["EDA", "Photosensor"]]).plot()
df = df[105000:122000]
df.plot()


sampling_rate=100
bio = nk.bio_process(ecg=df['ECG'], rsp=df['RSP'], eda=df['EDA'], add=df['Photosensor'], sampling_rate=sampling_rate)
df = bio["df"]

events = nk.find_events(df["Photosensor"], cut="lower")
epochs = nk.create_epochs(df, events["onsets"], duration=7*sampling_rate, onset=-1*sampling_rate)

eda = []
hr = []
for epoch_index in epochs:
    epoch = epochs[epoch_index]
    eda.append(epoch["SCR_Peaks"].ix[0:550].max())
    hr.append(epoch["ECG_RR_Interval"].ix[0:300].max())
#    data.append(nk.bio_EventRelated(epochs[epoch_index], event_length=3, sampling_rate=50))
