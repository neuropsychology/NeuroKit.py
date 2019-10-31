:warning:**The [NeuroKit2 project](https://github.com/neuropsychology/NeuroKit) has just started!** Better, stronger, faster, feel free to join in the community [here](https://github.com/neuropsychology/NeuroKit/issues/3) :warning:

<p align="center"><a href=http://neurokit.readthedocs.io/><img src="https://github.com/neuropsychology/NeuroKit.py/blob/master/docs/img/neurokit.png" width="400" align="center" alt="neurokit python eeg biosignals meg electrophysiology logo"></a></p>

<h2 align="center">Neuroscience made easy!</h2>


# NeuroKit.py
[![pypi](https://img.shields.io/pypi/pyversions/neurokit.svg)](https://pypi.python.org/pypi/neurokit)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d5248bd8c8574e90b5c8fe0bf2030201)](https://www.codacy.com/app/DominiqueMakowski/NeuroKit.py?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=neuropsychology/NeuroKit.py&amp;utm_campaign=Badge_Grade)
[![pypi](https://img.shields.io/pypi/v/neurokit.svg)](https://pypi.python.org/pypi/neurokit)
[![travis](https://travis-ci.org/neuropsychology/NeuroKit.py.svg?branch=master)](https://travis-ci.org/neuropsychology/NeuroKit.py)
[![codecov](https://codecov.io/gh/neuropsychology/NeuroKit.py/branch/master/graph/badge.svg)](https://codecov.io/gh/neuropsychology/NeuroKit.py)
[![Dependency Status](https://dependencyci.com/github/neuropsychology/NeuroKit.py/badge)](https://dependencyci.com/github/neuropsychology/NeuroKit.py)
[![License](https://img.shields.io/pypi/l/neurokit.svg)](https://github.com/neuropsychology/NeuroKit.py/blob/master/LICENSE)
[![Build status](https://ci.appveyor.com/api/projects/status/9w4qw55143xu1gei?svg=true)](https://ci.appveyor.com/project/DominiqueMakowski/neurokit-py)
[![Code Health](https://landscape.io/github/neuropsychology/NeuroKit.py/master/landscape.svg?style=flat)](https://landscape.io/github/neuropsychology/NeuroKit.py/master)
[![HitCount](http://hits.dwyl.io/neuropsychology/neuropsychology/neurokit.py.svg)](http://hits.dwyl.io/neuropsychology/neuropsychology/neurokit.py)

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
[![Maintainability](https://api.codeclimate.com/v1/badges/e4ac002d93a655bf61c1/maintainability)](https://codeclimate.com/github/neuropsychology/NeuroKit.py/maintainability)

Want to get involved in the developpment of an open-source software and improve neuroscience practice? **Join us!**

- You need some help? You found a bug? You would like to request a new feature?
  Just open an [issue](https://github.com/neuropsychology/NeuroKit.py/issues) :relaxed:
- Want to add a feature? Correct a bug? You're more than welcome to contribute!
  Check [this page](https://github.com/neuropsychology/NeuroKit.py/blob/master/CONTRIBUTING.md) to see how to submit your changes on github.

## Documentation

- [Tutorials](http://neurokit.readthedocs.io/en/latest/tutorials/index.html)
  - [x] Biosignals processing
  - [ ] M/EEG processing
- [API Documentation](http://neurokit.readthedocs.io/en/latest/documentation.html)


## Features

This package provides a high level integration of complex statistical routines for researchers and clinicians with not much experience in programming, statistics or signal theory.

- **[M/EEG](http://neurokit.readthedocs.io/en/latest/tutorials/EEG.html)** *(under developpment)*
  - **[`eeg_erp()`](http://neurokit.readthedocs.io/en/latest/documentation.html#eeg_erp)**: Extract event-related potentials
  - **[`eeg_complexity()`](http://neurokit.readthedocs.io/en/latest/documentation.html#eeg_complexity)**: Compute entropy, fractal dimension, and complexity indices
  - Time/Frequency: **SOON**
  - Microstates: **SOON**
- **[Biosignals](http://neurokit.readthedocs.io/en/latest/tutorials/Bio.html)**
  - **[`read_acqknowledge()`](http://neurokit.readthedocs.io/en/latest/documentation.html#read-acqknowledge)**: Load and convert Biopac:copyright:'s AcqKnowledge files to a dataframe
  - **[`ecg_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#ecg-process)**: Extract ECG features
    - *Heart Rate*
    - *Heart rate variability (HRV) - time, frequency and nonlinear domains*
    - *Cardiac Cycles - R peaks, RR intervals, P, Q, T Waves, ...*
    - *Cardiac Phase (systole/diastole)*
    - *Signal quality evaluation*
    - *Respiratory sinus arrhythmia (RSA) - P2T method*
    - *Complexity (multiscale entropy, fractal dimensions, ...)*
  - **[`rsp_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#ecg-process)**: Extract Respiratory features
    - *Respiratory rate and variability*
    - *Respiratory phase (inspiration/expiration)*
    - *Respiratory cycles characteristics (onsets, length, ...)*
  - **[`eda_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#eda-process)**: Extract Electrodermal Activity (EDA)
    - *Tonic and phasic components using the new cvxEDA algorithm ([Greco, 2016](https://www.ncbi.nlm.nih.gov/pubmed/26336110))*
    - *Skin Conductance Responses (SCR) onsets, peaks, amplitudes, latencies, recovery times, ...*
  - **[`emg_process()`](http://neurokit.readthedocs.io/en/latest/documentation.html#emg-process)**: Extract EMG features
    - *Pulse onsets*
    - *Linear envelope, muscle activation*
- **Signal**
    - **[`complexity()`](http://neurokit.readthedocs.io/en/latest/documentation.html#complexity)**: Extract complexity/chaos indices, such as values of entropy (Shannon's, Sample and Multiscale), fractal dimension, Hurst and Lyapunov exponents and more
- **Statistics**
  - **[`z_score()`](http://neurokit.readthedocs.io/en/latest/documentation.html#z-score)**: Normalize (scale and reduce) variables
  - **[`find_outliers()`](http://neurokit.readthedocs.io/en/latest/documentation.html#find_outliers)**: Identify outliers
- **Miscellaneous**
  - **[`compute_dprime()`](http://neurokit.readthedocs.io/en/latest/documentation.html#compute_dprime)**: Computes Signal Detection Theory (SDT) parameters (d', c, beta, a', b''d)
  - **[`compute_BMI()`](http://neurokit.readthedocs.io/en/latest/documentation.html#compute_bmi)**: Compute the traditional body mass index (BMI), the new BMI, the Body Fat Percentage (BFP) and their interpretation
  - **[`compute_interoceptive_accuracy()`](http://neurokit.readthedocs.io/en/latest/documentation.html#compute_interoceptive_accuracy)**: Compute interoception accuracy according to Garfinkel et al., (2015).


## Citation
You can cite NeuroKit with the following:
```
Makowski, D. (2016). NeuroKit: A Python Toolbox for Statistics and Neurophysiological Signal Processing (EEG, EDA, ECG, EMG...).
Memory and Cognition Lab' Day, 01 November, Paris, France
```
*Note: The authors do not give any warranty. If this software causes your keyboard to blow up, your brain to liquefy, your toilet to clog or a zombie plague to leak, the authors CANNOT IN ANY WAY be held responsible.*

## Credits
Note that important credits go to the developpers of the many packages upon which NeuroKit is built. Those include [mne](http://mne-tools.github.io/stable/index.html), [bioSPPy](https://github.com/PIA-Group/BioSPPy), [hrv](https://github.com/rhenanbartels/hrv), [bioread](https://github.com/njvack/bioread)... Make sure you cite them!
