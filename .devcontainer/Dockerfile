# syntax=docker/dockerfile:1.5
ARG BASE_IMAGE=local/uv:dev
FROM ${BASE_IMAGE} AS base

# Keep the same convention as your base image: login shell semantics
SHELL ["/bin/bash", "-l", "-c"]

USER root

# ------------------------------------
# Step 1: Install System Prerequisites
# ------------------------------------
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists <<'EOF'
#!/bin/bash
set -euo pipefail
apt update -q
DEBIAN_FRONTEND=noninteractive apt install -q -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    jq \
    unzip \
    tmux \
    tree \
    fd-find \
    ripgrep \
    bash-completion \
    build-essential \
    pkg-config \
    sudo 
EOF

# ------------------------------------
# Step 2: Create vscode user (if needed)
# ------------------------------------
RUN <<'EOF'
#!/bin/bash
set -euo pipefail
if ! id -u vscode >/dev/null 2>&1; then
  useradd -m -s /bin/bash vscode
fi
mkdir -p /workspaces
chown -R vscode:vscode /workspaces
EOF


# Allow passwordless sudo for vscode
RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/010-vscode-nopasswd \
  && chmod 0440 /etc/sudoers.d/010-vscode-nopasswd

# ------------------------------------
# Step 3: Make uv available to ALL users
# ------------------------------------
# Your base image installs uv into /root/.local/bin. Copy it to /usr/local/bin
# so the vscode user can use it without inheriting root's PATH.
RUN <<'EOF'
#!/bin/bash
set -euo pipefail

if [[ -x /root/.local/bin/uv ]]; then
  install -m 0755 /root/.local/bin/uv /usr/local/bin/uv
fi
if [[ -x /root/.local/bin/uvx ]]; then
  install -m 0755 /root/.local/bin/uvx /usr/local/bin/uvx
fi

command -v uv >/dev/null 2>&1 || { echo "uv not found after install"; exit 1; }
uv --version
EOF

# ------------------------------------
# Step 4: Create a shared "global" venv owned by vscode
# ------------------------------------
RUN <<'EOF'
#!/bin/bash
set -euo pipefail

mkdir -p /opt/venv
chown -R vscode:vscode /opt/venv

# Ensure vscode has a writable cache dir
VSCODE_HOME="$(getent passwd vscode | cut -d: -f6)"
mkdir -p "${VSCODE_HOME}/.cache"
chown -R vscode:vscode "${VSCODE_HOME}/.cache"

# Create the venv as vscode; force cache into their home
su - vscode -c 'export UV_CACHE_DIR="$HOME/.cache/uv"; uv venv /opt/venv --python=3.13 --seed'

chmod -R a+rX /opt/venv
EOF


# Make the venv usable even in non-login, non-interactive shells (e.g. postCreate)
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:/usr/local/bin:${PATH}"

# ------------------------------------
# Step 5: Auto-activate for vscode login shells
# ------------------------------------
RUN <<'EOF'
#!/bin/bash
set -euo pipefail

VSCODE_HOME="$(getent passwd vscode | cut -d: -f6)"

BASHRC_CONTENTS='
# Ensure shared venv is present and active
export VIRTUAL_ENV="/opt/venv"
export PATH="/opt/venv/bin:/usr/local/bin:$PATH"

# Auto-activate on shell startup
if [ -n "${BASH_VERSION:-}" ] && [ -f "/opt/venv/bin/activate" ]; then
  source /opt/venv/bin/activate
fi
'

echo "${BASHRC_CONTENTS}" >> "${VSCODE_HOME}/.bashrc"
echo "${BASHRC_CONTENTS}" >> "${VSCODE_HOME}/.profile"
echo "${BASHRC_CONTENTS}" >> "${VSCODE_HOME}/.bash_profile"
chown vscode:vscode "${VSCODE_HOME}/.bashrc" "${VSCODE_HOME}/.profile" "${VSCODE_HOME}/.bash_profile"
EOF

USER vscode

WORKDIR /workspaces

################
### __DOCS__ ###
################
RUN <<EOF
echo '
docker buildx build   --load   -f .devcontainer/Dockerfile   -t vscode/uv:local   .
'
EOF
