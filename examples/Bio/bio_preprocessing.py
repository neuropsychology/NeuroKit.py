# -*- coding: utf-8 -*-
import neurokit as nk


acq = nk.acq_to_df("eda.acq", resampling_method="pad")
eda = acq["EDA, X, PPGED-R"][10000:40000]

acq = nk.acq_to_df("rest.acq")

ecg = acq["ECG, X, RSPEC-R"][100000:130000]
rsp = acq["RSP, X, RSPEC-R"][100000:130000]

acq = nk.acq_to_df("event.acq")
event = acq["Photosensor"][191800:221800]

df = pd.DataFrame({
        "ECG":list(ecg),
        "RSP":list(rsp),
        "EDA":list(eda),
        "Photosensor":list(event)})
df.to_csv("data_bio.csv")

