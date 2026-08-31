#!/usr/bin/env bash
# Idempotent Cloud Agent install script for CAM5x AI CAM.
# Creates a Python virtualenv and installs dependencies. Installs the
# python3-venv system package first if the base image lacks it.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "python3-venv not available; installing it..."
  sudo apt-get update -qq
  sudo apt-get install -y python3-venv
fi

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "Install complete."
