==========================
GITHUB ACTION INSTRUCTIONS
==========================

This file is a reference script for setting up secrets for github actions
(because currently we can't add heredocs to github yaml files like we can with
other CI tools)

This file was designed to be used as a template. You can adapt it to
new projects with a few simple changes.  Namely perform the following
search and replaces.


# TODO: re-setup template


```bash
cat .github/workflows/setup_action_secrets.md | \
    sed 's|GITHUB_USER|Erotemic|g' | \
    sed 's|PYPKG|xdoctest|g' | \
    sed 's|GPG_ID|travis-ci-Erotemic|g' | \
    sed 's|PKG_CI_SECRET|EROTEMIC_CI_SECRET|g' \
> /tmp/repl 

# Check the diff
colordiff .github/workflows/setup_action_secrets.md /tmp/repl

# overwrite if you like the diff
cp /tmp/repl .github/workflows/setup_action_secrets.md
```

To use this script you need the following configurations on your CI account.

NOTES
-----

* This script will require maintenance for new releases of Python


CI SECRETS
----------

Almost all of the stages in this pipeline can be performed on a local machine
(making it much easier to debug) as well as the CI machine. However, there are
a handful of required environment variables which will contain sensitive
information. These variables are

* `TWINE_USERNAME` - this is your pypi username
    twine info is only needed if you want to automatically publish to pypi

* `TWINE_PASSWORD` - this is your pypi password 

* `EROTEMIC_CI_SECRET` - We will use this as a secret key to encrypt/decrypt gpg secrets 
    This is only needed if you want to automatically sign published
    wheels with a gpg key.

* `PERSONAL_GITHUB_PUSH_TOKEN` - 
    This is only needed if you want to automatically git-tag release branches.

    To make a API token go to:
        https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token

Instructions:

    Browse to: 
        https://github.com/Erotemic/xdoctest/settings/secrets/actions

    Do whatever you need to locally access the values of these variables

    echo $TWINE_USERNAME
    echo $PERSONAL_GITHUB_PUSH_TOKEN
    echo $EROTEMIC_CI_SECRET
    echo $TWINE_PASSWORD

    For each one, click "Add Environment Variable" and enter the name
    and value. Unfortunately this is a manual process.

WARNING: 

Ensure that your project settings do not allow Forks to view environment
variables.

TODO: Can you protect branches on GithubActions? Is that the default?

TODO: Look into secrethub

WARNING: If an untrusted actor gains the ability to write to a
protected branch, then they will be able to exfiltrate your secrets.

WARNING: These variables contain secret information. Ensure that these
the protected and masked settings are enabled when you create them.


ENCRYPTING GPG SECRETS
----------------------

The following script demonstrates how to securely encrypt a secret GPG key. It
is assumed that you have a file `secret_loader.sh` that looks like this

```bash
    source secretfile
```

and then a secret file that looks like this

```bash
    #!/bin/bash
    echo /some/secret/file 

    export TWINE_USERNAME=<pypi-username>
    export TWINE_PASSWORD=<pypi-password>
    export EROTEMIC_CI_SECRET="<a-very-long-secret-string>"
    export PERSONAL_GITHUB_PUSH_TOKEN="git-push-token:<token-password>"
```

You might also want to make a `secret_unloader.sh` that points to a script that
unloads these secret variables from the environment.

Given this file-structure setup, you can then run the following
commands verbatim. Alternatively just populate the environment
variables and run line-by-line without creating the secret
loader/unloader scripts.

SEE `setup_secrets.sh` script


Test Github Push Token 
----------------------

The following script tests if your `PERSONAL_GITHUB_PUSH_TOKEN` environment variable is correctly setup.

```bash
docker run -it ubuntu
apt update -y && apt install git -y
git clone https://github.com/Erotemic/xdoctest.git
cd xdoctest
# do sed twice to handle the case of https clone with and without a read token
git config user.email "ci@circleci.com"
git config user.name "CircleCI-User"
URL_HOST=$(git remote get-url origin | sed -e 's|https\?://.*@||g' | sed -e 's|https\?://||g')
echo "URL_HOST = $URL_HOST"
git tag "test-tag4"
git push --tags "https://${PERSONAL_GITHUB_PUSH_TOKEN}@${URL_HOST}"

# Cleanup after you verify the tags shows up on the remote
git push --delete origin test-tag4
git tag --delete test-tag4
```



Github Action Local Test
------------------------


```bash
    # How to run locally
    # https://packaging.python.org/guides/using-testpypi/
    cd $HOME/code
    git clone https://github.com/nektos/act.git $HOME/code/act
    cd $HOME/code/act
    chmod +x install.sh
    ./install.sh -b $HOME/.local/opt/act
    cd $HOME/code/xdoctest

    load_secrets
    unset GITHUB_TOKEN
    $HOME/.local/opt/act/act \
        --secret=EROTEMIC_TWINE_PASSWORD=$EROTEMIC_TWINE_PASSWORD \
        --secret=EROTEMIC_TWINE_USERNAME=$EROTEMIC_TWINE_USERNAME \
        --secret=EROTEMIC_CI_SECRET=$EROTEMIC_CI_SECRET \
        --secret=EROTEMIC_TEST_TWINE_USERNAME=$EROTEMIC_TEST_TWINE_USERNAME \
        --secret=EROTEMIC_TEST_TWINE_PASSWORD=$EROTEMIC_TEST_TWINE_PASSWORD 
