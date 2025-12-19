@echo off
REM Wrapper to run the coloring pipeline with optional venv

REM Change directory to the folder containing this batch file
cd /d %~dp0

REM Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3 from python.org
    pause
    exit /b 1
)

REM Check if a virtual environment folder exists
IF EXIST venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

REM Run the Python script
python process_coloring_pipeline.py

REM Pause so the console stays open
echo.
echo Processing complete. Press any key to exit...
pause >nul