@echo off
REM Build script for Windows executable
setlocal enabledelayedexpansion

echo ==========================================
echo   AI Rescheduling Agent - Build Script
echo ==========================================
echo.

echo 🖥️  Building for: Windows
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: Python %PYTHON_VERSION%
echo.

REM Install PyInstaller
echo Installing/upgrading PyInstaller...
python -m pip install --upgrade pyinstaller --user --quiet
echo PyInstaller ready
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt --user --quiet
echo Dependencies installed
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Cleaned
echo.

REM Build the executable
echo Building executable for Windows...
echo    Using spec file: build_windows.spec
echo.

REM Use python -m PyInstaller instead of pyinstaller command
python -m PyInstaller --clean --noconfirm build_windows.spec

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   BUILD SUCCESSFUL!
    echo ==========================================
    echo.
    echo Output location: dist\AI_Rescheduling_Agent.exe
    echo.
    
    REM Show size
    for %%A in (dist\AI_Rescheduling_Agent.exe) do echo 📊 Size: %%~zA bytes
    echo.
    
    echo To distribute:
    echo    1. Copy dist\AI_Rescheduling_Agent.exe to target machines
    echo    2. Create config.env file with API credentials
    echo    3. Run the executable
    echo.
    echo HIPAA Compliance Notes:
    echo    ✅ Runs localhost only (127.0.0.1^)
    echo    ✅ No external network access
    echo    ✅ All data stays on local machine
    echo    ✅ No telemetry or analytics
    echo.
) else (
    echo.
    echo ==========================================
    echo   ❌ BUILD FAILED
    echo ==========================================
    echo.
    echo Check the error messages above for details.
    pause
    exit /b 1
)

pause