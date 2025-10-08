@echo off
chcp 65001 >nul 2>&1

cls
echo.
echo ===============================================================
echo     Once Human Helper - Install and Build
echo ===============================================================
echo.

:: Check if Python is installed
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is NOT installed!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python %PYTHON_VERSION% found
echo.

:: Install dependencies
echo [2/3] Installing dependencies...
echo Installing Pillow...
python -m pip install --upgrade Pillow
if %errorlevel% neq 0 (
    echo WARNING: Pillow installation had issues, but continuing...
)

echo Installing PyInstaller...
python -m pip install --upgrade pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller!
    pause
    exit /b 1
)
echo OK: All dependencies installed
echo.

:: Check project files
echo [3/3] Checking project files...
if not exist "assets" (
    echo ERROR: Assets folder not found!
    echo Make sure you run this from the project root directory.
    pause
    exit /b 1
)
if not exist "gui.py" (
    echo ERROR: gui.py not found!
    echo Make sure you run this from the project root directory.
    pause
    exit /b 1
)
echo OK: All files found
echo.

:: Clean up old build files
echo Cleaning old build files...
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "*.spec" del /q "*.spec" >nul 2>&1
echo.

:: Build EXE
echo ===============================================================
echo Building EXE - This will take 2-5 minutes...
echo ===============================================================
echo.

python -m PyInstaller --noconfirm --onefile --windowed --icon="assets/appicon1.ico" --add-data "assets;assets" --name "OnceHumanHelper" gui.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo.
echo ===============================================================
echo            BUILD SUCCESSFUL!
echo ===============================================================
echo.

:: Clean up build artifacts
echo Cleaning up temporary files...
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "OnceHumanHelper.spec" del /q "OnceHumanHelper.spec" >nul 2>&1
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
echo OK: Temporary files removed
echo.

echo EXE Location: dist\OnceHumanHelper.exe
pause

