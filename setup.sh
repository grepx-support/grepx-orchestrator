#!/bin/bash
set -e

echo "Creating virtual environment..."
python3 -m venv venv || python -m venv venv

echo "Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
    venv/Scripts/python.exe -m pip install --upgrade pip
    venv/Scripts/pip.exe install pyyaml
else
    source venv/bin/activate
    pip install --upgrade pip
    pip install pyyaml
fi

echo ""
echo "Setup complete!"
echo "Run: ./run.sh -p price_app"