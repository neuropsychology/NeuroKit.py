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

.. image:: picture.jpeg
   :scale: 50 %
   :alt: eeg preprocessing channels
   :align: right