# orchestrator/setup.sh

#!/bin/bash
set -e

cd "$(dirname "$0")"

# Source common paths
source ./common.sh

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    PYTHON=$(find_python)
    $PYTHON -m venv venv
fi

echo "Upgrading pip..."
$VENV_PYTHON -m pip install --upgrade pip

echo "Installing requirements..."
$VENV_PIP install -r requirements.txt

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  ./run.sh --install-libs    # Install all libraries"
echo "  ./run.sh -p price_app      # Deploy specific project"
echo "  ./run.sh -a                # Deploy all projects"
echo "  ./run.sh -l                # List all projects"
