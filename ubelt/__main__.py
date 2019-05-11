#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs the xdoctest CLI interface for ubelt

CommandLine:
    python -m ubelt list
    python -m ubelt all
"""
from __future__ import absolute_import, division, print_function, unicode_literals


def main():
    import xdoctest
    xdoctest.doctest_module('ubelt')


if __name__ == '__main__':
    main()
