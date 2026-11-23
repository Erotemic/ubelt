#!/bin/bash
# Install dependency packages
pip install -r requirements.txt

# Install ubelt in editable mode using pyproject.toml metadata.
python -m pip install -e .
