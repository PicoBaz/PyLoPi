@echo off
echo ====================================
echo      PyLoPi - Log Analyzer
echo ====================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

if not exist "venv\installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo. > venv\installed
)

echo.
echo Starting PyLoPi...
echo Access the dashboard at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
pause