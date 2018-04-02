# -*- coding: utf-8 -*-
"""
Helpers for functional programming
"""


def identity(arg):
    """
    The identity function. Simply returns its inputs.

    Example:
        >>> assert identity(42) == 42
    """
    return arg


def inject_method(self, func, name=None):
    """
    Injects a function into an object instance as a bound method

    Args:
        self (object): instance to inject a function into
        func (func): the function to inject (must contain an arg for self)
        name (str): name of the method. optional. If not specified the name
            of the function is used.

    Example:
        >>> class Foo(object):
        >>>     def bar(self):
        >>>         return 'bar'
        >>> def baz(self):
        >>>     return 'baz'
        >>> self = Foo()
        >>> assert self.bar() == 'bar'
        >>> assert not hasattr(self, 'baz')
        >>> inject_method(self, baz)
        >>> assert not hasattr(Foo, 'baz'), 'should only change one instance'
        >>> assert self.baz() == 'baz'
        >>> inject_method(self, baz, 'bar')
        >>> assert self.bar() == 'baz'
    """
    new_method = func.__get__(self, self.__class__)
    if name is None:
        name = func.__name__
    setattr(self, name, new_method)
