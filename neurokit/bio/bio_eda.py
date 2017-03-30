# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import biosppy


import cvxopt as cv
import cvxopt.solvers

from ..statistics import z_score





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def process_eda(eda, sampling_rate=1000, use_cvxEDA=True):
    """
    Automated processing of EDA signal.

    Parameters
    ----------
    eda =  array
        EDA signal array.
    sampling_rate = int
        Sampling rate (samples/second).
    use_cvxEDA = bool
        Use convex optimization (CVXEDA) described in "cvxEDA: a Convex Optimization Approach to Electrodermal Activity Processing" (Greco et al., 2015).

    Returns
    ----------
    processed_eda = dict
        Dict containing processed EDA features.

        Contains the EDA raw signal, the filtered signal, the phasic compnent (if cvxEDA is True), the SCR onsets, peak indexes and amplitudes.

        This function is mainly a wrapper for the biosspy.eda.eda() and cvxEDA() functions. Credits go to their authors.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> processed_eda = nk.process_eda(eda_signal)

    Authors
    ----------
    Dominique Makowski, the bioSSPy dev team, the cvxEDA dev team

    Dependencies
    ----------
    - biosppy
    - numpy
    - pandas
    - cvxopt
    """

    eda_df = pd.DataFrame({"EDA_Raw": np.array(eda)})

    # Convex optimization
    if use_cvxEDA is True:
        eda = cvxEDA(eda, sampling_rate=sampling_rate)
        eda_df["EDA_Phasic"] = eda

    # Compute several features using biosppy
    biosppy_eda = dict(biosppy.signals.eda.eda(eda, sampling_rate=sampling_rate, show=False))

    eda_df["EDA_Filtered"] = biosppy_eda["filtered"]

    # Store SCR onsets
    scr_onsets = np.array([np.nan]*len(eda))
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

    processed_eda = {"EDA_Processed": eda_df,
                     "EDA_Features": {
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
def cvxEDA(eda, sampling_rate, tau0=2., tau1=0.7, delta_knot=10., alpha=8e-4, gamma=1e-2, solver=None, verbose=False, options={'reltol':1e-9}):
    """
    A convex optimization approach to electrodermal activity processing (CVXEDA)

    This function implements the cvxEDA algorithm described in "cvxEDA: a
    Convex Optimization Approach to Electrodermal Activity Processing" (Greco et al., 2015).

    Parameters
    ----------
       eda
           observed EDA signal.
       sampling_rate
           sampling rate (samples/seconds).
       tau0
           slow time constant of the Bateman function.
       tau1
           fast time constant of the Bateman function.
       delta_knot
           time between knots of the tonic spline function.
       alpha
           penalization for the sparse SMNA driver.
       gamma
           penalization for the tonic spline coefficients.
       solver
           sparse QP solver to be used, see cvxopt.solvers.qp
       verbose = bool
           Print progress?
       options
           solver options, see http://cvxopt.org/userguide/coneprog.html#algorithm-parameters

    Returns
    ----------
       phasic
           The phasic component.

    Authors
    ----------
    Luca Citi (lciti@ieee.org), Alberto Greco

    Citation
    ----------
    A Greco, G Valenza, A Lanata, EP Scilingo, and L Citi
    "cvxEDA: a Convex Optimization Approach to Electrodermal Activity Processing"
    IEEE Transactions on Biomedical Engineering, 2015
    DOI: 10.1109/TBME.2015.2474131

    Dependencies
    ----------
    - cvxopt
    - numpy
    """
    frequency = 1/sampling_rate

    z_eda = z_score(eda)
    z_eda = np.array(z_eda)[:,0]

    n = len(z_eda)
    z_eda = cv.matrix(z_eda)

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
    # .5*(M*q + B*l + C*d - z_eda)^2 + alpha*sum(A,1)*p + .5*gamma*l'*l
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
        h = cv.matrix([z(n,1),.5,.5,z_eda,.5,.5,z(nB,1)])
        c = cv.matrix([(cv.matrix(alpha, (1,n)) * A).T,z(nC,1),1,gamma,z(nB,1)])
        res = cv.solvers.conelp(c, G, h, dims={'l':n,'q':[n+2,nB+2],'s':[]})
        obj = res['primal objective']
    else:
        # Use qp
        Mt, Ct, Bt = M.T, C.T, B.T
        H = cv.sparse([[Mt*M, Ct*M, Bt*M], [Mt*C, Ct*C, Bt*C],
                    [Mt*B, Ct*B, Bt*B+gamma*cv.spmatrix(1.0, range(nB), range(nB))]])
        f = cv.matrix([(cv.matrix(alpha, (1,n)) * A).T - Mt*z_eda,  -(Ct*z_eda), -(Bt*z_eda)])
        res = cv.solvers.qp(H, f, cv.spmatrix(-A.V, A.I, A.J, (n,len(f))),
                            cv.matrix(0., (n,1)), solver=solver)
        obj = res['primal objective'] + .5 * (z_eda.T * z_eda)
    cv.solvers.options.clear()
    cv.solvers.options.update(old_options)

    l = res['x'][-nB:]
    d = res['x'][n:n+nC]
    tonic = B*l + C*d
    q = res['x'][:n]
    p = A * q
    phasic = M * q
    e = z_eda - phasic - tonic

    phasic = np.array(phasic)[:,0]
#    results = (np.array(a).ravel() for a in (r, t, p, l, d, e, obj))

    return(phasic)

