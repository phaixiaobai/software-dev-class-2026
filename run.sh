#!/usr/bin/env bash
# Lightweight runner: creates a .venv (if missing), installs requirements, then runs dem_generator.py
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment at $VENV_DIR"
  /opt/homebrew/bin/python3 -m venv "$VENV_DIR"
fi

PY="$VENV_DIR/bin/python"

echo "Upgrading pip and installing requirements (if needed)"
# Use "$PY -m pip" to avoid invoking the pip launcher script directly. The pip
# wrapper can have a shebang with the full path to the venv python which fails
# if the project path contains spaces or special characters.
"$PY" -m pip install --upgrade pip setuptools wheel >/dev/null
if [ -f "$ROOT_DIR/requirements.txt" ]; then
  echo "Installing from requirements.txt"
  "$PY" -m pip install -r "$ROOT_DIR/requirements.txt"
fi

echo "Running dem_generator.py with $PY"
"$PY" "$ROOT_DIR/dem_generator.py"
