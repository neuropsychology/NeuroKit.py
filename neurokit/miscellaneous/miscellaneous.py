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

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

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

        Notes
        ----------
        *Authors*

        - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

        *Dependencies*

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

        Notes
        ----------
        *Authors*

        - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

        *Dependencies*

        - time
        """
        t = (builtin_time.clock()-self.clock)*1000

        if reset is True:
            self.reset()
        return(t)








