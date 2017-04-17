Python and Stuff
#########################

Installation
=============


Windows
-----------------------


1. Download  version `Winython Zero <http://winpython.github.io/>`_.
2. Install it somewhere (desktop's a good place). It creates a folder called `WinPython-XXbits-x.x.x.xZero`.
3. Create an empty folder somewhere (e.g. `d:\temp`).
4. Download `numpy+mkl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_, `scipy <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_, `scikit-learn <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn>`_, `cvxopt <http://www.lfd.uci.edu/~gohlke/pythonlibs/#cvxopt>`_ and place them into the temp directory.
5. In the `WinPython-XXbits-x.x.x.xZero` folder open `WinPython Command Prompt`.
6. Run :code:`run pip install numpy --no-index --trusted-host=None --find-links=d:\temp`.
7. Run :code:`pip install scipy --no-index --trusted-host=None --find-links=d:\temp`.
8. Run :code:`pip install scikit-learn --no-index --trusted-host=None --find-links=d:\temp`.
9. Run :code:`pip install cvxopt --no-index --trusted-host=None --find-links=d:\temp`.
10. Run :code:`pip install PyQt5`.
11. Run :code:`pip install pylint==1.6.5`.
12. Run :code:`pip intall spyder`.
13. Run :code:`pip install https://github.com/neuropsychology/NeuroKit.py/zipball/master`.

