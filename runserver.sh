#!/bin/bash

VENV_DIR=".venv"
REQ_FILE="requirements.txt"
SERVER_URL="http://127.0.0.1:8000"
WAIT_SECONDS=3

# Check if requirements.txt exists
if [ ! -f "$REQ_FILE" ]; then
    echo "$REQ_FILE not found."
    exit 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
    source "$VENV_DIR/bin/activate"
    echo "Installing all requirements..."
    pip install -r "$REQ_FILE"
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements."
        exit 1
    fi
else
    source "$VENV_DIR/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment."
        exit 1
    fi
    echo "Checking for missing packages..."
    # Create temporary Python script to check and install missing packages
    cat > check_install.py << EOL
import sys
import subprocess
reqs = []
with open('$REQ_FILE', 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '==' in line:
            name, ver = line.split('==')
            name = name.lower()
            reqs.append((line, name, ver))
        else:
            name = line.lower()
            reqs.append((line, name, None))
installed = {}
pip_list = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=freeze']).decode().splitlines()
for line in pip_list:
    if '==' in line:
        name, ver = line.split('==')
        installed[name.lower()] = ver
missing = []
for original, name, req_ver in reqs:
    if name not in installed or (req_ver and installed[name] != req_ver):
        missing.append(original)
if missing:
    print(f"Installing missing packages: {missing}")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
else:
    print("All packages are already installed.")
EOL
    python3 check_install.py
    CHECK_ERROR=$?
    rm check_install.py
    if [ $CHECK_ERROR -ne 0 ]; then
        echo "Failed to check or install missing packages."
        exit 1
    fi
fi

echo "Starting the server in the background..."
uvicorn main:app --reload &
SERVER_PID=$!

echo "Waiting $WAIT_SECONDS seconds for the server to start..."
sleep $WAIT_SECONDS

echo "Opening the default browser to $SERVER_URL..."
xdg-open "$SERVER_URL"

# Keep the script running to keep the terminal open
wait $SERVER_PID