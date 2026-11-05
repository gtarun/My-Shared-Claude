@echo off
setlocal DisableDelayedExpansion
set "PYTHONUTF8=1"
if not exist "%~dp0claude-session-sharing.py" (
  echo The Python helper is missing. Extract the whole ZIP and keep its files together.
  pause
  exit /b 1
)
py -3 -c "import sys; raise SystemExit(sys.version_info.__lt__((3, 9)))" >nul 2>nul
if not errorlevel 1 goto use_py
python -c "import sys; raise SystemExit(sys.version_info.__lt__((3, 9)))" >nul 2>nul
if not errorlevel 1 goto use_python
echo Python 3.9 or newer is required.
echo Install Python from https://www.python.org/downloads/windows/ or ask IT, then try again.
pause
exit /b 1

:use_py
py -3 "%~dp0claude-session-sharing.py" menu
goto finished

:use_python
python "%~dp0claude-session-sharing.py" menu

:finished
if errorlevel 1 (
  echo.
  echo The command did not finish. Read the message above before trying again.
  pause
  exit /b 1
)
exit /b 0
