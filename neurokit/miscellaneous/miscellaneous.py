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
def read_data(filename, extension="", participant_id="", path="", localization="US", print_warning=True):
    """
    Load the datafile into a pandas' dataframe.

    Parameters
    ----------
    NA

    Returns
    ----------
    NA

    Example
    ----------
    NA

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - pandas
    """
    # Find a corresponding file
    file = filename
    if os.path.isfile(file) is False:
        file = path + filename + extension
    if os.path.isfile(file) is False:
        file = path + filename + ".xlsx"
    if os.path.isfile(file) is False:
        file = path + filename + ".csv"
    if os.path.isfile(file) is False:
        file = path + participant_id + filename + extension
    if os.path.isfile(file) is False:
        if ".csv" in file:
            file = path + "/csv/" + participant_id + "_" + filename + extension
        elif ".xlsx" in file:
            file = path + "/excel/" + participant_id + "_" + filename + extension
        else:
            extension = ".xlsx"
    if os.path.isfile(file) is False:
        if print_warning is True:
            print("NeuroKit Error: read_data(): file's path " + file + " not found!")

    if localization == "FR" or localization == "FRA" or localization == "French" or localization == "France":
        sep = ";"
        decimal = ","
    else:
        sep = ","
        decimal = "."

    if ".csv" in file:
        try:
            df = pd.read_csv(file, sep=sep, decimal=decimal, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file, sep=sep, decimal=decimal, encoding="cp1125")
    elif ".xls" in file or ".xlsx" in file:
        df = pd.read_excel(file, encoding="utf-8")
    else:
        if print_warning is True:
            print("NeuroKit Error: read_data(): wrong extension of the datafile.")
    return(df)


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def save_data(df, filename="data", extension="all", participant_id="", path="", localization="US", index=False, print_warning=True, index_label=None):
    """
    Save the datafile into a pandas' dataframe.

    Parameters
    ----------
    NA

    Returns
    ----------
    NA

    Example
    ----------
    NA

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - pandas
    """
    if localization == "FR" or localization == "FRA" or localization == "French" or localization == "France":
        sep = ";"
        decimal = ","
    else:
        sep = ","
        decimal = "."

    if extension == "all":
        extension = [".csv", ".xlsx"]

    for ext in list(extension):
        if ext == ".csv":
            if os.path.exists(path + "/csv/") is False:
                os.makedirs(path + "/csv/")
            df.to_csv(path + "/csv/" + participant_id + "_" + filename + ext, sep=sep, index=index, index_label=index_label, decimal=decimal, encoding="utf-8")
        elif ext == ".xlsx":
            if os.path.exists(path + "/excel/") is False:
                os.makedirs(path + "/excel/")
            df.to_excel(path + "/excel/" + participant_id + "_" + filename + ext, index=index, index_label=index_label, encoding="utf-8")
        else:
            if print_warning is True:
                print("NeuroKit Error: save_data(): wrong extension specified.")

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
    index = 0
    while index != len(mylist):
        uniques.append(True)
        try:
            while mylist[index] == mylist[index+1]:
                uniques.append(False)
                mylist.pop(index+1)
        except:  # When index out of range
            pass
        index += 1

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