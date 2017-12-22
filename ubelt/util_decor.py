# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import functools


def memoize(func):
    """
    memoization decorator that respects args and kwargs

    References:
        https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

    Args:
        func (function):  live python function

    Returns:
        func: memoized wrapper

    CommandLine:
        python -m ubelt.util_decor memoize

    Example:
        >>> import ubelt as ub
        >>> closure = {'a': 'b', 'c': 'd'}
        >>> incr = [0]
        >>> def foo(key):
        >>>     value = closure[key]
        >>>     incr[0] += 1
        >>>     return value
        >>> foo_memo = ub.memoize(foo)
        >>> assert foo('a') == 'b' and foo('c') == 'd'
        >>> assert incr[0] == 2
        >>> print('Call memoized version')
        >>> assert foo_memo('a') == 'b' and foo_memo('c') == 'd'
        >>> assert incr[0] == 4
        >>> assert foo_memo('a') == 'b' and foo_memo('c') == 'd'
        >>> print('Counter should no longer increase')
        >>> assert incr[0] == 4
        >>> print('Closure changes result without memoization')
        >>> closure = {'a': 0, 'c': 1}
        >>> assert foo('a') == 0 and foo('c') == 1
        >>> assert incr[0] == 6
        >>> assert foo_memo('a') == 'b' and foo_memo('c') == 'd'
    """
    cache = {}
    @functools.wraps(func)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    memoizer.cache = cache
    return memoizer
