# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import biosppy


import cvxopt as cv
import cvxopt.solvers

from ..statistics import z_score
from ..miscellaneous import find_closest_in_list




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eda_process(eda, sampling_rate=1000, cvxEDA_alpha=8e-4, cvxEDA_gamma=1e-2, scr_min_amplitude=0.1):
    """
    Automated processing of EDA signal.

    Parameters
    ----------
    eda :  list or array
        EDA signal array.
    sampling_rate : int
        Sampling rate (samples/second).
    use_cvxEDA : bool
        Use convex optimization (CVXEDA) described in "cvxEDA: a Convex Optimization Approach to Electrodermal Activity Processing" (Greco et al., 2015).
    cvxEDA_normalize : bool
        Normalize the signal before applying cvx algorithm.
    cvxEDA_alpha : float
        Penalization for the sparse SMNA driver.
    cvxEDA_gamma : float
        Penalization for the tonic spline coefficients.
    scr_min_amplitude : float
        Minimum treshold by which to exclude Skin Conductance Responses (SCRs).

    Returns
    ----------
    processed_eda : dict
        Dict containing processed EDA features.

        Contains the EDA raw signal, the filtered signal, the phasic compnent (if cvxEDA is True), the SCR onsets, peak indexes and amplitudes.

        This function is mainly a wrapper for the biosppy.eda.eda() and cvxEDA() functions. Credits go to their authors.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_eda = nk.eda_process(eda_signal)


    Notes
    ----------
    *Details*

    - **cvxEDA**: Based on a model which describes EDA as the sum of three terms: the phasic component, the tonic component, and an additive white Gaussian noise term incorporating model prediction errors as well as measurement errors and artifacts. This model is physiologically inspired and fully explains EDA through a rigorous methodology based on Bayesian statistics, mathematical convex optimization and sparsity.


    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - biosppy
    - numpy
    - pandas
    - cvxopt

    *See Also*

    - BioSPPy: https://github.com/PIA-Group/BioSPPy
    - cvxEDA: https://github.com/lciti/cvxEDA

    References
    -----------
    - Greco, A., Valenza, G., & Scilingo, E. P. (2016). Evaluation of CDA and CvxEDA Models. In Advances in Electrodermal Activity Processing with Applications for Mental Health (pp. 35-43). Springer International Publishing.
    - Greco, A., Valenza, G., Lanata, A., Scilingo, E. P., & Citi, L. (2016). cvxEDA: A convex optimization approach to electrodermal activity processing. IEEE Transactions on Biomedical Engineering, 63(4), 797-804.

    """
    # Initialization
    eda = np.array(eda)
    eda_df = pd.DataFrame({"EDA_Raw": np.array(eda)})

    # Preprocessing
    # ===================
    # Filtering
    filtered, _, _ = biosppy.tools.filter_signal(signal=eda,
                                 ftype='butter',
                                 band='lowpass',
                                 order=4,
                                 frequency=5,
                                 sampling_rate=sampling_rate)

    # Smoothing
    filtered, _ = biosppy.tools.smoother(signal=filtered,
                              kernel='boxzen',
                              size=int(0.75 * sampling_rate),
                              mirror=True)
    eda_df["EDA_Filtered"] = filtered
    eda_df.plot()

    # Derive Phasic and Tonic
    try:
        tonic, phasic = cvxEDA(eda, sampling_rate=sampling_rate, alpha=cvxEDA_alpha, gamma=cvxEDA_gamma)
        eda_df["EDA_Phasic"] = phasic
        eda_df["EDA_Tonic"] = tonic
        signal = phasic
    except:
        print("NeuroKit Warning: eda_process(): couln't apply cvxEDA to extract phasic and tonic components. Using raw signal.")
        signal = eda

    # Skin-Conductance Responses
    # ===========================
    if scr_method == "kim":
        onsets, peaks, amplitudes = biosppy.eda.kbk_scr(signal=signal, sampling_rate=sampling_rate, min_amplitude=0.1)
    if scr_method == "gamboa":
        onsets, peaks, amplitudes = biosppy.eda.basic_scr(signal=signal, sampling_rate=sampling_rate)


    # Compute several features using biosppy
    biosppy_eda = dict(biosppy.signals.eda.eda(eda, sampling_rate=sampling_rate, show=False, min_amplitude=scr_min_amplitude))

    eda_df["EDA_Filtered"] = biosppy_eda["filtered"]

    # Store SCR onsets
    scr_onsets = np.array([np.nan]*len(eda))
    if len(biosppy_eda['onsets']) > 0:
        scr_onsets[biosppy_eda['onsets']] = 1
    eda_df["SCR_Onsets"] = scr_onsets

    # Store SCR peaks and amplitudes
    scr_peaks = np.array([np.nan]*len(eda))
    peak_index = 0
    for index in range(len(scr_peaks)):
        try:
            if index == biosppy_eda["peaks"][peak_index]:
                scr_peaks[index] = biosppy_eda['amplitudes'][peak_index]
                peak_index += 1
        except:
            pass
    eda_df["SCR_Peaks"] = scr_peaks

    processed_eda = {"df": eda_df,
                     "EDA": {
                            "SCR_Onsets": biosppy_eda['onsets'],
                            "SCR_Peaks_Indexes": biosppy_eda["peaks"],
                            "SCR_Peaks_Amplitudes": biosppy_eda['amplitudes']}}
    return(processed_eda)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def cvxEDA(eda, sampling_rate=1000, tau0=2., tau1=0.7, delta_knot=10., alpha=8e-4, gamma=1e-2, solver=None, verbose=False, options={'reltol':1e-9}):
    """
    A convex optimization approach to electrodermal activity processing (CVXEDA).

    This function implements the cvxEDA algorithm described in "cvxEDA: a
    Convex Optimization Approach to Electrodermal Activity Processing" (Greco et al., 2015).

    Parameters
    ----------
       eda : list or array
           raw EDA signal array.
       sampling_rate : int
           Sampling rate (samples/second).
       tau0 : float
           Slow time constant of the Bateman function.
       tau1 : float
           Fast time constant of the Bateman function.
       delta_knot : float
           Time between knots of the tonic spline function.
       alpha : float
           Penalization for the sparse SMNA driver.
       gamma : float
           Penalization for the tonic spline coefficients.
       solver : bool
           Sparse QP solver to be used, see cvxopt.solvers.qp
       verbose : bool
           Print progress?
       options : dict
           Solver options, see http://cvxopt.org/userguide/coneprog.html#algorithm-parameters

    Returns
    ----------
        phasic : numpy.array
            The phasic component.


    Notes
    ----------
    *Authors*

    - Luca Citi (https://github.com/lciti)
    - Alberto Greco

    *Dependencies*

    - cvxopt
    - numpy

    *See Also*

    - cvxEDA: https://github.com/lciti/cvxEDA


    References
    -----------
    - Greco, A., Valenza, G., & Scilingo, E. P. (2016). Evaluation of CDA and CvxEDA Models. In Advances in Electrodermal Activity Processing with Applications for Mental Health (pp. 35-43). Springer International Publishing.
    - Greco, A., Valenza, G., Lanata, A., Scilingo, E. P., & Citi, L. (2016). cvxEDA: A convex optimization approach to electrodermal activity processing. IEEE Transactions on Biomedical Engineering, 63(4), 797-804.
    """
    frequency = 1/sampling_rate

    # Normalizing signal
    eda = z_score(eda)
    eda = np.array(eda)[:,0]

    n = len(eda)
    eda = cv.matrix(eda)

    # bateman ARMA model
    a1 = 1./min(tau1, tau0) # a1 > a0
    a0 = 1./max(tau1, tau0)
    ar = np.array([(a1*frequency + 2.) * (a0*frequency + 2.), 2.*a1*a0*frequency**2 - 8.,
        (a1*frequency - 2.) * (a0*frequency - 2.)]) / ((a1 - a0) * frequency**2)
    ma = np.array([1., 2., 1.])

    # matrices for ARMA model
    i = np.arange(2, n)
    A = cv.spmatrix(np.tile(ar, (n-2,1)), np.c_[i,i,i], np.c_[i,i-1,i-2], (n,n))
    M = cv.spmatrix(np.tile(ma, (n-2,1)), np.c_[i,i,i], np.c_[i,i-1,i-2], (n,n))

    # spline
    delta_knot_s = int(round(delta_knot / frequency))
    spl = np.r_[np.arange(1.,delta_knot_s), np.arange(delta_knot_s, 0., -1.)] # order 1
    spl = np.convolve(spl, spl, 'full')
    spl /= max(spl)
    # matrix of spline regressors
    i = np.c_[np.arange(-(len(spl)//2), (len(spl)+1)//2)] + np.r_[np.arange(0, n, delta_knot_s)]
    nB = i.shape[1]
    j = np.tile(np.arange(nB), (len(spl),1))
    p = np.tile(spl, (nB,1)).T
    valid = (i >= 0) & (i < n)
    B = cv.spmatrix(p[valid], i[valid], j[valid])

    # trend
    C = cv.matrix(np.c_[np.ones(n), np.arange(1., n+1.)/n])
    nC = C.size[1]

    # Solve the problem:
    # .5*(M*q + B*l + C*d - eda)^2 + alpha*sum(A,1)*p + .5*gamma*l'*l
    # s.t. A*q >= 0

    if verbose is False:
        options["show_progress"] = False
    old_options = cv.solvers.options.copy()
    cv.solvers.options.clear()
    cv.solvers.options.update(options)
    if solver == 'conelp':
        # Use conelp
        z = lambda m,n: cv.spmatrix([],[],[],(m,n))
        G = cv.sparse([[-A,z(2,n),M,z(nB+2,n)],[z(n+2,nC),C,z(nB+2,nC)],
                    [z(n,1),-1,1,z(n+nB+2,1)],[z(2*n+2,1),-1,1,z(nB,1)],
                    [z(n+2,nB),B,z(2,nB),cv.spmatrix(1.0, range(nB), range(nB))]])
        h = cv.matrix([z(n,1),.5,.5,eda,.5,.5,z(nB,1)])
        c = cv.matrix([(cv.matrix(alpha, (1,n)) * A).T,z(nC,1),1,gamma,z(nB,1)])
        res = cv.solvers.conelp(c, G, h, dims={'l':n,'q':[n+2,nB+2],'s':[]})
        obj = res['primal objective']
    else:
        # Use qp
        Mt, Ct, Bt = M.T, C.T, B.T
        H = cv.sparse([[Mt*M, Ct*M, Bt*M], [Mt*C, Ct*C, Bt*C],
                    [Mt*B, Ct*B, Bt*B+gamma*cv.spmatrix(1.0, range(nB), range(nB))]])
        f = cv.matrix([(cv.matrix(alpha, (1,n)) * A).T - Mt*eda,  -(Ct*eda), -(Bt*eda)])
        res = cv.solvers.qp(H, f, cv.spmatrix(-A.V, A.I, A.J, (n,len(f))),
                            cv.matrix(0., (n,1)), solver=solver)
        obj = res['primal objective'] + .5 * (eda.T * eda)
    cv.solvers.options.clear()
    cv.solvers.options.update(old_options)

    l = res['x'][-nB:]
    d = res['x'][n:n+nC]
    tonic = B*l + C*d
    q = res['x'][:n]
    p = A * q
    phasic = M * q
    e = eda - phasic - tonic

    phasic = np.array(phasic)[:,0]
#    results = (np.array(a).ravel() for a in (r, t, p, l, d, e, obj))

    return(tonic, phasic)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def eda_EventRelated(epoch, event_length, window_post=4):
    """
    Extract event-related EDA and Skin Conductance Response (SCR).

    Parameters
    ----------
    epoch : pandas.DataFrame
        An epoch contains in the epochs dict returned by :function:`neurokit.create_epochs()` on dataframe returned by :function:`neurokit.bio_process()`. Index must range from -4s to +4s (relatively to event onset and end).
    event_length : int
        Event's length in seconds.
    window_post : float
        Post-stimulus window size (in seconds) to include eventual responses (usually 3 or 4).

    Returns
    ----------
    EDA_Response : dict
        Event-related EDA response features.

    Example
    ----------
    >>> import neurokit as nk
    >>> bio = nk.bio_process(eda=df["EDA"], add=df["Photosensor"])
    >>> df = bio["df"]
    >>> events = nk.find_events(df["Photosensor"], cut="lower")
    >>> epochs = nk.create_epochs(df, events["onsets"], duration=events["durations"]+8000, onset=-4000)
    >>> for epoch in epochs:
    >>>     EDA_Response = nk.eda_ERP(epoch, event_length=4000)

    Notes
    ----------
    *Details*

    - **Looking for help**: *Experimental*: respiration artifacts correction needs to be implemented.
    - **EDA_Peak**: Max of EDA (in a window starting 1s after the stim onset) minus baseline.
    - **SCR_Amplitude**: Peak of SCR. If no SCR, returns NA.
    - **SCR_Magnitude**: Peak of SCR. If no SCR, returns 0.
    - **SCR_Amplitude_Log**: log of 1+amplitude.
    - **SCR_Magnitude_Log**: log of 1+magnitude.
    - **SCR_PeakTime**: Time of peak.
    - **SCR_Latency**: Time between stim onset and SCR onset.
    - **SCR_RiseTime**: Time between SCR onset and peak.
    - **SCR_Strength**: *Experimental*: peak divided by latency. Angle of the line between peak and onset.


    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)

    *Dependencies*

    - numpy
    - pandas

    *See Also*

    - https://www.biopac.com/wp-content/uploads/EDA-SCR-Analysis.pdf

    References
    -----------
    - Schneider, R., Schmidt, S., Binder, M., Schäfer, F., & Walach, H. (2003). Respiration-related artifacts in EDA recordings: introducing a standardized method to overcome multiple interpretations. Psychological reports, 93(3), 907-920.
    - Leiner, D., Fahr, A., & Früh, H. (2012). EDA positive change: A simple algorithm for electrodermal activity to measure general audience arousal during media exposure. Communication Methods and Measures, 6(4), 237-250.
    """
    # Initialization
    EDA_Response = {}
    window_end = event_length + window_post
    onset = find_closest_in_list(0.5, epoch.index, direction="smaller")


    # Sanity check
    if epoch.index[-1]-event_length < 1:
        print("NeuroKit Warning: eda_EventRelated(): your epoch only lasts for about %.2f s post stimulus. You might lose some SCRs." %(epoch.index[-1]-event_length))


    # EDA Based
    # =================
    baseline = epoch["EDA_Filtered"][0:onset].min()
    eda_peak = epoch["EDA_Filtered"][onset:window_end].max()
    EDA_Response["EDA_Peak"] = eda_peak - baseline


    epoch["EDA_Filtered"].plot()
    # SCR Based
    # =================
    # Computation
    peak_onset = epoch["SCR_Onsets"][onset:window_end].idxmax()
    if pd.isnull(peak_onset) is False:
        amplitude = epoch["SCR_Peaks"][peak_onset:window_end].max()
        peak_time = epoch["SCR_Peaks"][peak_onset:window_end].idxmax()

        if pd.isnull(amplitude):
            magnitude = 0
        else:
            magnitude = amplitude

        risetime = peak_time - peak_onset
        strength = magnitude/risetime
#        recovery = nk.find_closest_in_list(magnitude/2, epoch.index, direction="smaller")

    else:
        amplitude = np.nan
        magnitude = 0
        risetime = np.nan
        strength = np.nan

    # Storage
    EDA_Response["SCR_Amplitude"] = amplitude
    EDA_Response["SCR_Magnitude"] = magnitude
    EDA_Response["SCR_Amplitude_Log"] = np.log(1+amplitude)
    EDA_Response["SCR_Magnitude_Log"] = np.log(1+magnitude)
    EDA_Response["SCR_Latency"] = peak_onset
    EDA_Response["SCR_PeakTime"] = peak_time
    EDA_Response["SCR_RiseTime"] = risetime
    EDA_Response["SCR_Strength"] = strength  # Experimental




    # Artifact Correction
    # ====================
    # TODO !!
    # Respiration artifacts
    if "RSP_Filtered" in epoch.columns:
        pass  # I Dunno, maybe with granger causality or something?


    return(EDA_Response)

