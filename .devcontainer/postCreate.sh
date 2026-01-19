#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# Example: UV_PYTHON=3.12 (set via devcontainer.json containerEnv)
# If unset, default to whatever "python" is in the container.
UV_PYTHON="${UV_PYTHON:-}"

# Install uv first (user-local), then put it on PATH for this script
python -m pip install --user -U uv
export PATH="$HOME/.local/bin:$PATH"

# Choose a versioned venv name so switching versions doesn't clobber
if [[ -n "$UV_PYTHON" ]]; then
  VENV_DIR=".venv-py${UV_PYTHON//./}"   # 3.12 -> .venv-py312
  uv venv --python "$UV_PYTHON" "$VENV_DIR"   # may download python if needed
else
  # Derive from current python
  PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"
  VENV_DIR=".venv-py${PY_MM}"
  uv venv "$VENV_DIR"
fi

# Point .venv at the chosen environment (stable path for VS Code + uv discovery)
ln -sfn "$VENV_DIR" .venv

source .venv/bin/activate

# Install deps into the environment linked to .venv
uv pip install -U pip
# uv pip install -r requirements/dev.txt
uv pip install -e ".[all]"