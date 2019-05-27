#!/bin/bash
__heredoc__="""
Script to publish a new version of ubelt on PyPI

TODO:
    - [ ] Do a digital signature of release

Requirements:
     twine

Notes:
    # NEW API TO UPLOAD TO PYPI
    # https://packaging.python.org/tutorials/distributing-packages/

Usage:
    cd <YOUR REPO>

    git fetch --all
    git checkout master
    git pull 

    gitk --all

    ./publish

    git checkout -b dev/<next>
"""
if [[ "$USER" == "joncrall" ]]; then
    GITHUB_USERNAME=erotemic
fi

# First tag the source-code
VERSION=$(python -c "import setup; print(setup.version)")
BRANCH=$(git branch | grep \* | cut -d ' ' -f2)

echo "=== PYPI PUBLISHING SCRIPT =="
echo "BRANCH = $BRANCH"
echo "VERSION = '$VERSION'"

if [[ "$BRANCH" != "master" ]]; then
    echo "WARNING: you are running publish on a non-master branch"
fi

# Verify that we want to publish
read -p "Are you ready to publish version=$VERSION on branch=$BRANCH? (input 'yes' to confirm)" ANS
echo "ANS = $ANS"

if [[ "$ANS" == "yes" ]]; then
    echo "Live run"

    git tag $VERSION -m "tarball tag $VERSION"
    git push --tags origin master

    # Use twine to upload. This will prompt for username and password
    # If you get an error:
    #   403 Client Error: Invalid or non-existent authentication information.
    # simply try typing your password slower.
    pip install twine -U

    # Build wheel or source distribution
    python setup.py bdist_wheel --universal
    WHEEL_PATH=dist/ubelt-$VERSION-py2.py3-none-any.whl

    # Sign with your GPG key
    gpg --detach-sign -a $WHEEL_PATH
    twine check $WHEEL_PATH $WHEEL_PATH.asc

    # Set TWINE_PASSWORD environ to skip password step
    twine upload \
        --username $GITHUB_USERNAME --password=$TWINE_PASSWORD \
        $WHEEL_PATH $WHEEL_PATH.asc
else  
    echo "Dry run"
fi
