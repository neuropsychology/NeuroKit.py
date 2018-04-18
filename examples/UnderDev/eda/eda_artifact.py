import numpy as np
import neurokit as nk
import pandas as pd
import pywt


"""
https://github.com/MITMediaLabAffectiveComputing/eda-explorer
http://eda-explorer.media.mit.edu/info/
"""






df, sampling_rate = nk.read_acqknowledge("bio_data.acq", return_sampling_rate=True)
eda = df["EDA, X, PPGED-R"]
eda_processed = nk.eda_process(eda, sampling_rate=sampling_rate)
eda = eda_processed["df"]["EDA_Phasic"]


def getWaveletData(eda):
    '''
    This function computes the wavelet coefficients
    INPUT:
        data:           DataFrame, index is a list of timestamps at 8Hz, columns include EDA, filtered_eda
    OUTPUT:
        wave1Second:    DateFrame, index is a list of timestamps at 1Hz, columns include OneSecond_feature1, OneSecond_feature2, OneSecond_feature3
        waveHalfSecond: DateFrame, index is a list of timestamps at 2Hz, columns include HalfSecond_feature1, HalfSecond_feature2
    '''

    # Create wavelet dataframes
    oneSecond =
    halfSecond =

    # Compute wavelets
    cA_n, cD_3, cD_2, cD_1 = pywt.wavedec(eda, 'Haar', level=3) #3 = 1Hz, 2 = 2Hz, 1=4Hz

    # Wavelet 1 second window
    N = int(len(eda)/sampling_rate)
    coeff1 = np.max(abs(np.reshape(cD_1[0:4*N],(N,4))), axis=1)
    coeff2 = np.max(abs(np.reshape(cD_2[0:2*N],(N,2))), axis=1)
    coeff3 = abs(cD_3[0:N])
    wave1Second = pd.DataFrame({'OneSecond_feature1':coeff1,'OneSecond_feature2':coeff2,'OneSecond_feature3':coeff3})
    wave1Second.index = oneSecond[:len(wave1Second)]

    # Wavelet Half second window
    N = int(np.floor((len(data)/8.0)*2))
    coeff1 = np.max(abs(np.reshape(cD_1[0:2*N],(N,2))),axis=1)
    coeff2 = abs(cD_2[0:N])
    waveHalfSecond = pd.DataFrame({'HalfSecond_feature1':coeff1,'HalfSecond_feature2':coeff2})
    waveHalfSecond.index = halfSecond[:len(waveHalfSecond)]

    return wave1Second,waveHalfSecond

wave1Second.plot()


def getDerivatives(eda):
    deriv = (eda[1:-1] + eda[2:])/ 2. - (eda[1:-1] + eda[:-2])/ 2.
    second_deriv = eda[2:] - 2*eda[1:-1] + eda[:-2]
    return(deriv, second_deriv)





def get3MaxDerivatives(eda,num_max=3):
    deriv, second_deriv = getDerivatives(eda)
    d = copy.deepcopy(deriv)
    d2 = copy.deepcopy(second_deriv)
    max_indices = []
    for i in range(num_max):
        maxd_idx = np.nanargmax(abs(d))
        max_indices.append(maxd_idx)
        d[maxd_idx] = 0
        max2d_idx = np.nanargmax(abs(d2))
        max_indices.append(max2d_idx)
        d2[max2d_idx] = 0

    return max_indices, abs(deriv), abs(second_deriv)

def getDerivStats(eda):
    deriv, second_deriv = getDerivatives(eda)
    maxd = max(deriv)
    mind = min(deriv)
    maxabsd = max(abs(deriv))
    avgabsd = np.mean(abs(deriv))
    max2d = max(second_deriv)
    min2d = min(second_deriv)
    maxabs2d = max(abs(second_deriv))
    avgabs2d = np.mean(abs(second_deriv))

    return maxd,mind,maxabsd,avgabsd,max2d,min2d,maxabs2d,avgabs2d

def getStats(data):
    eda = data['EDA'].as_matrix()
    filt = data['filtered_eda'].as_matrix()
    maxd,mind,maxabsd,avgabsd,max2d,min2d,maxabs2d,avgabs2d = getDerivStats(eda)
    maxd_f,mind_f,maxabsd_f,avgabsd_f,max2d_f,min2d_f,maxabs2d_f,avgabs2d_f = getDerivStats(filt)
    amp = np.mean(eda)
    amp_f = np.mean(filt)
    return amp, maxd,mind,maxabsd,avgabsd,max2d,min2d,maxabs2d,avgabs2d,amp_f,maxd_f,mind_f,maxabsd_f,avgabsd_f,max2d_f,min2d_f,maxabs2d_f,avgabs2d_f
