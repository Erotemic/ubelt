#!/bin/bash
__doc__="
Remove intermediate 
"
find . -regex ".*\(__pycache__\|\.py[co]\)" -delete || find . -iname "*.pyc" -delete || find . -iname "*.pyo" -delete
rm -rf build
rm -rf htmlcov
