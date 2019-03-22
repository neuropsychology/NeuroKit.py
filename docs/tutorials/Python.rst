Installing Python
#########################


This part focuses on how to get a working, portable distribution of python.

Windows
=============

- **Easy** (1.5go)

1. Download a `working winpython <https://drive.google.com/open?id=1TZbJ_PO8tbdOVtXHTYXHJEuEQ6pLJsie>`_ distribution (includes **Python 3.7**, **NeuroKit 0.2.7** and **Neuropsydia 1.0.6**)
2. Unzip it
3. Open the folder
4. Run `Spyder.exe`

- **Intermediate** (> 1.5go)

1. Download a non-zero version of `Winython <http://winpython.github.io/>`_
2. Install it somewhere (desktop's a good place). It creates a folder called `WinPython-XXbits-x.x.x.x`
3. In the `WinPython-XXbits-x.x.x.x` folder open `WinPython Command Prompt.exe`
4. Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`
5. Run :code:`pip install https://github.com/neuropsychology/Neuropsydia.py/zipball/master`
6. Launch `Spyder.exe`

- **Hard** (1.5go)

1. Download the latest `Winython Zero <http://winpython.github.io/>`_
2. Install it somewhere (desktop's a good place). It creates a folder called `WinPython-XXbits-x.x.x.xZero` (or `WPy-xxxx`)
3. Download the following files (adapted to your version of python, e.g. 3.7 and whether it's a 32 or 64 bits distribution) and place them into the `script` subfolder:
    - `numpy+mkl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_
    - `scipy <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_
    - `scikit-learn <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn>`_
    - `cvxopt <http://www.lfd.uci.edu/~gohlke/pythonlibs/#cvxopt>`_ 
    - `kiwisolver <http://www.lfd.uci.edu/~gohlke/pythonlibs/#kiwisolver>`_ 
    - `cycler <http://www.lfd.uci.edu/~gohlke/pythonlibs/#cycler>`_ 
    - `matplotlib <http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib>`_ 
    
4. In the `WinPython-XXbits-x.x.x.xZero` (or `WPy-xxxx`) folder open `WinPython Command Prompt.exe` and run the following:
    - Run :code:`pip install numpy --no-index --trusted-host=None --find-links=./`
    - Run :code:`pip install scipy --no-index --trusted-host=None --find-links=./`
    - Run :code:`pip install scikit-learn --no-index --trusted-host=None --find-links=./`
    - Run :code:`pip install cvxopt --no-index --trusted-host=None --find-links=./`
    - Run :code:`pip install kiwisolver --no-index --trusted-host=None --find-links=./`
    - Run :code:`pip install cycler --no-index --trusted-host=None --find-links=./`
	- Run :code:`pip install dateutils`
	- Run :code:`pip install pyparsing`
    - Run :code:`pip install matplotlib --no-index --trusted-host=None --find-links=./`
    - Run :code:`pip install PyQt5`
    - Run :code:`pip install pylint`
    - Run :code:`pip install spyder`
    - Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`
    - Run :code:`pip install https://github.com/neuropsychology/Neuropsydia.py/zipball/master`
    
10. Launch `Spyder.exe`

Mac OS
=============

1. Install `Anaconda <https://www.anaconda.com/download/>`_
2. Open the `terminal <https://www.youtube.com/watch?time_continue=59&v=gk2CgkURkgY>`_
3. Run :code:`source activate root`
4. Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`
5. Run :code:`pip install https://github.com/neuropsychology/Neuropsydia.py/zipball/master`
6. Launch `Spyder.exe`