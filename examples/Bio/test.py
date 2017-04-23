import neurokit as nk
import biosppy
ori = nk.read_acqknowledge("test.acq")


check = ori.ix[2500000:2510000]["ECG, X, RSPEC-R"]
rri = dict(biosppy.ecg.ecg(check))["rpeaks"]

#
#ori = ori.resample("10L").mean()
#
#ori.ix[250000:300000].plot()
#
#df = ori.ix[250000:300000]
#df.index
#
#df.columns
#bio = nk.bio_process(df["ECG, X, RSPEC-R"], df["RSP, X, RSPEC-R"], df['EDA, X, PPGED-R'], sampling_rate=500, add=df['Photosensor'])
#
#
#bio["df"].plot()
#bio["EDA"]
