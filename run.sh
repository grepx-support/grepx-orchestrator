#!/bin/bash
set -e

if [ ! -d "venv" ]; then
    echo "Error: venv not found. Run ./setup.sh first"
    exit 1
fi

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
    venv/Scripts/python.exe orchestrator.py "$@"
else
    source venv/bin/activate
    python orchestrator.py "$@"
fi