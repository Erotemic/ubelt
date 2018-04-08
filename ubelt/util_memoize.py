# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import functools
import sys
from ubelt import util_hash


def _hashable(item):
    """
    Returns the item if it is naturally hashable, otherwise it tries to use
    ub.hash_data to make it hashable. Errors if it cannot.
    """
    try:
        hash(item)
    except TypeError:
        return util_hash.hash_data(item)
    else:
        return item


def _make_signature_key(args, kwargs):
    """
    Transforms function args into a key that can be used by the cache

    CommandLine:
        python -m ubelt.util_decor _make_signature_key

    Example:
        >>> args = (4, [1, 2])
        >>> kwargs = {'a': 'b'}
        >>> key = _make_signature_key(args, kwargs)
        >>> print('key = {!r}'.format(key))
        >>> # Some mutable types cannot be handled by ub.hash_data
        >>> import pytest
        >>> import six
        >>> if six.PY2:
        >>>     import collections as abc
        >>> else:
        >>>     from collections import abc
        >>> with pytest.raises(TypeError):
        >>>     _make_signature_key((4, [1, 2], {1: 2, 'a': 'b'}), kwargs={})
        >>> class Dummy(abc.MutableSet):
        >>>     def __contains__(self, item): return None
        >>>     def __iter__(self): return iter([])
        >>>     def __len__(self): return 0
        >>>     def add(self, item, loc): return None
        >>>     def discard(self, item): return None
        >>> with pytest.raises(TypeError):
        >>>     _make_signature_key((Dummy(),), kwargs={})
    """
    kwitems = kwargs.items()
    # TODO: we should check if Python is at least 3.7 and sort by kwargs
    # keys otherwise. Should we use hash_data for key generation
    if (sys.version_info.major, sys.version_info.minor) < (3, 7):  # nocover
        # We can sort because they keys are gaurenteed to be strings
        kwitems = sorted(kwitems)
    kwitems = tuple(kwitems)

    try:
        key = _hashable(args), _hashable(kwitems)
    except TypeError:
        raise TypeError('Signature is not hashable: args={} kwargs{}'.format(args, kwargs))
    return key


def memoize(func):
    """
    memoization decorator that respects args and kwargs

    References:
        https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

    Args:
        func (function): live python function

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
        key = _make_signature_key(args, kwargs)
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

    def __call__(self, *args, **kwargs):
        """
        The wrapped function call
        """
        cache = self._instance.__dict__.setdefault(self._cache_name, {})
        key = _make_signature_key(args, kwargs)
        if key in cache:
            return cache[key]
        else:
            value = cache[key] = self._func(self._instance, *args, **kwargs)
            return value

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_decor all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
