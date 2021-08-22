# -*- coding: utf-8 -*-
"""
This module exposes decorators for in-memory caching of functional results.
This is particularly useful when prototyping dynamic programing algorithms.

Either :func:`memoize`, :func:`memoize_method`, and :func:`memoize_property`
should be used depending on what type of function is being wrapped. The
following example demonstrates this.

Example:
    >>> import ubelt as ub
    >>> # Memoize a function, the args are hashed
    >>> @ub.memoize
    >>> def func(a, b):
    >>>     return a + b
    >>> #
    >>> class MyClass:
    >>>     # Memoize a class method, the args are hashed
    >>>     @ub.memoize_method
    >>>     def my_method(self, a, b):
    >>>         return a + b
    >>>     #
    >>>     # Memoize a property: there can be no args,
    >>>     @ub.memoize_property
    >>>     @property
    >>>     def my_property1(self):
    >>>         return 4
    >>>     #
    >>>     # The property decorator is optional
    >>>     def my_property2(self):
    >>>         return 5
    >>> #
    >>> func(1, 2)
    >>> func(1, 2)
    >>> self = MyClass()
    >>> self.my_method(1, 2)
    >>> self.my_method(1, 2)
    >>> self.my_property1
    >>> self.my_property1
    >>> self.my_property2
    >>> self.my_property2
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import functools
import sys
from ubelt import util_hash


__all__ = ['memoize', 'memoize_method', 'memoize_property']


PY2 = sys.version_info[0] == 2


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

    Example:
        >>> args = (4, [1, 2])
        >>> kwargs = {'a': 'b'}
        >>> key = _make_signature_key(args, kwargs)
        >>> print('key = {!r}'.format(key))
        >>> # Some mutable types cannot be handled by ub.hash_data
        >>> import pytest
        >>> if PY2:
        >>>     import collections as abc
        >>> else:
        >>>     from collections import abc
        >>> # This used to error, in ubelt versions < 0.9.5
        >>> _make_signature_key((4, [1, 2], {1: 2, 'a': 'b'}), kwargs={})
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
        msg = ('Signature is not hashable: '
               'args={} kwargs{}'.format(args, kwargs))
        raise TypeError(msg)
    return key


def memoize(func):
    """
    memoization decorator that respects args and kwargs

    Args:
        func (Callable): live python function

    Returns:
        Callable: memoized wrapper

    References:
        https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

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
        # Mimic attributes of a bound method
        if PY2:
            self.im_func = func
        else:
            self.__func__ = func

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


def memoize_property(fget):
    """
    Return a property attribute for new-style classes that only calls its
    getter on the first access. The result is stored and on subsequent accesses
    is returned, preventing the need to call the getter any more.

    This decorator can either be used by itself or by decorating another
    property. In either case the method will always become a property.

    Notes:
        implementation is a modified version of [1].

    References:
        ..[1] https://github.com/estebistec/python-memoized-property

    Example:
        >>> class C(object):
        ...     load_name_count = 0
        ...     @memoize_property
        ...     def name(self):
        ...         "name's docstring"
        ...         self.load_name_count += 1
        ...         return "the name"
        ...     @memoize_property
        ...     @property
        ...     def another_name(self):
        ...         "name's docstring"
        ...         self.load_name_count += 1
        ...         return "the name"
        >>> c = C()
        >>> c.load_name_count
        0
        >>> c.name
        'the name'
        >>> c.load_name_count
        1
        >>> c.name
        'the name'
        >>> c.load_name_count
        1
        >>> c.another_name
    """
    # Unwrap any existing property decorator
    while hasattr(fget, 'fget'):
        fget = fget.fget

    attr_name = '_' + fget.__name__

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)
