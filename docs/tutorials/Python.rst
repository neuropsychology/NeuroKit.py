Installing Python
#########################


This part focuses on how to get a working, portable distribution of python.

Windows
=============

- **Easy** (300mo)

1. Download a `working winpython <https://drive.google.com/file/d/0B9Wj3n7B5MAtOFdiVnk1UXQyXzA/view?usp=sharing>`_ distribution (includes **NeuroKit 0.1.0** and **Neuropsydia 1.0.3**)
2. Unzip it
3. Open the folder
4. Run `Spyder.exe`

- **Intermediate** (1.5go)

1. Download a non-zero version of `Winython <http://winpython.github.io/>`_
2. Install it somewhere (desktop's a good place). It creates a folder called `WinPython-XXbits-x.x.x.x`
3. In the `WinPython-XXbits-x.x.x.x` folder open `WinPython Command Prompt.exe`
4. Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`
5. Run :code:`pip install https://github.com/neuropsychology/Neuropsydia.py/zipball/master`
6. Run `Spyder.exe`

- **Hard** (300mo)

1. Download the latest `Winython Zero <http://winpython.github.io/>`_
2. Install it somewhere (desktop's a good place). It creates a folder called `WinPython-XXbits-x.x.x.xZero`
3. Download `numpy+mkl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_, `scipy <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_, `scikit-learn <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn>`_ and `cvxopt <http://www.lfd.uci.edu/~gohlke/pythonlibs/#cvxopt>`_ (adapted to your version of python, i.e. 3.4; 3.5 or 3.6) and place them into the `script` subfolder
4. In the `WinPython-XXbits-x.x.x.xZero` folder open `WinPython Command Prompt.exe`
5. Run :code:`pip install numpy --no-index --trusted-host=None --find-links=./`
6. Run :code:`pip install scipy --no-index --trusted-host=None --find-links=./`
7. Run :code:`pip install scikit-learn --no-index --trusted-host=None --find-links=./`
8. Run :code:`pip install cvxopt --no-index --trusted-host=None --find-links=./`
9. Run :code:`pip install PyQt5`
10. Run :code:`pip install pylint==1.6.5`
11. Run :code:`pip install spyder`
12. Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`
13. Run :code:`pip install https://github.com/neuropsychology/Neuropsydia.py/zipball/master`
14. Run `Spyder.exe`

Mac OS
=============

1. Install `Anaconda <https://www.anaconda.com/download/>`_
2. Open the `terminal <https://www.youtube.com/watch?time_continue=59&v=gk2CgkURkgY>`_
3. Run :code:`source activate root`
3. Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`
4. Run :code:`pip install https://github.com/neuropsychology/Neuropsydia.py/zipball/master`
5. Run `Spyder`