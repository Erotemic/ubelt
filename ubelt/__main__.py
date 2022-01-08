#!/usr/bin/env python
"""
Runs the xdoctest CLI interface for ubelt

CommandLine:
    python -m ubelt list
    python -m ubelt all
    python -m ubelt zero
"""

if __name__ == '__main__':
    import xdoctest  # type: ignore
    xdoctest.doctest_module('ubelt')
