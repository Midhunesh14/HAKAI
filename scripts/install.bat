@echo off
echo ========================================================
echo Installing HAKAI Programming Language Environment
echo ========================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Running verification tests...
python -m pytest tests/ -v

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo HAKAI 1.0 successfully installed and verified!
    echo Add this directory to your PATH to use 'hakai' and 'hpm'.
    echo ========================================================
) else (
    echo [ERROR] Verification tests failed.
)

