#!/bin/bash
__doc__="""
Make a strict version of requirements

./dev/make_strict_req.sh
"""
mkdir -p requirements-strict
sed 's/>=/==/' requirements/runtime.txt > requirements-strict/runtime.txt
sed 's/>=/==/' requirements/optional.txt > requirements-strict/optional.txt
sed 's/>=/==/' requirements/tests.txt > requirements-strict/tests.txt
sed 's/requirements/requirements-strict/' requirements.txt > requirements-strict.txt

