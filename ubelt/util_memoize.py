"""
This module exposes decorators for in-memory caching of functional results.
This is particularly useful when prototyping dynamic programming algorithms.

Either :func:`memoize`, :func:`memoize_method`, and :func:`memoize_property`
should be used depending on what type of function is being wrapped. The
following example demonstrates this.

In Python 3.8+ :func:`memoize` works similarly to the standard library
:func:`functools.cache`, but the ubelt version makes use of
:func:`ubelt.util_hash.hash_data`, which is slower, but handles inputs
containing mutable containers.

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

from __future__ import annotations

import functools
import sys
import typing

from ubelt import util_hash

if typing.TYPE_CHECKING:
    from typing import Any, Callable


# TODO: Need to think if we can fix any of the typing ignores in this file.

__all__ = ['memoize', 'memoize_method', 'memoize_property']


def _hashable(item):
    """
    Returns the item if it is naturally hashable, otherwise it tries to use
    ubelt.util_hash.hash_data to make it hashable. Errors if it cannot.
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
        >>> from ubelt.util_memoize import _make_signature_key
        >>> args = (4, [1, 2])
        >>> kwargs = {'a': 'b'}
        >>> key = _make_signature_key(args, kwargs)
        >>> print('key = {!r}'.format(key))
        >>> # Some mutable types cannot be handled by ub.hash_data
        >>> import pytest
        >>> from collections import abc
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
        # We can sort because they keys are guaranteed to be strings
        kwitems = sorted(kwitems)
    kwitems = tuple(kwitems)

    try:
        key = _hashable(args), _hashable(kwitems)
    except TypeError:
        msg = ('Signature is not hashable: '
               'args={} kwargs{}'.format(args, kwargs))
        raise TypeError(msg)
    return key


