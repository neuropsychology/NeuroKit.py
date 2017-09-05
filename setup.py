from setuptools import setup, find_packages
import re


# ------------------
def find_version():
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format("__version__"), open('neurokit/__init__.py').read())
    return result.group(1)
# ------------------



# ------------------
setup(
name = "neurokit",
description = ("A Python Toolbox for Statistics and Signal Processing (EEG, EDA, ECG, EMG...)."),
version = find_version(),
license = "MIT",
author = "Dominique Makowski",
author_email = "dom.makowski@gmail.com",
maintainer = "Dominique Makowski",
maintainer_email = "dom.makowski@gmail.com",
packages = find_packages(),
package_data = {
        "neurokit.materials":["*.model"]},
install_requires = [
        'numpy',
        'pandas',
        'scipy',
        'sklearn',
        'matplotlib',
        'mne',
        'bioread',
        'nolds',
        'biosppy',
        'Pillow',
        'cvxopt'],
dependency_links=[],
long_description = open('README.md').read(),
keywords = "python signal processing EEG EDA ECG hrv rpeaks biosignals complexity",
url = "https://github.com/neuropsychology/NeuroKit.py",
download_url = 'https://github.com/neuropsychology/NeuroKit.py/tarball/master',
test_suite="nose.collector",
tests_require=[
        'nose',
        'coverage'],
classifiers = [
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6']
)
