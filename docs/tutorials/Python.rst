Python and Stuff
#########################

Installation
=============


Windows
-----------------------


1. Download winpython Zero version
2. Install it somewhere (desktop's a good place). It creates a folder called `WinPython-XXbits-x.x.x.xZero`
3. Create an empty folder somewhere (e.g. `d:\temp`)
Download numpy+mkl, scipy and scikit-learn and place them into the temp directory

3. In the created folder open the winpython command prompt


Download other packages
pip download --dest d:\temp PyQt5
pip download --dest d:\temp matplotlib
pip download --dest d:\temp pandas
pip download --dest d:\temp spyder
Install them
run pip install numpy --no-index --trusted-host=None --find-links=d:\temp
run pip install scipy --no-index --trusted-host=None --find-links=d:\temp
run pip install scikit-learn --no-index --trusted-host=None --find-links=d:\temp
run pip install PyQt5 --no-index --trusted-host=None --find-links=d:\temp
run pip install matplotlib --no-index --trusted-host=None --find-links=d:\temp
run pip install pandas --no-index --trusted-host=None --find-links=d:\temp
run pip install spyder --no-index --trusted-host=None --find-links=d:\temp


