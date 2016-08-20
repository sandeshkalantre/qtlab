:: qtlabgui.bat
:: Runs QTlab GUI part on Windows

@ECHO OFF

:: If using a separate GTK install (and not the one provided in the
:: pygtk-all-in-one installer), uncomment and adjust the following
:: two lines to point to the appropriate locations
::SET GTK_BASEPATH=%CD%\3rd_party\gtk
::SET PATH=%CD%\3rd_party\gtk\bin;%CD%\3rd_party\gtk\lib;%PATH%

:: Add Console2 to PATH
SET PATH=%CD%\3rd_party\Console2\;%PATH%

:: Check for version of python
IF EXIST C:\Users\mbelab\AppData\Local\Enthought\Canopy32\User\Scripts\python.exe (
    SET PYTHON_PATH=C:\Users\mbelab\AppData\Local\Enthought\Canopy32\User\Scripts
    GOTO mark1
)
IF EXIST c:\python26\python.exe (
    SET PYTHON_PATH=c:\python26
    GOTO mark1
)
:mark1

:: Run QTlab GUI
start Console -w "QTLab GUI" -r "/k %PYTHON_PATH%\python.exe clients/client_gtk.py --module gui_client --config gui_client.cfg %*"

:: Use this for easier debugging
::start %PYTHON_PATH%\python.exe clients/client_gtk.py --module gui_client --config gui_client.cfg %*
