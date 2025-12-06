#!/bin/bash
set -e

cd "$(dirname "$0")"

# Source common paths
source ./common.sh

if [ ! -d "venv" ]; then
    echo "Error: venv not found. Run ./setup.sh first"
    exit 1
fi

$VENV_PYTHON orchestrator.py "$@"