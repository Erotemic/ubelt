#!/bin/bash
__heredoc__="""
Requirements:
     pip install -r docs/requirements.txt
     sphinx

Notes:
    cd ~/code/ubelt/docs
    make html
    sphinx-apidoc -f -o ~/code/ubelt/docs/source ~/code/ubelt/ubelt --separate
    make html

    cd ~/code/sphinx
    github-add-fork source https://github.com/sphinx-doc/sphinx.git
"""

(cd ~/code/ubelt/docs && make html)
