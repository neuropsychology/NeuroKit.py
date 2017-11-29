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
def save_nk_object(obj, filename="file", path="", extension="nk", compress=False, compatibility=-1):
    """
    Save whatever python object to a pickled file.

    Parameters
    ----------
    file : object
        Whatever python thing (list, dict, ...).
    filename : str
        File's name.
    path : str
        File's path.
    extension : str
        File's extension. Default "nk" but can be whatever.
    compress: bool
        Enable compression using gzip.
    compatibility : int
        See :func:`pickle.dump`.


    Example
    ----------
    >>> import neurokit as nk
    >>> obj = [1, 2]
    >>> nk.save_nk_object(obj, filename="myobject")

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - pickle
    - gzip
    """
    if compress is True:
        with gzip.open(path + filename + "." + extension, 'wb') as name:
            pickle.dump(obj, name, protocol=compatibility)
    else:
        with open(path + filename + "." + extension, 'wb') as name:
            pickle.dump(obj, name, protocol=compatibility)
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
    filename : str
        Full file's name (with extension).
    path : str
        File's path.

    Example
    ----------
    >>> import neurokit as nk
    >>> obj = [1, 2]
    >>> nk.save_nk_object(obj, filename="myobject")
    >>> loaded_obj = nk.read_nk_object("myobject.nk")

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - pickle
    - gzip
    """
    filename = path + filename
    
    try:
        with open(filename, 'rb') as name:
            file = pickle.load(name)
    except pickle.UnpicklingError:
        with gzip.open(filename, 'rb') as name:
            file = pickle.load(name)
    except ModuleNotFoundError:  # In case you're trying to unpickle a dataframe made with pandas < 0.17
        try:
            file = pd.read_pickle(filename)
        except:
            pass
    return(file)

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def find_creation_date(path):
    """
    Try to get the date that a file was created, falling back to when it was last modified if that's not possible.

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
    >>> import datetime
    >>>
    >>> creation_date = nk.find_creation_date(file)
    >>> creation_date = datetime.datetime.fromtimestamp(creation_date)

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_
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