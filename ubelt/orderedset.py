# -*- coding: utf-8 -*-
"""
The implementation of this util has been moved to
https://github.com/LuminosoInsight/ordered-set
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import ordered_set

__all__ = ['OrderedSet', 'oset']

OrderedSet = ordered_set.OrderedSet
oset = OrderedSet


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.orderedset all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
