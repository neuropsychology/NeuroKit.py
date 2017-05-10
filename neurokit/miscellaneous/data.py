# -*- coding: utf-8 -*-
import time as builtin_time
import pandas as pd
import numpy as np

import platform
import os
import pickle
import gzip

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
def save_nk_object(file, filename="file", path="", extension="nk", compress=False, compatibility=-1):
    """
    Save an object to a pickled file.

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
    - pickle
    """
    if compress is True:
        with gzip.open(path + filename + "." + extension, 'wb') as name:
            pickle.dump(file, name, protocol=compatibility)
    else:
        with open(path + filename + "." + extension, 'wb') as name:
            pickle.dump(file, name, protocol=compatibility)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def read_nk_object(filename, path=""):
    """
    Read a pickled file.

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
    - pickle
    """
    try:
        with open(filename, 'rb') as name:
            file = pickle.load(name)
    except pickle.UnpicklingError:
        with gzip.open(filename, 'rb') as name:
            file = pickle.load(name)
    return(file)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def get_creation_date(path):
    """
    Try to get the date that a file was created, falling back to when it was last modified if that not possible.
    See  for explanation.

    Parameters
    ----------
    path : str
       File's path.

    Returns
    ----------
    creation_date : str
        Time of file creation.


    Example
    ----------
    >>> import neurokit as nk
    >>>
    >>> date = nk.get_creation_date(file)

    Notes
    ----------
    *Authors*

    - Dominique Makowski (https://github.com/DominiqueMakowski)
    - Mark Amery

    *Dependencies*

    - platform
    - os

    *See Also*

    - http://stackoverflow.com/a/39501288/1709587

    """
    if platform.system() == 'Windows':
        return(os.path.getctime(path))
    else:
        stat = os.stat(path)
        try:
            return(stat.st_birthtime)
        except AttributeError:
            print("Neuropsydia error: get_creation_date(): We're probably on Linux. No easy way to get creation dates here, so we'll settle for when its content was last modified.")
            return(stat.st_mtime)