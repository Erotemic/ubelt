#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import ubelt as ub
# ub.doctest_package('ubelt', 'all')

import pytest
import sys
pytest.main([
    '-p', 'no:doctest',
    '--cov=xdoctest',
    '--cov-config', '.coveragerc',
    '--cov-report', 'html',
    '--xdoctest',
    'ubelt',
] + sys.argv[1:])
