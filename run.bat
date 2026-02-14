@echo off
setlocal

echo.
echo ============================================
echo        BILL VALIDATION TOOL STARTING
echo ============================================
echo.

REM ------------------------------------------------
REM Step 1: Check if Python (via py launcher) exists
REM ------------------------------------------------
echo Checking for Python installation...
py -3 --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Python 3 is not installed.
    echo Please install Python from https://www.python.org/
    echo Make sure to enable:
    echo  - Add Python to PATH
    echo  - Install launcher for all users
    echo.
    pause
    exit /b
)

echo Python detected successfully.
echo.

REM ------------------------------------------------
REM Step 2: Create virtual environment if missing
REM ------------------------------------------------
if not exist venv (
    echo Creating virtual environment...
    py -3 -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.

REM ------------------------------------------------
REM Step 3: Activate virtual environment
REM ------------------------------------------------
echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b
)

echo Virtual environment activated.
echo.

REM ------------------------------------------------
REM Step 4: Install required packages inside venv
REM ------------------------------------------------
echo Installing / Checking required packages...

python -m pip install --upgrade pip
python -m pip install pandas

if errorlevel 1 (
    echo ERROR: Package installation failed.
    pause
    exit /b
)

echo Packages ready.
echo.

REM ------------------------------------------------
REM Step 5: Run GUI Application
REM ------------------------------------------------
echo Launching Bill Validation GUI...
echo.

python gui.py

if errorlevel 1 (
    echo.
    echo Application closed due to an error.
) else (
    echo.
    echo Application closed normally.
)

echo.
echo ============================================
echo              PROCESS FINISHED
echo ============================================
echo.

pause
endlocal
