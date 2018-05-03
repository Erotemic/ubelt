# content of conftest.py
import pytest  # NOQA


def pytest_addoption(parser):
    # Allow --network to be passed in as an option on sys.argv
    parser.addoption("--network", action="store_true")
