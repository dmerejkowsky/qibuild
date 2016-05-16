# CMake and Python2.7 (32bits) are already installed
# pip:

$GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
$GET_PIP_PATH = "C:\get-pip.py"

$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile($GET_PIP_URL, $GET_PIP_PATH)
python $GET_PIP_PATH

# swig
$SWIG_URL = "http://downloads.sourceforge.net/project/swig/swigwin/swigwin-3.0.8/swigwin-3.0.8.zip"
$SWIG_ZIP_PATH = "C:\swig.zip"
$SWIG_PATH = "C:\swig"
$webclient.DownloadFile($SWIG_URL, $SWIG_ZIP_PATH)
7z x $SWIG_ZIP_PATH -O$SWIG_PATH

# doxygen
$DOXYGEN_URL = "http://downloads.sourceforge.net/project/doxygen/snapshots/doxygen-1.8-svn/windows/doxygenw20140924_1_8_8.zip"
$DOXYGEN_ZIP_PATH = "C:\doxgyen.zip"
$webclient.DownloadFile($DOXYGEN_URL, $DOXYGEN_ZIP_PATH)
7z x $DOXYGEN_ZIP_PATH -O$DOXYGEN_PATH
