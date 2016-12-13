EEG
###

Welcome to the course for EEG processing using ``neurokit``.

Reading Data 
============

First, import the needed modules.


.. code-block:: python

   # Load the participant's file into a raw object
   raw = nk.eeg_load_raw("Participant1_Task",
                  path="Data/Participant1/",
                  eog=('HEOG', 'VEOG'),
                  misc=['PHOTO'],
                  reference=['TP7', 'TP9'])

We can then watch the plot and identify the bad channels by clicking on them.

.. code-block:: python

    # Inspect all channels
	raw.plot()

.. figure:: img/Tuto_EEG_1.png
   :alt: eeg preprocessing channels see plot
   :align: right