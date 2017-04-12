# -*- coding: utf-8 -*-
import time as builtin_time
import pandas as pd
import numpy as np

import os
import platform


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
    Dominique Makowski

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
        Dominique Makowski

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
        Dominique Makowski

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
def find_following_duplicates(mylist):
    """
    Find the duplicates that are following themselves.

    Parameters
    ----------
    mylist =  list
        A list.

    Returns
    ----------
    list
        A list containing True for each unique and False for following duplicates.

    Example
    ----------
    >>> import neurokit as nk
    >>> mylist = ["a","a","b","a","a","a","c","c","b","b"]
    >>> nk.remove_following_duplicates(mylist)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
    """
    mylist = mylist.copy()


    uniques = []
    for i in range(len(mylist)):
        if i == 0:
            uniques.append(True)
        else:
            if mylist[i] == mylist[i-1]:
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
def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.

    Parameters
    ----------
    path_to_file =  str
        The path

    Returns
    ----------
    creation_date

    Example
    ----------
    >>> import neurokit as nk
    >>> date = nk.get_creation_date(path)

    Authors
    ----------
    Mark Amery

    Dependencies
    ----------
    - os
    - platform
    """
    if platform.system() == 'Windows':
        return(os.path.getctime(path_to_file))
    else:
        stat = os.stat(path_to_file)
        try:
            return(stat.st_birthtime)
        except AttributeError:
            print("Neuropsydia error: get_creation_date(): We're probably on Linux. No easy way to get creation dates here, so we'll settle for when its content was last modified.")
            return(stat.st_mtime)



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def closest_in_list(number, array, direction="both", strictly=False):
    """
    Find the closest number in the array from x.

    Parameters
    ----------
    number =  float
        The number.
    array = list
        The list to look in.
    direction = str
        "both" for smaller or greater, "greater" for only greater numbers and "smaller" for the closest smaller.
    strictly = bool
        False for stricly superior or inferior or True for including equal.

    Returns
    ----------
    closest = int

    Example
    ----------
    >>> import neurokit as nk
    >>> array = [3, 5, 6, 1, 2]
    >>> nk.find_closest_in_list(1.8, array)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
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
    Returns the traditional BMI, the 'new' Body Mass Index (BMI, see https://people.maths.ox.ac.uk/trefethen/bmi.html) and estimates the Body Fat Percentage (BFP;, Deurenberg, 1991)


    Parameters
    ----------
    height =  float
        Height in cm.
    weight = float
        Weight in kg.
    age = float
        Age in years.
    sex = str
        "m" or "f".


    Returns
    ----------
    bmi = dict
        dict containing values and their interpretations.

    Example
    ----------
    >>> import neurokit as nk
    >>> nk.BMI(182, 55)

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    None
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
        if 2 <= bmi["BFP"] <= 5:
            bmi["BFP_category"] = "Essential"
        if 6 <= bmi["BFP"] <= 12:
            bmi["BFP_category"] = "Athletic"
        if 13 <= bmi["BFP"] <= 16:
            bmi["BFP_category"] = "Fitness"
        if 17 <= bmi["BFP"] <= 21:
            bmi["BFP_category"] = "Average"
        if 22 <= bmi["BFP"] <= 29:
            bmi["BFP_category"] = "Overweight"
        if bmi["BFP"] > 29:
            bmi["BFP_category"] = "Obese"
    else:
        if bmi["BFP"] < 10:
            bmi["BFP_category"] = "Critical"
        if 10 <= bmi["BFP"] <= 13:
            bmi["BFP_category"] = "Essential"
        if 14 <= bmi["BFP"] <= 20:
            bmi["BFP_category"] = "Athletic"
        if 21 <= bmi["BFP"] <= 24:
            bmi["BFP_category"] = "Fitness"
        if 25 <= bmi["BFP"] <= 30:
            bmi["BFP_category"] = "Average"
        if 31 <= bmi["BFP"] <= 39:
            bmi["BFP_category"] = "Overweight"
        if bmi["BFP"] > 40:
            bmi["BFP_category"] = "Obese"



    return(bmi)