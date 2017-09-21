import neurokit as nk
import numpy as np
import pandas as pd
import biosppy
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
#==============================================================================
# Create data
#==============================================================================
#data = nk.read_nk_object("PTB-Diagnostic_database-ECG.nk")
#
#All = []
#for participant in data["Control"]:
#    for signal_name in data["Control"][participant]["Signals"].columns:
#        signal = data["Control"][participant]["Signals"][signal_name]
#        CCs = dict(biosppy.ecg.ecg(signal, sampling_rate=data["Control"][participant]["sampling_rate"], show=False))["templates"]
#        CCs = pd.DataFrame(CCs).T
#
#        CCs.index = pd.date_range(pd.datetime.today(), periods=600, freq="ms")
#
#        # 200 Hz
#        CCs = CCs.rolling(20).mean().resample("3L").pad()
#        CCs = CCs.reset_index(drop=True)[0:200]
#        if list(CCs.index) == list(range(200)):
#            if len(CCs) == 200:
#                CCs = CCs.T
#                CCs["Lead"] = signal_name
#                All.append(CCs)
#
#df = pd.concat(All, axis=0, ignore_index=True)
#df.to_csv("cardiac_cycles.csv", index=False)
df = pd.DataFrame.from_csv("cardiac_cycles.csv")


#==============================================================================
# Preprocessing
#==============================================================================

# Remove lines with NA
df = df.dropna(axis=1)

# Z score
y = df.pop("Lead")
df = nk.z_score(df.T).T
X = np.array(df)

X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.33, random_state=666)





##==============================================================================
## Fit model
##==============================================================================
model = sklearn.neural_network.MLPClassifier()
#
model.fit(X_train, y_train)


y_pred = model.predict(X_test)

#
#
#
##==============================================================================
## Evaluation
##==============================================================================
labels = list(set(y_pred))
labels.sort()
cm = sklearn.metrics.confusion_matrix(y_test, y_pred)
cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
cm = pd.DataFrame(cm, index = [i for i in labels],
                  columns = [i for i in labels])
sns.heatmap(cm, annot=True, fmt='.2f')



def classifaction_report_df(report):
    lines = report.split('\n')
    lines = lines[2:-1]
    lines.pop(-2)

    report = {}
    for i, line in enumerate(lines):
        report[i] = line
        line = line.split(" ")
        line.remove("")
        line = [x for x in line if x != ""]
        report[i] = line
    report[len(lines)-1] = ["Average"] + report[len(lines)-1][3:]
    report = pd.DataFrame.from_dict(report).T
    report.columns = ["class", "precision", "recall", "f1_score", "support"]
    return(report)
report = classifaction_report_df(sklearn.metrics.classification_report(y_test, y_pred))
sklearn.metrics.accuracy_score(y_test, y_pred)

##==============================================================================
## Save
##==============================================================================
#
#sklearn.externals.joblib.dump(model, 'heartbeat_evaluation.model')
