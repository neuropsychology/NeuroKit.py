#import pandas as pd
#import numpy as np
#import neurokit as nk
#import biosppy
#
#df = pd.read_csv("data_bvp.csv", sep=";")
##bvp = df["BVP"]
#
#df.columns
#
#df['SGZ'][df['SGZ'].notnull()].plot(subplots=True)
#bvp = df['SGZ'][df['SGZ'].notnull()]
#
#
#df.plot()
#df[27000:27080][['SGZ']].plot(subplots=True)
#
#7/20*60
#
#df, sampling_rate = nk.read_acqknowledge("bvp2.acq", return_sampling_rate=True)
#df.columns
#df[100000:120000]["PPG, X, PPGED-R"].plot()
#bvp2 = df["PPG, X, PPGED-R"][0:200000]
#
#
#features = dict(biosppy.bvp.bvp(bvp2, 1000))





import numpy as np
import matplotlib.pyplot as plt
import matplotlib


freqs = np.arange(2, 20, 3)

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*freqs[0]*t)
l, = plt.plot(t, s, lw=2)


class Index(object):
    ind = 0

    def good(self, event, response=[]):
        self.ind += 1
        i = self.ind % len(freqs)
        ydata = np.sin(2*np.pi*freqs[i]*t)
        l.set_ydata(ydata)
        plt.draw()
        response.append("good")


    def bad(self, event, response=[]):
        self.ind -= 1
        i = self.ind % len(freqs)
        ydata = np.sin(2*np.pi*freqs[i]*t)
        l.set_ydata(ydata)
        plt.draw()
        response.append("bad")


response = []
callback = Index()
axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bnext = matplotlib.widgets.Button(axnext, 'Good', response)
bnext.on_clicked(callback.good)
bprev = matplotlib.widgets.Button(axprev, 'Bad',)
bprev.on_clicked(callback.bad)

plt.show()
