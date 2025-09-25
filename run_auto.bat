@echo off
REM Executes the script in AUTOMATIC mode. Drag a PDF onto this file.

echo --- Pre-Execution Info (Automatic Mode) ---
echo Script Directory: %~dp0
echo Dropped File: %1
echo ---

pushd "%~dp1"
if errorlevel 1 (
echo ERROR: Could not change to directory '%~dp1'.
pause
exit /b
)

echo Executing Python script in Automatic Mode...
python "%~dp0\pdfpy.py" "%~nx1"

echo.
echo Script execution finished.
popd
pause