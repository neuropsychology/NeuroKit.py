import sklearn
import pandas as pd
import neurokit as nk
import numpy as np
import seaborn as sns

ecg = pd.read_csv("data_test_ecg.csv")["ECG"]


ecg = nk.ecg_process(ecg)["ECG"]
CCs = ecg["Cardiac_Cycles"]
CCs = pd.DataFrame(CCs).T
CCs.index = pd.date_range(pd.datetime.today(), periods=600, freq="ms")
CCs = CCs.rolling(20).mean().resample("3L").pad()
CCs = CCs.reset_index(drop=True)[8:200]
CCs = nk.z_score(CCs).T
CCs = np.array(CCs)



model = sklearn.externals.joblib.load('heartbeat_evaluation.pkl')
predict = model.predict_proba(CCs)
predict = pd.DataFrame(predict)
predict.columns = model.classes_
sns.distplot(pd.DataFrame(predict))
