@echo off
setlocal enabledelayedexpansion

set VENV_DIR=.venv
set REQ_FILE=requirements.txt
set SERVER_URL=http://127.0.0.1:8000
set WAIT_SECONDS=3

if not exist %REQ_FILE% (
    echo requirements.txt not found.
    exit /b 1
)

if not exist %VENV_DIR% (
    echo Creating virtual environment in %VENV_DIR%...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
    call %VENV_DIR%\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo Failed to activate virtual environment.
        exit /b 1
    )
    echo Installing all requirements...
    pip install -r %REQ_FILE%
    if %errorlevel% neq 0 (
        echo Failed to install requirements.
        exit /b 1
    )
) else (
    call %VENV_DIR%\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo Failed to activate virtual environment.
        exit /b 1
    )
    echo Checking for missing packages...
    (
        echo import sys
        echo import subprocess
        echo reqs = []
        echo with open^('%REQ_FILE%', 'r'^) as f:
        echo     for line in f:
        echo         line = line.strip^(^)
        echo         if not line or line.startswith^('#'^):
        echo             continue
        echo         if '==' in line:
        echo             name, ver = line.split^('=='^)
        echo             name = name.lower^(^)
        echo             reqs.append^((line, name, ver)^)
        echo         else:
        echo             name = line.lower^(^)
        echo             reqs.append^((line, name, None)^)
        echo installed = {}
        echo pip_list = subprocess.check_output^([sys.executable, '-m', 'pip', 'list', '--format=freeze']^).decode^(^).splitlines^(^)
        echo for line in pip_list:
        echo     if '==' in line:
        echo         name, ver = line.split^('=='^)
        echo         installed[name.lower^(^)^] = ver
        echo missing = []
        echo for original, name, req_ver in reqs:
        echo     if name not in installed or ^(req_ver and installed[name] != req_ver^):
        echo         missing.append^(original^)
        echo if missing:
        echo     print^(f"Installing missing packages: {missing}"^)
        echo     subprocess.check_call^([sys.executable, '-m', 'pip', 'install'] + missing^)
        echo else:
        echo     print^("All packages are already installed."^)
    ) > check_install.py
    python check_install.py
    set CHECK_ERROR=%errorlevel%
    del check_install.py
    if %CHECK_ERROR% neq 0 (
        echo Failed to check or install missing packages.
        exit /b 1
    )
)

echo Starting the server in a new window...
start "Uvicorn Server" cmd /k "call %VENV_DIR%\Scripts\activate.bat && uvicorn main:app --reload"

echo Waiting %WAIT_SECONDS% seconds for the server to start...
timeout /t %WAIT_SECONDS% /nobreak >nul

echo Opening the default browser to %SERVER_URL%...
start %SERVER_URL%

endlocal