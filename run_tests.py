#!/usr/bin/env python
# -*- coding: utf-8 -*-
if __name__ == '__main__':
    import pytest
    import sys
    package_name = 'ubelt'
    pytest.main([
        '-p', 'no:doctest',
        '--cov-config', 'coveragerc',
        '--cov-report', 'html',
        '--cov-report', 'term',
        '--xdoctest',
        '--cov=' + package_name,
        package_name,
    ] + sys.argv[1:])
