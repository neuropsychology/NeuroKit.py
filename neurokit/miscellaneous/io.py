# -*- coding: utf-8 -*-
import time as builtin_time
import pandas as pd
import numpy as np

import os
import pickle

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
def save_object(raws, filename="file.nk", path=""):
    """
    Save an object to a pickle's file.

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
    with open(path + filename, 'wb') as file:
        pickle.dump(raws, file)
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def load_object(filename, path=""):
    """
    Load a pickle file.

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
    with open(filename, 'rb') as file:
        raws = pickle.load(file)
    return(raws)