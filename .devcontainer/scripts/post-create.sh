#!/usr/bin/env bash
set -euo pipefail

# Ensure uv + the shared venv are on PATH even if something changes upstream
export PATH="/root/.local/bin:/opt/venv/bin:$PATH"
export VIRTUAL_ENV="/opt/venv"

# Avoid git safety warnings in containers
git config --global --add safe.directory "$(pwd)" >/dev/null 2>&1 || true

# Editable install, dev deps included if you have a [project.optional-dependencies] dev
uv pip install -e . -v
