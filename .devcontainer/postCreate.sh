#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# Install uv
python -m pip install --user -U uv
export PATH="$HOME/.local/bin:$PATH"

# Create versioned virtual environment (or reuse existing)
if [[ -n "${UV_PYTHON:-}" ]]; then
  VENV_DIR=".venv-py${UV_PYTHON//./}"
  uv venv --allow-existing --python "$UV_PYTHON" "$VENV_DIR"
else
  PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"
  VENV_DIR=".venv-py${PY_MM}"
  uv venv --allow-existing "$VENV_DIR"
fi

# Link to stable .venv path
ln -sfn "$VENV_DIR" .venv

# Activate and install dependencies
source .venv/bin/activate
uv pip install -U pip
uv pip install -e ".[all]"
