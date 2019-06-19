#!/bin/bash
# Install dependency packages
pip install -r requirements/runtime.txt
pip install -r requirements/tests.txt
pip install -r requirements/optional.txt

# new pep makes this not always work
# pip install -e .

python setup.py develop
