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


class memoize_method(object):
    """
    memoization decorator for a method that respects args and kwargs

    References:
        http://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods/

    Example:
        >>> import ubelt as ub
        >>> closure = {'a': 'b', 'c': 'd'}
        >>> incr = [0]
        >>> class Foo(object):
        >>>     @memoize_method
        >>>     def foo_memo(self, key):
        >>>         value = closure[key]
        >>>         incr[0] += 1
        >>>         return value
        >>>     def foo(self, key):
        >>>         value = closure[key]
        >>>         incr[0] += 1
        >>>         return value
        >>> self = Foo()
        >>> assert self.foo('a') == 'b' and self.foo('c') == 'd'
        >>> assert incr[0] == 2
        >>> print('Call memoized version')
        >>> assert self.foo_memo('a') == 'b' and self.foo_memo('c') == 'd'
        >>> assert incr[0] == 4
        >>> assert self.foo_memo('a') == 'b' and self.foo_memo('c') == 'd'
        >>> print('Counter should no longer increase')
        >>> assert incr[0] == 4
        >>> print('Closure changes result without memoization')
        >>> closure = {'a': 0, 'c': 1}
        >>> assert self.foo('a') == 0 and self.foo('c') == 1
        >>> assert incr[0] == 6
        >>> assert self.foo_memo('a') == 'b' and self.foo_memo('c') == 'd'
        >>> print('Constructing a new object should get a new cache')
        >>> self2 = Foo()
        >>> self2.foo_memo('a')
        >>> assert incr[0] == 7
        >>> self2.foo_memo('a')
        >>> assert incr[0] == 7
    """
    def __init__(self, func):
        self._func = func
        self._cache_name = '_cache__' + func.__name__

    def __get__(self, instance, cls=None):
        """
        Descriptor get method. Called when the decorated method is accessed
        from an object instance.

        Args:
            instance (object): the instance of the class with the memoized method
            cls (type): the type of the instance
        """
        self._instance = instance
        return self

    def __call__(self, *args):
        """
        The wrapped function call
        """
        cache = self._instance.__dict__.setdefault(self._cache_name, {})
        if args in cache:
            return cache[args]
        else:
            value = cache[args] = self._func(self._instance, *args)
            return value

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_decor all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
