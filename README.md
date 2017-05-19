<p align="center"><a href=http://neurokit.readthedocs.io/><img src="https://github.com/neuropsychology/NeuroKit.py/blob/master/docs/img/neurokit.png" width="400" align="center" alt="neurokit python eeg biosignals meg electrophysiology logo"></a></p>

<h2 align="center">Neuroscience made easy!</h2>


# NeuroKit.py 
[![pypi](https://img.shields.io/pypi/pyversions/neurokit.svg)](https://pypi.python.org/pypi/neurokit) [![pypi](https://img.shields.io/pypi/v/neurokit.svg)](https://pypi.python.org/pypi/neurokit) [![](https://travis-ci.org/neuropsychology/NeuroKit.py.svg?branch=master)](https://travis-ci.org/neuropsychology/NeuroKit.py) [![codecov](https://codecov.io/gh/neuropsychology/NeuroKit.py/branch/master/graph/badge.svg)](https://codecov.io/gh/neuropsychology/NeuroKit.py) [![Dependency Status](https://dependencyci.com/github/neuropsychology/NeuroKit.py/badge)](https://dependencyci.com/github/neuropsychology/NeuroKit.py) [![License](https://img.shields.io/pypi/l/neurokit.svg)](https://github.com/neuropsychology/NeuroKit.py/blob/master/LICENSE)

A Python Toolbox for Statistics and Neurophysiological Signal Processing (EEG, EDA, ECG, EMG...).



|Name|NeuroKit|
|----------------|---|
|Documentation|[![Documentation Status](https://readthedocs.org/projects/neurokit/badge/?version=latest)](http://neurokit.readthedocs.io/en/latest/?badge=latest)|
|Discussion|[![Join the chat at https://gitter.im/NeuroKit-py/Lobby](https://img.shields.io/gitter/room/neuropsychology/NeuroKit.py.js.svg)](https://gitter.im/NeuroKit-py/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)|
|Questions|[![](https://img.shields.io/badge/issue-create-purple.svg?colorB=FF9800)](https://github.com/neuropsychology/NeuroKit.py/issues)|
|Authors|[![](https://img.shields.io/badge/CV-D._Makowski-purple.svg?colorB=9C27B0)](https://dominiquemakowski.github.io/)|

---


## Installation

Run the following:

```bash
pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master
```

Not working? [Check this out](http://neurokit.readthedocs.io/en/latest/tutorials/Python.html)!


## Contribute
- You need some help? You found a bug? You would like to request a new feature? 
  Just open an [issue](https://github.com/neuropsychology/NeuroKit.py/issues) :relaxed:
- Want to add a feature? Correct a bug? You're more than welcome to contribute!
  Check [this page](http://ecole-de-neuropsychologie.readthedocs.io/en/latest/Contributing/Contribute/) to see how to submit your changes on github.

## Description

This package provides a high level integration of complex statistical routines for researchers and clinicians with not much experience in programming, statistics or signal theory.

Main features:

- **M/EEG**
  - **[`read_eeg()`](http://neurokit.readthedocs.io/en/latest/documentation.html#read-eeg)**: Read and convert many EEG and MEG files to an [`mne.io.Raw`](http://martinos.org/mne/stable/generated/mne.io.Raw.html#mne.io.Raw) object
  - Preprocessing: Under development
  - ERP: Under development
  - Time/Frequency: Under development
  - Microstates: Under development
- **[Biosignals](http://neurokit.readthedocs.io/en/latest/tutorials/Bio.html)**
  - **[`read_acqknowledge()`](http://neurokit.readthedocs.io/en/latest/documentation.html#read-acqknowledge)**: Load and convert Biopac:copyright:'s AcqKnowledge files to a dataframe
  - **[`ecg_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#ecg-process)**: Extract ECG and RSP features
    - *Heart Rate*
    - *Heart rate variability (HRV) - time and frequency domains*
    - *Cardiac Cycles - R peaks, RR intervals, ...*
    - *Signal quality evaluation*
    - *Respiratory rate and variability*
    - *Respiratory sinus arrhythmia (RSA)*
    - *Complexity (multiscale entropy, fractal dimensions, ...)*
  - **[`eda_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#eda-process)**: Extract Electrodermal Activity (EDA)
    - *Phasic component using the new cvxEDA algorithm ([Greco, 2016](https://www.ncbi.nlm.nih.gov/pubmed/26336110))*
    - *Skin Conductance Responses (SCR) onsets, peaks and amplitudes*
  - **[`emg_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#emg-process)**: Extract EMG features
    - *Pulse onsets*
- **Statistics**
  - **[`z_score()`](http://neurokit.readthedocs.io/en/latest/documentation.html#z-score)**: Normalize (scale and reduce) variables
- **Miscellaneous**
  - **[`complexity()`](http://neurokit.readthedocs.io/en/latest/documentation.html#complexity)**: Extract complexity/chaos indices, such as values of entropy (Shannon's, Sample and Multiscale), fractal dimension, Hurst and Lyapunov exponents and more
  - **[`BMI()`](http://neurokit.readthedocs.io/en/latest/documentation.html#bmi)**: Compute the traditional body mass index (BMI), the new BMI, the Body Fat Percentage (BFP) and their interpretation






## Documentation

- [Tutorials](http://neurokit.readthedocs.io/en/latest/tutorials/index.html)
  - [x] Biosignals processing
  - [ ] M/EEG processing
- [API Documentation](http://neurokit.readthedocs.io/en/latest/documentation.html)


## Citation
You can cite NeuroKit with the following:
```
Makowski, D. (2016). NeuroKit: A Python Toolbox for Statistics and Neurophysiological Signal Processing (EEG, EDA, ECG, EMG...).
Memory and Cognition Lab' Day, 01 November, Paris, France
```
*Note: The authors do not give any warranty. If this software causes your keyboard to blow up, your brain to liquefy, your toilet to clog or a zombie plague to leak, the authors CANNOT IN ANY WAY be held responsible.*

## Credits
Note that important credits go to the developpers of the many packages upon which NeuroKit is built. Those include [mne](http://mne-tools.github.io/stable/index.html), [bioSPPy](https://github.com/PIA-Group/BioSPPy), [hrv](https://github.com/rhenanbartels/hrv), [bioread](https://github.com/njvack/bioread)... Make sure you cite them!
