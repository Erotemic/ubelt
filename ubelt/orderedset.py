# -*- coding: utf-8 -*-
"""
This module exposes the `OrderedSet` class, which is a collection of unique
items that maintains the order in which the items were added. An `OrderedSet`
(or its alias `oset`) behaves very similarly to Python's builtin `set` object,
the main difference being that an `OrderedSet` can efficiently lookup its items
by index.


While `ubelt` exposes `OrderedSet`, the actual implementation lives in the
standalone `ordered_set` package. For more details on the implementation please
reference https://github.com/LuminosoInsight/ordered-set.

Example:
    >>> import ubelt as ub
    >>> ub.oset([1, 2, 3])
    OrderedSet([1, 2, 3])
    >>> (ub.oset([1, 2, 3]) - {2}) | {2}
    OrderedSet([1, 3, 2])
    >>> [ub.oset([1, 2, 3])[i] for i in [1, 0, 2]]
    [2, 1, 3]
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import ordered_set

__all__ = ['OrderedSet', 'oset']

OrderedSet = ordered_set.OrderedSet
oset = OrderedSet
