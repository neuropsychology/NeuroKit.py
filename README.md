<p align="center"><a href=http://neurokit.readthedocs.io/en/latest/?badge=latest><img src="https://github.com/neuropsychology/NeuroKit.py/blob/master/docs/img/neurokit.png" width="400" align="center" alt="neurokit python eeg biosignals meg electrophysiology logo"></a></p>

<h2 align="center">Neuroscience made easy!</h2>


# NeuroKit.py 
A Python Toolbox for Statistics and Neurophysiological Signal Processing (EEG, EDA, ECG, EMG...).





|Name|NeuroKit|
|----------------|---|
|Latest Version|[![](https://img.shields.io/badge/version-0.0.8-brightgreen.svg)](https://pypi.python.org/pypi/neurokit)|
|Documentation|[![Documentation Status](https://readthedocs.org/projects/neurokit/badge/?version=latest)](http://neurokit.readthedocs.io/en/latest/?badge=latest)|
|Discussion|[![Join the chat at https://gitter.im/NeuroKit-py/Lobby](https://badges.gitter.im/NeuroKit-py/Lobby.svg)](https://gitter.im/NeuroKit-py/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)|
|Questions|[![](https://img.shields.io/badge/issue-create-purple.svg?colorB=FF9800)](https://github.com/neuropsychology/NeuroKit.py/issues)|
|Authors|[![](https://img.shields.io/badge/CV-D._Makowski-purple.svg?colorB=9C27B0)](https://cdn.rawgit.com/neuropsychology/Organization/master/CVs/DominiqueMakowski.pdf)|

---

**Warning: This package is under development.**

## Installation

Run the following:

```bash
pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master
```

## Contribute
- You need some help? You found a bug? You would like to request a new feature? 
  Just open an [issue](https://github.com/neuropsychology/NeuroKit.py/issues) :relaxed:
- Want to add a feature? Correct a bug? You're more than welcome to contribute!
  Check [this page](http://ecole-de-neuropsychologie.readthedocs.io/en/latest/Contributing/Contribute/) to see how to submit your changes on github.

## Description

This package provides a high level integration of complex statistical routines for researchers and clinicians with not much experience in programming, statistics or signal theory.

Main features:

- **M/EEG**
  - **`read_eeg()`**: Under development
  - Preprocessing: Under development
  - Filtering: Under development
  - Microstates: Under development
- **[Biosignals](http://neurokit.readthedocs.io/en/latest/tutorials/Bio.html)**
  - **`read_acqknowledge()`**: Load and convert Biopac:copyright:'s AcqKnowledge files to a `pandas`' dataframe
  - **`ecg_process()`**: Extract ECG and RSP features (R peaks, Heart rate, Heart rate variability (HRV))
  - **`eda_process()`**: Extract Electrodermal Activity (EDA) features (phasic component using the new cvxEDA algorithm ([Greco, 2016](https://www.ncbi.nlm.nih.gov/pubmed/26336110)), Skin Conductance Response's (SCR) onsets, peaks and amplitudes)
- **Statistics**
  - **`z_score()`**: Normalize (scale and reduce) variables
- **Miscellaneous**
  - **`fractal_dimensions()`**: Extract Fractal dimensions, chaos and entropy features
  - **`BMI()`**: Computes the traditional body mass index (BMI), the new BMI, the Body Fat Percentage (BFP) and their interpretation






## Examples


#### ECG, RSP and EDA processing with a Biopac:copyright:'s Acqknowledge file (See [this example](http://neurokit.readthedocs.io/en/latest/tutorials/Bio.html)).
```python
import neurokit as nk
import pandas as pd

# Read the data file
acq = nk.read_acqknowledge("myfile.acq")

# Processing
bio = nk.bio_process(ecg=acq["ECG, X, RSPEC-R"], rsp=acq["RSP, X, RSPEC-R"], eda=acq["EDA, X, PPGED-R"])
bio["Bio"].plot()
```


#### Fractal/chaos/entropy indices computation
```python
import neurokit as nk
signal = [5, 1, 7, 2, 5, 1, 7, 4, 6, 7, 5, 4, 1, 1, 4, 4]
results = nk.fractal_dimensions(signal)
print(results["Entropy"])
```

#### Z-scores
```python
import neurokit as nk
raw_scores = [1, 2, 8, 6, 2, 4]
z_scores = nk.z_score(raw_scores)
```

#### Body Mass Index (BMI)
```python
import neurokit as nk
nk.BMI(height=166, weight=54, age=22, sex="f")
```



## Citation
You can cite NeuroKit with the following:
```
Makowski, D. (2016). NeuroKit: A Python Toolbox for Statistics and Neurophysiological Signal Processing (EEG, EDA, ECG, EMG...).
Memory and Cognition Lab' Day, 01 November, Paris, France
```
*Note: The authors do not give any warranty. If this software causes your keyboard to blow up, your brain to liquefy, your toilet to clog or a zombie plague to leak, the authors CANNOT IN ANY WAY be held responsible.*

## Credits
Note that important credits go to the developpers of the many packages upon which NeuroKit is built. Those include, among others, [mne](http://mne-tools.github.io/stable/index.html) (M/EEG), [bioSPPy](https://github.com/PIA-Group/BioSPPy) (bio), [hrv](https://github.com/rhenanbartels/hrv) (ecg), [bioread](https://github.com/njvack/bioread) (bio)... Make sure you cite them!
