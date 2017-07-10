# -*- coding: utf-8 -*-
import time as builtin_time
import pandas as pd
import numpy as np


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
class Time():
    """
    A class object to get time.
    Its methods (functions) are:
        - reset()
        - get()
    See those for further informations.

    Parameters
    ----------
    None

    Returns
    ----------
    None

    Example
    ----------
    >>> import neurokit as nk
    >>> myclock = nk.Time()
    >>> time_passed_since_myclock_creation = myclock.get()
    >>> myclock.reset()
    >>> time_passed_since_reset = myclock.get()

    Authors
    ----------
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    Dependencies
    ----------
    - time
    """
    def __init__(self):
        self.clock = builtin_time.clock()

    def reset(self):
        """
        Reset the clock of the Time object.

        Parameters
        ----------
        None

        Returns
        ----------
        None

        Example
        ----------
        >>> import neurokit as nk
        >>> time_passed_since_neuropsydia_loading = nk.time.get()
        >>> nk.time.reset()
        >>> time_passed_since_reset = nk.time.get()

        Authors
        ----------
        - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

        Dependencies
        ----------
        - time
        """
        self.clock = builtin_time.clock()

    def get(self, reset=True):
        """
        Get time since last initialisation / reset.

        Parameters
        ----------
        reset = bool, optional
            Should the clock be reset after returning time?

        Returns
        ----------
        float
            Time passed in milliseconds.

        Example
        ----------
        >>> import neurokit as nk
        >>> time_passed_since_neurobox_loading = nk.time.get()
        >>> nk.time.reset()
        >>> time_passed_since_reset = nk.time.get()

        Authors
        ----------
        - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

        Dependencies
        ----------
        - time
        """
        t = (builtin_time.clock()-self.clock)*1000

        if reset is True:
            self.reset()
        return(t)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_following_duplicates(array):
    """
    Find the duplicates that are following themselves.

    Parameters
    ----------
    array :  list or array
        A list containig duplicates.

    Returns
    ----------
    list
        A list containing True for each unique and False for following duplicates.

    Example
    ----------
    >>> import neurokit as nk
    >>> mylist = ["a","a","b","a","a","a","c","c","b","b"]
    >>> nk.find_following_duplicates(mylist)

    Authors
    ----------
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    Dependencies
    ----------
    - numpy
    """
    array = array.copy()


    uniques = []
    for i in range(len(array)):
        if i == 0:
            uniques.append(True)
        else:
            if array[i] == array[i-1]:
                uniques.append(False)
            else:
                uniques.append(True)


    # Find index of uniques
    indices = np.where(uniques)

    return(uniques)





# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_closest_in_list(number, array, direction="both", strictly=False):
    """
    Find the closest number in the array from x.

    Parameters
    ----------
    number :  float
        The number.
    array : list
        The list to look in.
    direction : str
        "both" for smaller or greater, "greater" for only greater numbers and "smaller" for the closest smaller.
    strictly : bool
        False for stricly superior or inferior or True for including equal.

    Returns
    ----------
    closest = int

    Example
    ----------
    >>> import neurokit as nk
    >>> nk.find_closest_in_list(1.8, [3, 5, 6, 1, 2])

    Authors
    ----------
    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
    """
    if direction == "both":
        closest = min(array, key=lambda x:abs(x-number))
    if direction == "smaller":
        if strictly is True:
            closest = max(x for x in array if x < number)
        else:
            closest = max(x for x in array if x <= number)
    if direction == "greater":
        if strictly is True:
            closest = min(filter(lambda x: x > number, array))
        else:
            closest = min(filter(lambda x: x >= number, array))

    return(closest)





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