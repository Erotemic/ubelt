# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import functools


def memoize(func_or_method):
    """
    memoization decorator that respects args and kwargs and works for methods
    and functions.

    Args:
        func (function):  live python function or method

    Returns:
        func: memoized wrapper

    Note:
        This function cannot be wrapped because it relies on hard-coded stack
        offsets to determine if the wrapped function is being defined in the
        context of a class and hence should be treated as a method.
    """
    # Determine if the function is being defined in the context of a class
    # References:
    # https://stackoverflow.com/questions/8793233/python-can-a-decorator-determine-if-a-function-is-being-defined-inside-a-class
    import inspect
    frames = inspect.stack()
    defined_in_class = False
    if len(frames) > 2:
        maybe_class_frame = frames[2]
        statement_list = maybe_class_frame[4]
        first_statment = statement_list[0]
        if first_statment.strip().startswith('class '):
            defined_in_class = True
    if defined_in_class:
        return memoize_method
    else:
        return memoize_func


def memoize_func(func):
    """
    memoization decorator that respects args and kwargs

    Args:
        func (function):  live python function

    Returns:
        func: memoized wrapper

    References:
        https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

    CommandLine:
        python -m ubelt.util_decor memoize_func

    Example:
        >>> closure = {'a': 'b', 'c': 'd'}
        >>> incr = [0]
        >>> def foo(key):
        >>>     value = closure[key]
        >>>     incr[0] += 1
        >>>     return value
        >>> foo_memo = memoize_func(foo)
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
        print('func = {!r}'.format(func))
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
