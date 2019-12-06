#!/bin/bash
__heredoc__='''
Script to publish a new version of this library on PyPI

Args:
    # These environment variables must / should be set
    TWINE_USERNAME : username for pypi
    TWINE_PASSWORD : password for pypi
    USE_GPG : defaults to True

Requirements:
     twine >= 1.13.0
     gpg2 >= 2.2.4
     OpenSSL >= 1.1.1c

Notes:
    # NEW API TO UPLOAD TO PYPI
    # https://packaging.python.org/tutorials/distributing-packages/

Usage:
    cd <YOUR REPO>

    # Set your variables or load your secrets
    export TWINE_USERNAME=<pypi-username>
    export TWINE_PASSWORD=<pypi-password>

    source $(secret_loader.sh)

    # Interactive/Dry run
    ./publish.sh 

    # Non-Interactive run
    #./publish.sh yes
'''

check_variable(){
    KEY=$1
    VAL=${!KEY}
    echo "[DEBUG] CHECK VARIABLE: $KEY=\"$VAL\""
    if [[ "$VAL" == "" ]]; then
        echo "[ERROR] UNSET VARIABLE: $KEY=\"$VAL\""
        exit 1;
    fi
}

# Options
CURRENT_BRANCH=${CURRENT_BRANCH:=$(git branch | grep \* | cut -d ' ' -f2)}
DEPLOY_BRANCH=${DEPLOY_BRANCH:=release}
DEPLOY_REMOTE=${DEPLOY_REMOTE:=origin}

VERSION=$(python -c "import setup; print(setup.VERSION)")
MB_PYTHON_TAG=${MB_PYTHON_TAG:=py2.py3-none-any}
NAME=${NAME:=$(python -c "import setup; print(setup.NAME)")}

TWINE_USERNAME=${TWINE_USERNAME:=""}
TWINE_PASSWORD=${TWINE_PASSWORD:=""}

USE_GPG=${USE_GPG:="True"}
GPG_KEYID=${GPG_KEYID:=$(git config --global user.signingkey)}
TAG_AND_UPLOAD=${TAG_AND_UPLOAD:=$1}

if [[ "$(which gpg2)" != "" ]]; then
    GPG_EXECUTABLE=${GPG_EXECUTABLE:=gpg2}
else
    GPG_EXECUTABLE=${GPG_EXECUTABLE:=gpg}
fi

check_variable CURRENT_BRANCH
check_variable DEPLOY_BRANCH
check_variable DEPLOY_REMOTE
check_variable VERSION || exit 1


echo "
=== PYPI BUILDING SCRIPT ==
CURRENT_BRANCH='$CURRENT_BRANCH'
DEPLOY_BRANCH='$DEPLOY_BRANCH'
VERSION='$VERSION'
TWINE_USERNAME='$TWINE_USERNAME'
GPG_KEYID = '$GPG_KEYID'
MB_PYTHON_TAG = '$MB_PYTHON_TAG'
NAME = '$NAME'
"


echo "
=== <BUILD WHEEL> ===
"
echo "LIVE BUILDING"
# Build wheel and source distribution
python setup.py bdist_wheel --universal
python setup.py sdist 

BDIST_WHEEL_PATH=$(ls dist/$NAME-$VERSION-$MB_PYTHON_TAG*.whl)
SDIST_PATH=$(dir dist/$NAME-$VERSION*.tar.gz)
echo "
echo "VERSION='$VERSION'"
BDIST_WHEEL_PATH='$BDIST_WHEEL_PATH'
SDIST_PATH='$SDIST_PATH'
"

check_variable BDIST_WHEEL_PATH
check_variable SDIST_PATH 

echo "
=== <END BUILD WHEEL> ===
"

echo "
=== <GPG SIGN> ===
"
if [ "$USE_GPG" == "True" ]; then
    # https://stackoverflow.com/questions/45188811/how-to-gpg-sign-a-file-that-is-built-by-travis-ci
    # REQUIRES GPG >= 2.2
    check_variable GPG_EXECUTABLE
    check_variable GPG_KEYID

    echo "Signing wheels"
    GPG_SIGN_CMD="$GPG_EXECUTABLE --batch --yes --detach-sign --armor --local-user $GPG_KEYID"
    $GPG_SIGN_CMD --output $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH
    $GPG_SIGN_CMD --output $SDIST_PATH.asc $SDIST_PATH

    echo "Checking wheels"
    twine check $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH
    twine check $SDIST_PATH.asc $SDIST_PATH

    echo "Verifying wheels"
    $GPG_EXECUTABLE --verify $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH 
    $GPG_EXECUTABLE --verify $SDIST_PATH.asc $SDIST_PATH 
else
    echo "USE_GPG=False, Skipping GPG sign"
fi
echo "
=== <END GPG SIGN> ===
"

if [[ "$CURRENT_BRANCH" != "$DEPLOY_BRANCH" ]]; then
    TAG_AND_UPLOAD="no"
    echo "current branch is not the deploy branch. Forcing tag_and_upload=no"
fi


# Verify that we want to publish
if [[ "$TAG_AND_UPLOAD" != "yes" ]]; then
    if [[ "$TAG_AND_UPLOAD" != "no" ]]; then
        read -p "Are you ready to publish version='$VERSION' on branch='$CURRENT_BRANCH'? (input 'yes' to confirm)" ANS
        echo "ANS = $ANS"
        TAG_AND_UPLOAD="$ANS"
    else
        echo "WRONG BRANCH: Not ready to publish VERSION='$VERSION' on branch='$CURRENT_BRANCH'" 
    fi
else
    echo "Do not want to publish VERSION='$VERSION' on branch='$CURRENT_BRANCH'" 
fi


if [[ "$TAG_AND_UPLOAD" == "yes" ]]; then
    check_variable TWINE_USERNAME
    check_variable TWINE_PASSWORD

    git tag $VERSION -m "tarball tag $VERSION"
    git push --tags $DEPLOY_REMOTE $DEPLOY_BRANCH

    if [ "$USE_GPG" == "True" ]; then
        twine upload --username $TWINE_USERNAME --password=$TWINE_PASSWORD --sign $BDIST_WHEEL_PATH.asc $BDIST_WHEEL_PATH
        twine upload --username $TWINE_USERNAME --password=$TWINE_PASSWORD --sign $SDIST_PATH.asc $SDIST_PATH
    else
        twine upload --username $TWINE_USERNAME --password=$TWINE_PASSWORD $BDIST_WHEEL_PATH 
        twine upload --username $TWINE_USERNAME --password=$TWINE_PASSWORD $SDIST_PATH 
    fi
    echo """
        !!! FINISH: LIVE RUN !!!
    """
else
    ls dist
    echo """
        DRY RUN ... Skiping tag and upload

        VERSION = '$VERSION'
        DEPLOY_REMOTE = '$DEPLOY_REMOTE'
        CURRENT_BRANCH = '$CURRENT_BRANCH'
        DEPLOY_BRANCH = '$DEPLOY_BRANCH'
        TAG_AND_UPLOAD = '$TAG_AND_UPLOAD'

        To do live run set TAG_AND_UPLOAD=yes and ensure deploy and current branch are the same

        !!! FINISH: DRY RUN !!!
    """
fi
