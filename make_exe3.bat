# download 'Winpython64-3.7.6.0.exe' installer
# run it and allow it to extract to your desktop
# this will put a 'WPy64-3760' folder on your desktop.
# in windows explorer prwse into that folder then double-click the 'WinPython Command Prompt.exe' to open a special cmd.exe dos box...
# assuming u started inside the above 'WinPython Command Prompt.exe' dos box before u run this .bat file...
# cd to the folder where the 'gui_tool' cloned from rfdesign's git hub repo exists
# run this file  'make_exe.bat'

# note, first we uninstall a bunch of big/scary pip/python packages that we defineitely do not want to bundle in the .exe
# this helps as sometimes the pyinstaller dependancies get carried away and  bundle too much.  it can't bundle if its not installed

pip install pyinstaller

# get newest cx_freeze as canned-in version can have issues.
pip uninstall -y cx_freeze
pip install wheel
pip install -y cx_freeze

#pip uninstall -y numpy
#pip uninstall -y scipy
pip uninstall -y numba
#pip uninstall -y matplotlib
pip uninstall -y numexpr
pip uninstall -y zmq
pip uninstall -y scikit-learn
pip uninstall -y seaborn
pip uninstall -y scs
pip uninstall -y tables
pip uninstall -y wordcloud

pip uninstall -y pandas
pip uninstall -y mizani
pip uninstall -y keras-vis
pip uninstall -y keras
pip uninstall -y sphinx
pip uninstall -y tcl
pip uninstall -y statsmodels
pip uninstall -y scikit-optimize
pip uninstall -y quantecon
pip uninstall -y pygbm
pip uninstall -y pyflux
pip uninstall -y plotnine
pip uninstall -y pdvega
pip uninstall -y mlxtend
pip uninstall -y imbalanced-learn
pip uninstall -y datashader
pip uninstall -y dask-searchcv
pip uninstall -y cvxpy
pip uninstall -y astroml

pip install  numpy

echo you may delete \build and \dist folders if there are errors
del dist\
del build\

copy uavcan_gui_tool.spec.good uavcan_gui_tool.spec

#pyinstaller --log-level=DEBUG --clean --noconfirm -d all --onedir uavcan_gui_tool.spec 
pyinstaller --noconfirm --onedir -d all --clean uavcan_gui_tool.spec

# make installer from binaries with NSIS
"C:\Program Files (x86)\NSIS\makensisw.exe" "UAVCAN GUI Tool2.nsi"
