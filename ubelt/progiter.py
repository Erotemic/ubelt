# -*- coding: utf-8 -*-
"""
ProgIter now exists in a standalone pip-installable module. The source code
lives in its own github repo here: https://github.com/Erotemic/progiter

Example:
    >>> import ubelt as ub
    >>> for n in ub.ProgIter(range(1000)):
    >>>     # do some work
    >>>     pass
"""
# On machines following Erotemic's directory structure for development
# the code can be found here: ~/code/progiter/progiter/progiter.py
from __future__ import absolute_import, division, print_function, unicode_literals
from progiter import ProgIter

__all__ = [
    'ProgIter',
]
