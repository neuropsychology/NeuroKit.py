EEG
###

Welcome to the course for EEG processing using ``neurokit``.

Preprocessing
=============


Reading Data 
------------

We have the following directory organization:

- analysis_script.py

- Data/

	- Participant1/
		
		- Participant1_Task.xlsx
		
		- Participant1_Task.eeg
		
		- Participant1_Task.vhdr
		
		- Participant1_Task.vmrk
		

In the ``analysis_script.py`` file, first import the needed modules. Then, load the EEG data in an ``mne`` raw object.


.. code-block:: python

   import neurokit as nk
	
   # Load the participant's file into a raw object
   raw = nk.eeg_load_raw("Participant1_Task",
                  path="Data/Participant1/",
                  eog=('HEOG', 'VEOG'),
                  misc=['PHOTO'],
                  reference=['TP7', 'TP9'])

We can then watch the plot and identify the bad channels by clicking on them (or, by adding their names to the list).

.. code-block:: python

    # Inspect all channels
	raw.plot()
	
	# Mark bad channels
    raw.info['bads'] = []

.. figure:: img/Tuto_EEG_1.png
   :alt: eeg preprocessing channels see plot
   :align: right
   
We can then mark events for further epoching.

.. code-block:: python

    # Add events based on the photo channel and name them accordingly with the task log
	raw, events, event_id = nk.eeg_add_events(raw,
		stim_channel="PHOTO",
		treshold=0.04,
		upper=False,
		number=96,
		events_from_file="Participant1_Task",
		path="Data/Participant1/",
		conditions=["Condition", "Emotion"])
											  
											  
Filtering and Artifact Removal
------------------------------


First, filter the data for ERP. Then, apply an ICA, apply an SSP correction if you want and finally, mark bad eog using a 50ms window.

.. code-block:: python

	# Filter for ERP
	raw_erp = nk.eeg_filter(raw, lowpass=0.1, highpass=50, notch=True, method="iir")
	
	# ICA
	raw_erp = nk.eeg_eog_ica(raw_erp)

	# SSP (uncomment this line to apply this correction)
	# raw = mak.eeg_eog_ssp(raw)

	# Window
	raw_erp = nk.eeg_eog_window(raw_erp)

Then, create epochs of 1s and save them into a file.

.. code-block:: python

	# Epoching
	epochs_erp = nk.eeg_epoching(raw_erp, events, event_id, tmin=-0.2, tmax=1, eog_reject=600e-6, drop_bad=False)

	# Save the epochs
	epochs_erp.save("Data/Participant1/Participant1_erp_epo.fif")

	

	
Event Related Potentials (ERPs)
===============================


Reading Data 
------------

.. code-block:: python

	import neurokit as nk
	import mne

	# Read epochs
	epochs = mne.read_epochs("Data/Participant1/Participant1_erp_epo.fif")
	