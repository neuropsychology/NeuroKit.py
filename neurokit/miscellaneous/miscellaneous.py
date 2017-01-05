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