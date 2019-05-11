# -*- coding: utf-8 -*-
"""
Helpers for functional programming.

The `identity` function simply returns its own inputs. This is useful for
bypassing print statements and many other cases. I also think it looks a little
nicer than `lambda x: x`.

The `inject` function "injects" another function into a class instance as a
method. This is useful for monkey patching.
"""


def identity(arg=None, *args, **kwargs):
    """
    The identity function. Simply returns the value of its first input.

    All other inputs are ignored. Defaults to None if called without args.

    Args:
        arg (object, default=None): some value
        *args: ignored
        **kwargs: ignored

    Returns:
        object: arg: the same value

    CommandLine:
        xdoctest -m ubelt.util_func identity

    Example:
        >>> import ubelt as ub
        >>> ub.identity(42)
        42
        >>> ub.identity(42, 42)
        42
        >>> ub.identity()
        None
    """
    return arg


def inject_method(self, func, name=None):
    """
    Injects a function into an object instance as a bound method

    The main use case of this function is for monkey patching. While monkey
    patching is sometimes necessary it should generally be avoided. Thus, we
    simply remind the developer that there might be a better way.

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
    # TODO: if func is a bound method we should probably unbind it
    new_method = func.__get__(self, self.__class__)
    if name is None:
        name = func.__name__
    setattr(self, name, new_method)
