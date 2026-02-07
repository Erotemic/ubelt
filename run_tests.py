#!/usr/bin/env python
import sys


def get_this_script_fpath():
    import pathlib

    try:
        fpath = pathlib.Path(__file__)
    except NameError:
        # This is not being run from a script, thus the developer is doing some
        # IPython hacking, so we will assume a path on the developer machine.
        fpath = pathlib.Path('~/code/ubelt/run_tests.py').expanduser()
        if not fpath.exists():
            raise Exception(
                'Unable to determine the file path that this script '
                'should correspond to'
            )
    return fpath


def main():
    import os

    import pytest

    repo_dpath = get_this_script_fpath().parent

    package_name = 'ubelt'
    mod_dpath = repo_dpath / 'ubelt'
    test_dpath = repo_dpath / 'tests'
    config_fpath = repo_dpath / 'pyproject.toml'

    pytest_args = [
        '--cov-config', os.fspath(config_fpath),
        '--cov-report', 'html',
        '--cov-report', 'term',
        '--durations', '100',
        '--xdoctest',
        '--cov=' + package_name,
        os.fspath(mod_dpath),
        os.fspath(test_dpath)
    ]
    pytest_args = pytest_args + sys.argv[1:]
    ret = pytest.main(pytest_args)
    return ret


if __name__ == '__main__':
    sys.exit(main())
