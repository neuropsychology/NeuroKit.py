import neurokit as nk
import pandas as pd
import numpy as np
import biosppy
#df = nk.read_acqknowledge("bio.acq")
#df2 = df["2017-05-31 17:07:43":"2017-05-31 17:35:33"]
#df2.plot()
#
#df.columns
#df3 = df2[["EDA, X, PPGED-R", "RSP, X, RSPEC-R", 'Photosensor']]
#df3.columns = ["EDA", "RSP", 'Photosensor']
#
#df4 = df3.resample("10L").mean()
#df4.plot()
#
#df4.to_csv("EDA_RSP_Artifacts.csv")
#
#data = pd.read_excel("data.xlsx")
#data = data.sort_values("Order")
#data = list(data["Emotion"])[0:48]
#pd.Series(data).to_csv("events.csv")

df = pd.read_csv("EDA_RSP_Artifacts.csv")  # Sampled at 100Hz
conditions = pd.Series.from_csv("events.csv")

# Preprocessing
df = nk.bio_process(eda=df["EDA"], rsp=df["RSP"], add=df[["Photosensor", "RSP"]], sampling_rate=100, scr_min_amplitude=0.05)
df = df["df"]


events = nk.find_events(df["Photosensor"], cut="lower")
epochs = nk.create_epochs(df, events["onsets"], duration=900, onset=-300)

# SIMPLE MODEL
#evoked = {"Negative": [], "Neutral": []}
#for index, condition in enumerate(conditions):
#    evoked[condition].append(epochs[index]["SCR_Peaks"].ix[50:600].max())
#diff = pd.Series(evoked["Negative"]).mean() - pd.Series(evoked["Neutral"]).mean()
#print(diff)
# 0.00022831300315032284



# SIMPLE MODEL - WITH SCR ONSET
#onsets = []
#evoked = {"Negative": [], "Neutral": []}
#for index, condition in enumerate(conditions):
#    peak_onset = epochs[index]["SCR_Onsets"].ix[0:300].idxmax()
#    if pd.isnull(peak_onset) is False:
#        evoked[condition].append(epochs[index]["SCR_Peaks"].ix[peak_onset:600].max())
#    else:
#        evoked[condition].append(np.nan)
#diff = pd.Series(evoked["Negative"]).mean() - pd.Series(evoked["Neutral"]).mean()
#print(diff)
#0.0004714861243897688

