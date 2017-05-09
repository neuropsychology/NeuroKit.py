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
def eda_process(eda, sampling_rate=1000, use_cvxEDA=True, cvxEDA_normalize=True, cvxEDA_alpha=8e-4, cvxEDA_gamma=1e-2, scr_min_amplitude=0.1):
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
    eda_df = pd.DataFrame({"EDA_Raw": np.array(eda)})

    # Convex optimization
    if use_cvxEDA is True:
        try:
            eda = cvxEDA(eda, sampling_rate=sampling_rate, normalize=cvxEDA_normalize, alpha=cvxEDA_alpha, gamma=cvxEDA_gamma)
            eda_df["EDA_Phasic"] = eda
        except:
            print("NeuroKit Warning: couln't apply cvxEDA on EDA signal. Using normal.")

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
def cvxEDA(eda, sampling_rate, normalize=True, tau0=2., tau1=0.7, delta_knot=10., alpha=8e-4, gamma=1e-2, solver=None, verbose=False, options={'reltol':1e-9}):
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
       normalize : bool
           Normalize the signal before applying cvx algorithm.
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

    if normalize is True:
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

    return(phasic)

