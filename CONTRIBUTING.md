# Contribution Guidelines
**All people are very much welcome to contribute to code, documentation, testing and suggestions.**

## How to submit a change? 
- Check [this page](http://ecole-de-neuropsychologie.readthedocs.io/en/latest/Contributing/Contribute/) to see how to make a commit.
- You don't know how much about code? You can contribute to [documentation](https://github.com/neuropsychology/NeuroKit.py/tree/master/docs) by creating tutorials, help and info!

## Structure
- NeuroKit is currently organized into 5 major sections: Biosignals, M/EEG, statistics, miscellaneous and implementation of several statistical procedures used in psychology/neuroscience. However, this structure might be changed in order to be clarified or expanded (MRI processing, eye tracking, ...).
- API coherence has to be maintained/increased, with functions starting with the same prefix (`find_`, `read_`, `compute_`, `plot_`, `ecg_`, etc.) so that the user can easily find them by typing the "intuitive" prefix.


## Code
- Authors of code contribution will be added within the [**contributor**](http://neurokit.readthedocs.io/en/latest/about.html#contributors) section within the documentation.
- Authors of code contribution are invited to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style sheet to write some nice (and readable) python.
- Please document and comment your code, so that the purpose of each step (or code line) is stated in a clear and understandable way.
- Avoid unnecessary function splitting into smaller bits: it makes testing and reading of the code more difficult (as one must jump between functions and files to understand what's happening).
- Avoid unnecessary use of "magic" functions (preceded by underscores, `_foo()`). I don't know I don't find them elegant. But it's personal. I might be wrong.