def memoize(func: Callable) -> Callable:
    """
    memoization decorator that respects args and kwargs

    In Python 3.9. The :mod:`functools` introduces the `cache` method, which is
    currently faster than memoize for simple functions [FunctoolsCache]_.
    However, memoize can handle more general non-natively hashable inputs.

    Args:
        func (Callable): live python function

    Returns:
        Callable: memoized wrapper

    References:
        .. [WikiMemoize] https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
        .. [FunctoolsCache] https://docs.python.org/3/library/functools.html

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

    # memoizer.cache = cache
    setattr(memoizer, 'cache', cache)
    return memoizer


class memoize_method:
    """
    memoization decorator for a method that respects args and kwargs

    References:
        .. [ActiveState_Miller_2010] http://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods

    Attributes:
        __func__ (Callable): the wrapped function

    Note:
        This is very thread-unsafe, and has an issue as pointed out in
        [ActiveState_Miller_2010]_, next version may work on fixing this.

    Example:
        >>> import ubelt as ub
        >>> closure1 = closure = {'a': 'b', 'c': 'd', 'z': 'z1'}
        >>> incr = [0]
        >>> class Foo:
        >>>     def __init__(self, instance_id):
        >>>         self.instance_id = instance_id
        >>>     @ub.memoize_method
        >>>     def foo_memo(self, key):
        >>>         "Wrapped foo_memo docstr"
        >>>         value = closure[key]
        >>>         incr[0] += 1
        >>>         return value, self.instance_id
        >>>     def foo(self, key):
        >>>         value = closure[key]
        >>>         incr[0] += 1
        >>>         return value, self.instance_id
        >>> self1 = Foo('F1')
        >>> assert self1.foo('a') == ('b', 'F1')
        >>> assert self1.foo('c') == ('d', 'F1')
        >>> assert incr[0] == 2
        >>> #
        >>> print('Call memoized version')
        >>> assert self1.foo_memo('a') == ('b', 'F1')
        >>> assert self1.foo_memo('c') == ('d', 'F1')
        >>> assert incr[0] == 4, 'should have called a function 4 times'
        >>> #
        >>> assert self1.foo_memo('a') == ('b', 'F1')
        >>> assert self1.foo_memo('c') == ('d', 'F1')
        >>> print('Counter should no longer increase')
        >>> assert incr[0] == 4
        >>> #
        >>> print('Closure changes result without memoization')
        >>> closure2 = closure = {'a': 0, 'c': 1, 'z': 'z2'}
        >>> assert self1.foo('a') == (0, 'F1')
        >>> assert self1.foo('c') == (1, 'F1')
        >>> assert incr[0] == 6
        >>> assert self1.foo_memo('a') == ('b', 'F1')
        >>> assert self1.foo_memo('c') == ('d', 'F1')
        >>> #
        >>> print('Constructing a new object should get a new cache')
        >>> self2 = Foo('F2')
        >>> self2.foo_memo('a')
        >>> assert incr[0] == 7
        >>> self2.foo_memo('a')
        >>> assert incr[0] == 7
        >>> # Check that the decorator preserves the name and docstring
        >>> assert self1.foo_memo.__doc__ == 'Wrapped foo_memo docstr'
        >>> assert self1.foo_memo.__name__ == 'foo_memo'
        >>> print(f'self1.foo_memo = {self1.foo_memo!r}, {hex(id(self1.foo_memo))}')
        >>> print(f'self2.foo_memo = {self2.foo_memo!r}, {hex(id(self2.foo_memo))}')
        >>> #
        >>> # Test for the issue in the active state recipe
        >>> method1 = self1.foo_memo
        >>> method2 = self2.foo_memo
        >>> assert method1('a') == ('b', 'F1')
        >>> assert method2('a') == (0, 'F2')
        >>> assert method1('z') == ('z2', 'F1')
        >>> assert method2('z') == ('z2', 'F2')
    """

    __func__: Callable[..., Any]

    def __init__(self, func: Callable[..., Any]) -> None:
        """
        Args:
            func (Callable): method to wrap
        """
        self._func = func
        self._cache_name = '_cache__' + func.__name__  # type: ignore[invalid-assignment]
        # Mimic attributes of a bound method
        self.__func__ = func  # type: ignore[invalid-assignment]
        functools.update_wrapper(self, func)  # type: ignore[invalid-argument-type]

    def __get__(self, instance: object, cls: type | None = None):
        """
        Descriptor get method. Called when the decorated method is accessed
        from an object instance.

        Args:
            instance (object): the instance of the class with the memoized method
            cls (type | None): the type of the instance
        """
        import types

        unbound = self._func
        cache = instance.__dict__.setdefault(self._cache_name, {})

        # https://stackoverflow.com/questions/71413937/what-does-using-get-on-a-function-do
        @functools.wraps(unbound)
        def memoizer(instance, *args, **kwargs):
            key = _make_signature_key(args, kwargs)
            if key not in cache:
                cache[key] = unbound(instance, *args, **kwargs)
            return cache[key]

        # Bind the unbound memoizer to the instance
        bound_memoizer = types.MethodType(memoizer, instance)

        # Set the attribute to prevent calling __get__ again
        # Is there a better way to do this?
        setattr(instance, self._func.__name__, bound_memoizer)  # type: ignore[possibly-missing-attribute]
        return bound_memoizer


def memoize_property(fget: property | typing.Callable):
    """
    Return a property attribute for new-style classes that only calls its
    getter on the first access. The result is stored and on subsequent accesses
    is returned, preventing the need to call the getter any more.

    This decorator can either be used by itself or by decorating another
    property. In either case the method will always become a property.

    Note:
        implementation is a modified version of [estebistec_memoize]_.

    References:
        .. [estebistec_memoize] https://github.com/estebistec/python-memoized-property

    Args:
        fget (property | Callable): A property or a method.

    Example:
        >>> import ubelt as ub
        >>> class C:
        ...     load_name_count = 0
        ...     @ub.memoize_property
        ...     def name(self):
        ...         "name's docstring"
        ...         self.load_name_count += 1
        ...         return "the name"
        ...     @ub.memoize_property
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
        fget = fget.fget  # type: ignore[invalid-assignment]

    attr_name = '_' + fget.__name__  # type: ignore[unresolved-attribute]

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)
