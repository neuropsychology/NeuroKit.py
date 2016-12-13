EEG
###

Welcome to the course for EEG processing using ``neurokit``.

Reading Data 
============

First, import the needed modules.


.. code-block:: python

    raw = nt.load_raw(example_participant,
    			   path="Data/",
    			   reference=['TP7', 'TP9'],
    			   eog=('HEOG', 'VEOG'),
	    		   misc=['PHOTO'])

.. figure:: Tuto_EEG_1.png
   :target: https://github.com/neuropsychology/NeuroKit.py/blob/master/docs/img/Tuto_EEG_1.png
   :scale: 50 %
   :alt: eeg preprocessing channels
   :align: right