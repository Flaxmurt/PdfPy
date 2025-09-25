@echo off
REM Executes the script in MANUAL mode. Drag a PDF onto this file.

if "%~1"=="" (
echo ERROR: To use this script, drag and drop a single PDF file onto it.
pause
exit /b
)

echo --- PDFPy Manual Splitter ---
echo.
echo Processing file: %~nx1
echo.

echo Please enter the starting page number for each chapter, separated by commas.
set /p pages="Example: 5,10,56,85,125: "
if "%pages%"=="" (
echo ERROR: No page numbers were entered. Aborting.
pause
exit /b
)
echo.

REM Change directory to the location of the PDF to handle paths correctly.
pushd "%~dp1"
if errorlevel 1 (
echo ERROR: Could not change to directory '%~dp1'.
pause
exit /b
)

echo Executing Python script in Manual Mode...
python "%~dp0\pdfpy.py" "%~nx1" --manual %pages%

echo.
echo Script execution finished.
popd
pause