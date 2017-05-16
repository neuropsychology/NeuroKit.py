import sklearn
import pandas as pd
import neurokit as nk
import numpy as np
import seaborn as sns

ecg = pd.read_csv("data_test_ecg.csv")["ECG"]


ecg = nk.ecg_process(ecg)["ECG"]
heartbeats = ecg["Cardiac_Cycles"]



def classify_heartbeats(heartbeats):
    heartbeats = pd.DataFrame(heartbeats).T
    heartbeats.index = pd.date_range(pd.datetime.today(), periods=600, freq="ms")
    heartbeats = heartbeats.rolling(20).mean().resample("3L").pad()
    heartbeats = heartbeats.reset_index(drop=True)[8:200]
    heartbeats = nk.z_score(heartbeats).T
    heartbeats = np.array(heartbeats)




    model = sklearn.externals.joblib.load(nk.Path.materials() + 'heartbeat_classification.model')
    predict = model.predict_proba(heartbeats)
    predict = pd.DataFrame(predict)
    predict.columns = model.classes_
    sns.distplot(pd.DataFrame(predict))
