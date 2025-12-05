# orchestrator/setup.sh

#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
    venv/Scripts/python.exe -m pip install --upgrade pip
    venv/Scripts/python.exe -m pip install -r requirements.txt
else
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  ./run.sh --install-libs    # Install all libraries"
echo "  ./run.sh -p price_app      # Deploy specific project"
echo "  ./run.sh -a                # Deploy all projects"
echo "  ./run.sh -l                # List all projects"