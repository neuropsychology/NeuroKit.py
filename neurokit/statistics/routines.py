# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import scipy
import scipy.stats




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def dprime(n_Hit=None, n_Miss=None, n_FA=None, n_CR=None):
    """
    Computes the d', beta, aprime, b''d and c parameters based on the signal detection theory (SDT). **Feel free to help me expand the documentation of this function with details and interpretation guides.**

    Parameters
    ----------
    n_Hit : int
        Number of hits.
    n_Miss : int
        Number of misses.
    n_FA : int
        Number of false alarms.
    n_CR : int
       Number of correct rejections.

    Returns
    ----------
    parameters : dict
        A dictionary with the parameters (see details).

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)


    Notes
    ----------
    *Details*

    The Signal Detection Theory (often abridged as SDT) is used in very different domains from psychology (psychophysics, perception, memory), medical diagnostics (do the symptoms match a known diagnostic or can they be dismissed are irrelevant), to statistical decision (do the data indicate that the experiment has an effect or not). It evolved from the development of communications and radar equipment the first half of this century to psychology, as an attempt to understand some features of human behavior that were not well explained by tradition models. SDT is, indeed, used to analyze data coming from experiments where the task is to categorize ambiguous stimuli which can be generated either by a known process (called the *signal*) or be obtained by chance (called the *noise* in the SDT framework). Based on the number of hits, misses, false alarms and correct rejections, it estimates two main parameters from the experimental data: **d' (d-prime, for discriminability index**) and C (a variant of it is called beta). Non parametric variants are aprime and b''d (bppd)

    - **dprime**: The sensitivity index. Indicates the strength of the signal (relative to the noise). More specifically, it is the standardized difference between the means of the Signal Present and Signal Absent distributions.
    - **beta**: Response bias index.
    - **aprime**:  Non-parametric sensitivity index.
    - **bppd**: Non-parametric response bias index.
    - **c**: Response bias index.

    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_


    *Dependencies*

    - scipy

    *See Also*

    - `neuropsychology <https://www.rdocumentation.org/packages/neuropsychology/topics/dprime>`_
    - http://lindeloev.net/calculating-d-in-python-and-php/
    """
    n_Hit = 9
    n_Miss = 2
    n_FA = 4
    n_CR = 6

    # Ratios
    hit_rate = n_Hit/(n_Hit + n_Miss)
    fa_rate = n_FA/(n_FA + n_CR)


    # Adjusted ratios
    hit_rate_adjusted = (n_Hit+ 0.5)/((n_Hit+ 0.5) + n_Miss + 1)
    fa_rate_adjusted = (n_FA+ 0.5)/((n_FA+ 0.5) + n_CR + 1)


    # dprime
    dprime = scipy.stats.norm.ppf(hit_rate_adjusted) - scipy.stats.norm.ppf(hit_rate_adjusted)

    # beta
    zhr = scipy.stats.norm.ppf(hit_rate_adjusted)
    zfar = scipy.stats.norm.ppf(fa_rate_adjusted)
    beta = np.exp(-zhr*zhr/2 + zfar*zfar/2)

    # aprime
    a = 1/2+((hit_rate-fa_rate)*(1+hit_rate-fa_rate) / (4*hit_rate*(1-fa_rate)))
    b = 1/2-((fa_rate-hit_rate)*(1+fa_rate-hit_rate) / (4*fa_rate*(1-hit_rate)))

    if fa_rate > hit_rate:
        aprime = b
    elif fa_rate < hit_rate:
        aprime = a
    else:
        aprime = 0.5

    # bppd
    bppd = ((1-hit_rate)*(1-fa_rate)-hit_rate*fa_rate) / ((1-hit_rate)*(1-fa_rate)+hit_rate*fa_rate)

    # c
    c = -(scipy.stats.norm.ppf(hit_rate_adjusted) + scipy.stats.norm.ppf(fa_rate_adjusted))/2

    parameters = dict(dprime=dprime, beta=beta, aprime=aprime, bppd=bppd, c=c)
    return(parameters)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def BMI(height, weight, age, sex):
    """
    Returns the traditional BMI, the 'new' Body Mass Index and estimates the Body Fat Percentage (BFP; Deurenberg et al., 1991).

    Parameters
    ----------
    height : float
        Height in cm.
    weight : float
        Weight in kg.
    age : float
        Age in years.
    sex : str
        "m" or "f".

    Returns
    ----------
    bmi : dict
        dict containing values and their interpretations.

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.BMI(height=166, weight=54, age=22, sex="f")

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *See Also*

    - https://people.maths.ox.ac.uk/trefethen/bmi.html

    References
    -----------
    - Deurenberg, P., Andreoli, A., Borg, P., & Kukkonen-Harjula, K. (2001). The validity of predicted body fat percentage from body mass index and from impedance in samples of five European populations. European Journal of Clinical Nutrition, 55(11), 973.
    - Deurenberg, P., Weststrate, J. A., & Seidell, J. C. (1991). Body mass index as a measure of body fatness: age-and sex-specific prediction formulas. British journal of nutrition, 65(02), 105-114.
    """
    # BMI
    height = height/100
    bmi = {}
    bmi["BMI_old"] = weight/(height**2)
    bmi["BMI_new"] = 1.3*weight/height**2.5
    if bmi["BMI_new"] < 15:
        bmi["BMI_category"] = "Very severely underweight"
    if 15 < bmi["BMI_new"] < 16:
         bmi["BMI_category"] = "Severely underweight"
    if 16 < bmi["BMI_new"] < 18.5:
         bmi["BMI_category"] = "Underweight"
    if 18.5 < bmi["BMI_new"] < 25:
         bmi["BMI_category"] = "Healthy weight"
    if 25 < bmi["BMI_new"] < 30:
         bmi["BMI_category"] = "Overweight"
    if 30 < bmi["BMI_new"] < 35:
         bmi["BMI_category"] = "Moderately obese"
    if 35 < bmi["BMI_new"] < 40:
         bmi["BMI_category"] = "Severely obese"
    if bmi["BMI_new"] > 40:
         bmi["BMI_category"] = "Very severely obese"

    # BFP
    if sex.lower() == "m":
        sex = 1
    else:
        sex = 0

    if age <= 15:
        bmi["BFP"] = 1.51*bmi["BMI_old"]-0.70*age-3.6*sex+1.4
    else:
        bmi["BFP"] = 1.20*bmi["BMI_old"] + 0.23*age-10.8*sex-5.4

    if sex == 1:
        if bmi["BFP"] < 2:
            bmi["BFP_category"] = "Critical"
        if 2 <= bmi["BFP"] < 6:
            bmi["BFP_category"] = "Essential"
        if 6 <= bmi["BFP"] < 13:
            bmi["BFP_category"] = "Athletic"
        if 13 <= bmi["BFP"] < 17:
            bmi["BFP_category"] = "Fitness"
        if 17 <= bmi["BFP"] < 22:
            bmi["BFP_category"] = "Average"
        if 22 <= bmi["BFP"] < 30:
            bmi["BFP_category"] = "Overweight"
        if bmi["BFP"] >= 30:
            bmi["BFP_category"] = "Obese"
    else:
        if bmi["BFP"] < 10:
            bmi["BFP_category"] = "Critical"
        if 10 <= bmi["BFP"] < 14:
            bmi["BFP_category"] = "Essential"
        if 14 <= bmi["BFP"] < 21:
            bmi["BFP_category"] = "Athletic"
        if 21 <= bmi["BFP"] < 25:
            bmi["BFP_category"] = "Fitness"
        if 25 <= bmi["BFP"] < 31:
            bmi["BFP_category"] = "Average"
        if 31 <= bmi["BFP"] < 40:
            bmi["BFP_category"] = "Overweight"
        if bmi["BFP"] >= 40:
            bmi["BFP_category"] = "Obese"



    return(bmi)




# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def compute_interoceptive_accuracy(nbeats_real, nbeats_reported):
    """
    Computes interoceptive accuracy according to Garfinkel (2015).

    Parameters
    ----------
    nbeats_real : int or list
        Real number of heartbeats.
    nbeats_reported : int or list
        Reported number of heartbeats.

    Returns
    ----------
    accuracy : float or list
        Objective accuracy in detecting internal bodily sensations. It is the central construct underpinning other interoceptive measures (Garfinkel, 2015).

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.compute_interoceptive_accuracy(5, 3)


    Authors
    ----------
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    Dependencies
    ----------
    - numpy
    """
    # Convert to array if list
    if isinstance(nbeats_real, list):
        nbeats_real = np.array(nbeats_real)
        nbeats_reported = np.array(nbeats_reported)
    # Compute accuracy
    accuracy = 1 - (abs(nbeats_real-nbeats_reported))/((nbeats_real+nbeats_reported)/2)

    return(accuracy)

