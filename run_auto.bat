@echo off
REM Executes the script in AUTOMATIC mode. Drag a PDF onto this file.

echo --- Pre-Execution Info (Automatic Mode) ---
echo Script Directory: %~dp0
echo Dropped File: %1
echo ---

echo Executing Python script in Automatic Mode...
REM This is the corrected line.
REM Using "%~1" removes any quotes that Windows may have added to the path
REM before wrapping it in our own. This ensures paths with spaces are
REM always handled correctly as a single argument.
python "%~dp0\pdfpy.py" "%~1"

echo.
echo Script execution finished.
pause

