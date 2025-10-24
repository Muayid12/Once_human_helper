@echo off
chcp 65001 >nul 2>&1

:: Generate log file with timestamp
set LOG_FILE=install_and_build_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

:: Start logging
echo Build started at %date% %time% > "%LOG_FILE%"
echo. >> "%LOG_FILE%"

cls
echo.
echo ===============================================================
echo     Once Human Helper - Install and Build
echo ===============================================================
echo.
echo Log file: %LOG_FILE%
echo.

:: Check if Python is installed
echo [1/3] Checking Python...
echo [1/3] Checking Python... >> "%LOG_FILE%"
python --version >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is NOT installed!
    echo ERROR: Python is NOT installed! >> "%LOG_FILE%"
    echo Please install Python from: https://www.python.org/downloads/
    echo Please install Python from: https://www.python.org/downloads/ >> "%LOG_FILE%"
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python %PYTHON_VERSION% found
echo OK: Python %PYTHON_VERSION% found >> "%LOG_FILE%"
echo.

:: Install dependencies
echo [2/3] Installing dependencies...
echo. >> "%LOG_FILE%"
echo [2/3] Installing dependencies... >> "%LOG_FILE%"
echo Installing Pillow...
echo Installing Pillow... >> "%LOG_FILE%"
python -m pip install --upgrade Pillow >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Pillow installation had issues, but continuing...
    echo WARNING: Pillow installation had issues, but continuing... >> "%LOG_FILE%"
)

echo Installing PyInstaller...
echo Installing PyInstaller... >> "%LOG_FILE%"
python -m pip install --upgrade pyinstaller >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller!
    echo ERROR: Failed to install PyInstaller! >> "%LOG_FILE%"
    pause
    exit /b 1
)
echo OK: All dependencies installed
echo OK: All dependencies installed >> "%LOG_FILE%"
echo.

:: Check project files
echo [3/3] Checking project files...
echo. >> "%LOG_FILE%"
echo [3/3] Checking project files... >> "%LOG_FILE%"
if not exist "assets" (
    echo ERROR: Assets folder not found!
    echo ERROR: Assets folder not found! >> "%LOG_FILE%"
    echo Make sure you run this from the project root directory.
    echo Make sure you run this from the project root directory. >> "%LOG_FILE%"
    pause
    exit /b 1
)
if not exist "gui.py" (
    echo ERROR: gui.py not found!
    echo ERROR: gui.py not found! >> "%LOG_FILE%"
    echo Make sure you run this from the project root directory.
    echo Make sure you run this from the project root directory. >> "%LOG_FILE%"
    pause
    exit /b 1
)
echo OK: All files found
echo OK: All files found >> "%LOG_FILE%"
echo.

:: Clean up old build files
echo Cleaning old build files...
echo. >> "%LOG_FILE%"
echo Cleaning old build files... >> "%LOG_FILE%"
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "*.spec" del /q "*.spec" >nul 2>&1
echo.

:: Build EXE
echo ===============================================================
echo Building EXE - This will take 2-5 minutes...
echo ===============================================================
echo.
echo. >> "%LOG_FILE%"
echo =============================================================== >> "%LOG_FILE%"
echo Building EXE - This will take 2-5 minutes... >> "%LOG_FILE%"
echo =============================================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

python -m PyInstaller --noconfirm --onefile --windowed --icon="assets/appicon1.ico" --add-data "assets;assets" --name "OnceHumanHelper" gui.py >> "%LOG_FILE%" 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo ERROR: Build failed! >> "%LOG_FILE%"
    echo Check the error messages above for details.
    echo Check the log file for details: %LOG_FILE% >> "%LOG_FILE%"
    echo Full log saved to: %LOG_FILE%
    pause
    exit /b 1
)

echo.
echo ===============================================================
echo            BUILD SUCCESSFUL!
echo ===============================================================
echo.
echo. >> "%LOG_FILE%"
echo =============================================================== >> "%LOG_FILE%"
echo            BUILD SUCCESSFUL! >> "%LOG_FILE%"
echo =============================================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

:: Move EXE from dist to main folder
echo Moving EXE to main folder...
echo Moving EXE to main folder... >> "%LOG_FILE%"
if exist "dist\OnceHumanHelper.exe" (
    move /Y "dist\OnceHumanHelper.exe" "OnceHumanHelper.exe" >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (
        echo OK: EXE moved to main folder
        echo OK: EXE moved to main folder >> "%LOG_FILE%"
    ) else (
        echo WARNING: Failed to move EXE
        echo WARNING: Failed to move EXE >> "%LOG_FILE%"
    )
) else (
    echo WARNING: EXE not found in dist folder
    echo WARNING: EXE not found in dist folder >> "%LOG_FILE%"
)
echo.

:: Clean up build artifacts
echo Cleaning up temporary files...
echo Cleaning up temporary files... >> "%LOG_FILE%"
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "OnceHumanHelper.spec" del /q "OnceHumanHelper.spec" >nul 2>&1
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
echo OK: Temporary files removed
echo OK: Temporary files removed >> "%LOG_FILE%"
echo.

echo EXE Location: OnceHumanHelper.exe
echo EXE Location: OnceHumanHelper.exe >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
echo Build completed at %date% %time% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
echo Full build log saved to: %LOG_FILE%
pause

