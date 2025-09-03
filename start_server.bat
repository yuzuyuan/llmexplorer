@echo off
setlocal

:: =================================================================
:: LLM Explorer - Startup Script (Windows GPU Version)
:: =================================================================
:: This script will check for dependencies, set up a local Conda
:: environment, and launch the application.
:: =================================================================

:: Change to the directory where this script is located
cd /d "%~dp0"

:: --- 1. Check for NVIDIA GPU Drivers ---
echo [INFO] Step 1 of 5: Checking for NVIDIA GPU drivers...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] NVIDIA drivers not found.
    echo [ERROR] This application requires NVIDIA drivers to be installed.
    echo [ERROR] Please download and install them from: https://www.nvidia.com/Download/index.aspx
    pause
    exit /b 1
)
echo [SUCCESS] NVIDIA drivers found.
echo.

:: --- 2. Define Paths and Check for Installer ---
set "ENV_DIR=%~dp0llm_env"
set "CONDA_INSTALL_DIR=%~dp0conda_install"
set "MINICONDA_INSTALLER=installers\Miniconda3-latest-Windows-x86_64.exe"

echo [INFO] Step 2 of 5: Looking for Miniconda installer...
if not exist "%MINICONDA_INSTALLER%" (
    echo [ERROR] Miniconda installer not found!
    echo [ERROR] Expected to find it at: "%~dp0%MINICONDA_INSTALLER%"
    echo [ERROR] Please make sure you have downloaded Miniconda and placed the .exe file in the 'installers' folder.
    pause
    exit /b 1
)
echo [SUCCESS] Miniconda installer found.
echo.

:: --- 3. Check if Environment Already Exists ---
echo [INFO] Step 3 of 5: Checking for existing Conda environment...
if exist "%ENV_DIR%\python.exe" (
    echo [INFO] Environment already exists. Skipping installation.
    goto start_services
)

:: --- 4. Install Environment (First Time Run) ---
echo [INFO] First time setup: A local environment will be installed.
echo [INFO] This may take several minutes. Please be patient.
echo.

:: Install Miniconda silently
echo [INFO] Installing Miniconda...
call "%MINICONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%CONDA_INSTALL_DIR%
if %errorlevel% neq 0 (
    echo [ERROR] Miniconda installation failed! Please check permissions or disk space.
    pause
    exit /b 1
)

:: Create the Conda environment from the .yml file
echo [INFO] Creating Conda environment from environment.yml. This will download all dependencies...
call "%CONDA_INSTALL_DIR%\Scripts\conda.exe" env create -f "backend\environment.yml" -p "%ENV_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create Conda environment! Please check your internet connection and the environment.yml file.
    pause
    exit /b 1
)
echo [SUCCESS] Environment installed successfully!
echo.

:start_services
:: --- 5. Start Application Services ---
echo [INFO] Step 4 of 5: Activating environment and starting services...

:: Activate the local Conda environment
call "%CONDA_INSTALL_DIR%\Scripts\activate.bat" "%ENV_DIR%"

:: Start Backend API Server (in a new background window)
echo [INFO] Starting Backend API server in the background...
start "LLMExplorer_Backend" /B python -m uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir "backend"

:: Start Frontend Server (in a new background window)
echo [INFO] Starting Frontend server in the background...
start "LLMExplorer_Frontend" /B python -m http.server 5173 --directory "dist"

:: Wait for services to initialize
timeout /t 5 /nobreak >nul

echo [INFO] Step 5 of 5: Opening application in your web browser...
start http://localhost:5173
echo.
echo =================================================================
echo  LLM Explorer is now running.
echo  Please visit: http://localhost:5173
echo  (To stop the application, simply close this window)
echo =================================================================
echo.

:: Keep the window open
pause >nul