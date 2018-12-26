# -*- coding: utf-8 -*-
from __future__ import division
from .statistics import normal_range
from .statistics import find_following_duplicates
from .statistics import find_closest_in_list

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score

import matplotlib.pyplot as plt
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
def compute_dprime(n_Hit=None, n_Miss=None, n_FA=None, n_CR=None):
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
    >>> nk.compute_dprime(n_Hit=7, n_Miss=4, n_FA=6, n_CR=6)


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

    # Ratios
    hit_rate = n_Hit/(n_Hit + n_Miss)
    fa_rate = n_FA/(n_FA + n_CR)


    # Adjusted ratios
    hit_rate_adjusted = (n_Hit+ 0.5)/((n_Hit+ 0.5) + n_Miss + 1)
    fa_rate_adjusted = (n_FA+ 0.5)/((n_FA+ 0.5) + n_CR + 1)


    # dprime
    dprime = scipy.stats.norm.ppf(hit_rate_adjusted) - scipy.stats.norm.ppf(fa_rate_adjusted)

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
def compute_BMI(height, weight, age, sex):
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
    >>> nk.compute_BMI(height=166, weight=54, age=22, sex="f")

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
    Computes interoceptive accuracy according to Garfinkel et al., (2015).

    Parameters
    ----------
    nbeats_real : int or list
        Real number of heartbeats.
    nbeats_reported : int or list
        Reported number of heartbeats.

    Returns
    ----------
    accuracy : float or list
        Objective accuracy in detecting internal bodily sensations. It is the central construct underpinning other interoceptive measures (Garfinkel et al., 2015).

    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> nk.compute_interoceptive_accuracy(5, 3)


    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - numpy

    References
    -----------
    - Garfinkel, S. N., Seth, A. K., Barrett, A. B., Suzuki, K., & Critchley, H. D. (2015). Knowing your own heart: distinguishing interoceptive accuracy from interoceptive awareness. Biological psychology, 104, 65-74.
    """
    # Convert to array if list
    if isinstance(nbeats_real, list):
        nbeats_real = np.array(nbeats_real)
        nbeats_reported = np.array(nbeats_reported)
    # Compute accuracy
    accuracy = 1 - (abs(nbeats_real-nbeats_reported))/((nbeats_real+nbeats_reported)/2)

    return(accuracy)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
class staircase:
    def __init__(self, signal=[0, 100], treshold=0.50, burn=5, stop_n_inversions=False, prior_signal=[], prior_response=[]):
        """
        Staircase procedure handler to find a treshold. For now, using a GLM - likelihood method.

        Parameters
        ----------
        signal : list
            Either list with min or max or range of possible signal values.
        treshold : int or list
            Treshold (between 0 and 1) to look for.
        burn : int or list
            Signal values to try at the beginning. If int, then it computes n equally spaced values.
        stop_n_inversions : False or int
            Stop generating new signal values after n inversions.
        prior_signal : int or list
            Range of signal values used as prior.
        prior_response : int or list
            Range of response values used as prior.



        Example
        ----------
        >>> # Let's imagine a perception task designed to find the treshold of
        >>> # signal at which the participant detect the stimulus at 50% chance.
        >>> # The signal ranges from 0 to 100. We set priors that at 100, the
        >>> # stim is detected (1) and at 0, not detected (0).
        >>>
        >>> import neurokit as nk
        >>> staircase = staircase(signal=np.linspace(0, 100, 25),
        >>>                      treshold=0.50,
        >>>                      burn=5,
        >>>                      stop_n_inversions=False,
        >>>                      prior_signal=[0, 100],
        >>>                      prior_response=[0, 1])
        >>>
        >>>
        >>>
        >>> # Run the experiment
        >>> for trial in range(50):
        >>> signal = staircase.predict_next_value()
        >>> if signal != "stop":
        >>> # Simulate response
        >>>     if signal > 50:
        >>>         response = 1
        >>>     else:
        >>>         response = 0
        >>>     staircase.add_response(response=response, value=signal)
        >>>
        >>> # Get data
        >>> staircase.diagnostic_plot()
        >>> data = staircase.get_data()
        >>>


        Notes
        ----------
        *Authors*

        - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

        *Dependencies*

        - numpy
        - pandas
        - sklearn
        """
        self.treshold = treshold
        self.signal_min = np.min(signal)
        self.signal_max = np.max(signal)
        self.signal_range = self.signal_max - self.signal_min
        if len(signal) == 2:
            self.signal = pd.DataFrame({"Signal":np.linspace(self.signal_min, self.signal_max, 1000)})
        else:
            self.signal = pd.DataFrame({"Signal": signal})
        self.next_value = np.nan
        self.data = np.nan
        self.stop_n_inversions = stop_n_inversions
        self.prior_signal = prior_signal
        self.prior_response = prior_response

        if isinstance(burn, int):
            self.burn_n = burn
            self.burn = list(np.round(np.linspace(0, 100, burn), 2))
        else:
            self.burn_n = len(burn)
            self.burn = list(burn)

        self.X = pd.DataFrame({"Signal":prior_signal})
        self.y = np.array(prior_response)
        self.model = np.nan

    def fit_model(self, X, y):
        model = LogisticRegression(C=1)
        model = model.fit(X , y)
        return(model)

    def predict_next_value(self):
        if len(self.burn) > 0:
            value = np.random.choice(self.burn)
            self.burn.remove(value)
            self.next_value = value

        elif len(set(list(self.y))) <= 1:
            self.next_value = np.random.uniform(self.signal_min, self.signal_max)

        else:
            if self.stop_n_inversions is not False:
                if isinstance(self.stop_n_inversions, int):
                    inversions = find_following_duplicates(self.y[self.burn_n:])
                    n_inversions = np.sum(inversions)
                    if n_inversions > self.stop_n_inversions:
                        self.next_value = "stop"

            else:
                probs = self.model.predict_proba(self.signal)
                probs = pd.concat([pd.DataFrame(probs), self.signal], axis=1)
                next_value = probs[probs[1]==find_closest_in_list(self.treshold, probs[1])]
                self.next_value = next_value["Signal"].values[0]

        return(self.next_value)

    def add_response(self, response, value):
        """
        Add response to staircase.

        Parameters
        ----------
        response : int or bool
            0 or 1.
        value : int or float
            Signal corresponding to response.
        """
        if value != "stop":
            self.X = pd.concat([self.X, pd.DataFrame({"Signal":[value]})])
            self.y = np.array(list(self.y) + [response])
            if len(set(list(self.y))) > 1:
                self.model = self.fit_model(self.X , self.y)


    def diagnostic_plot(self):
        fig, axes = plt.subplots(nrows=2, ncols=2)

        data = self.get_data()
        X = pd.DataFrame(data["Signal"])
        y = data["Response"].values
        model = self.fit_model(X , y)
        probs = model.predict_proba(self.signal)
        probs = pd.concat([pd.DataFrame(probs), self.signal], axis=1)

        data["Signal"].plot(ax=axes[0,0], color="black")
        colors = {0:'red', 1:'green'}
        data.plot.scatter(x='Trial', y="Signal", c=data['Response'].apply(lambda x: colors[x]), ax=axes[0,0], zorder=3)
        axes[0, 0].set(xlabel="Trial Order", ylabel="Signal")
        axes[0, 0].set_title('Signal Staircase')

        probs.plot(legend=False, x='Signal', y=1, color="blue", ax=axes[0,1])
        axes[0, 1].set(ylabel="Probability")
        axes[0, 1].set_title('Probability Link')

        data.plot(legend=False, x="Trial", y="Treshold_Mean", color="orange", ax=axes[1,0])
        axes[1, 0].fill_between(data["Trial"], data["Treshold_Mean"]+data["Treshold_SD"], data["Treshold_Mean"]-data["Treshold_SD"], color="#009688")
        axes[1, 0].set(ylabel="Signal")
        axes[1, 0].set_title('Cumulative Treshold Mean')

        return(data)


    def get_data(self):
        self.data = pd.concat([self.X.reset_index(drop=True), pd.DataFrame({"Response":self.y})], axis=1)
        self.data = self.data[len(self.prior_response):]
        self.data = self.data.reset_index(drop=True)
        self.data["Trial"] = self.data.index
        self.data["Inversion"] = find_following_duplicates(self.data["Response"])
        self.data["Treshold_Mean"] = self.data['Signal'].expanding().mean()
        self.data["Treshold_SD"] = self.data['Signal'].expanding().std()
        self.data["Coef"] = self.get_coef()

        # Cross validation
        y_pred = self.model.predict(pd.DataFrame(self.data["Signal"]))
        y_test = self.data["Response"]
        self.data["MSE"] = mean_squared_error(y_test, y_pred)
        self.data["R2"] = r2_score(y_test, y_pred)
        return(self.data)

    def get_treshold(self):
        return(self.predict_next_value())

    def get_coef(self):
        coef = self.model.coef_[0][0]
        return(coef)
