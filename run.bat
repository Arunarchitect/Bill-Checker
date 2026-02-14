@echo off
setlocal

echo.
echo ============================================
echo        BILL VALIDATION TOOL STARTING
echo ============================================
echo.

REM ------------------------------------------------
REM Step 1: Check if Python is installed
REM ------------------------------------------------
echo Checking for Python installation...
python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b
)

echo ✅ Python detected.
echo.

REM ------------------------------------------------
REM Step 2: Create virtual environment if missing
REM ------------------------------------------------
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment.
        pause
        exit /b
    )
    echo ✅ Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.

REM ------------------------------------------------
REM Step 3: Activate virtual environment
REM ------------------------------------------------
echo Activating virtual environment...
call venv\Scripts\activate

if errorlevel 1 (
    echo ❌ Failed to activate virtual environment.
    pause
    exit /b
)

echo ✅ Virtual environment activated.
echo.

REM ------------------------------------------------
REM Step 4: Install required packages
REM ------------------------------------------------
echo Checking and installing required packages...
pip install --upgrade pip >nul 2>&1
pip install pandas >nul 2>&1

if errorlevel 1 (
    echo ❌ Failed to install required packages.
    echo Please check your internet connection.
    pause
    exit /b
)

echo ✅ Required packages ready.
echo.

REM ------------------------------------------------
REM Step 5: Run GUI Application
REM ------------------------------------------------
echo Launching Bill Validation GUI...
echo.

python gui.py

if errorlevel 1 (
    echo.
    echo ❌ Application closed due to an error.
) else (
    echo.
    echo ✅ Application closed normally.
)

echo.
echo ============================================
echo              PROCESS FINISHED
echo ============================================
echo.

pause
endlocal
