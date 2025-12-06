# orchestrator/common.sh

#!/bin/bash

# Python paths - modify here to control globally
PYTHON_CMD="python3.12"
PYTHON_FALLBACK="python3"

# Find Python
find_python() {
    if command -v $PYTHON_CMD &> /dev/null; then
        echo $PYTHON_CMD
    elif command -v $PYTHON_FALLBACK &> /dev/null; then
        echo $PYTHON_FALLBACK
    else
        echo "python"
    fi
}

# Detect OS and set paths
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
    VENV_PYTHON="venv/Scripts/python.exe"
    VENV_PIP="venv/Scripts/pip.exe"
    VENV_ACTIVATE="venv/Scripts/activate"
else
    VENV_PYTHON="venv/bin/python"
    VENV_PIP="venv/bin/pip"
    VENV_ACTIVATE="venv/bin/activate"
fi

# Activate venv
activate_venv() {
    if [ -f "$VENV_ACTIVATE" ]; then
        source "$VENV_ACTIVATE"
    fi
}

export PYTHON_CMD
export VENV_PYTHON
export VENV_PIP
export VENV_ACTIVATE