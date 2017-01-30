# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import itertools as it


def take(items, indices):
    r"""
    Selects a subset of a list based on a list of indices.
    This is similar to np.take, but pure python.

    Args:
        items (list): some indexable object
        indices (list OR slice OR int): some indexing object

    Returns:
        iter or scalar: subset of the list

    SeeAlso:
        ub.dict_subset

    Example:
        >>> import ubelt as ub
        >>> items = [0, 1, 2, 3]
        >>> indices = [2, 0]
        >>> ub.take(items, indices)
        [2, 0]

    Example:
        >>> import ubelt as ub
        >>> items = [0, 1, 2, 3]
        >>> index = 2
        >>> ub.take(items, index)
        2

    Example:
        >>> import ubelt as ub
        >>> items = [0, 1, 2, 3]
        >>> index = slice(1, None, 2)
        >>> ub.take(items, index)
        [1, 3]
    """
    try:
        return [items[index] for index in indices]
    except TypeError:
        return items[indices]


def compress(items, flags):
    r"""
    Selects items where the corresponding value in flags is True
    This is similar to np.compress and it.compress

    Args:
        items (iterable): a sequence
        flags (iterable): corresponding sequence of bools

    Returns:
        list: a subset of masked items

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 3, 4, 5]
        >>> flags = [False, True, True, False, True]
        >>> ub.compress(items, flags)
        [2, 3, 5]
    """
    return list(it.compress(items, flags))


def flatten(nested_list):
    r"""
    Args:
        nested_list (list): list of lists

    Returns:
        list: flat list

    Example:
        >>> import ubelt as ub
        >>> nested_list = [['a', 'b'], ['c', 'd']]
        >>> ub.flatten(nested_list)
        ['a', 'b', 'c', 'd']
    """
    return list(it.chain.from_iterable(nested_list))
