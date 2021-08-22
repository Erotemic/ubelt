# -*- coding: utf-8 -*-
"""
Helpers for functional programming.

The :func:`identity` function simply returns its own inputs. This is useful for
bypassing print statements and many other cases. I also think it looks a little
nicer than `lambda x: x`.

The :func:`inject` function "injects" another function into a class instance as a
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
        object: arg - the same value

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
        self (T): instance to inject a function into

        func (Callable[[T, ...], Any]):
            the function to inject (must contain an arg for self)

        name (str, default=None): name of the method. optional. If not
            specified the name of the function is used.

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


def compatible(config, func, start=0):
    """
    Take only the items of a dict that can be passed to function as kwargs

    Args:
        config (dict):
            a flat configuration dictionary

        func (Callable):
            a function or method

        start (int, default=0):
            Only take args after this position. Set to 1 if calling with an
            unbound method to avoid the "self" argument.

    Returns:
        dict : a subset of ``config`` that only contains items compatible with
            the signature of ``func``.

    TODO:
        - [ ] Move to util_func

    Example:
        >>> # An example use case is to select a subset of of a config
        >>> # that can be passed to some function as kwargs
        >>> from ubelt.util_candidate import *  # NOQA
        >>> # Define a function with args that match some keys in a config.
        >>> def func(a, e, f):
        >>>     return a * e * f
        >>> # Define a config that has a superset of items needed by the func
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> # Call the function only with keys that are compatible
        >>> func(**compatible(config, func))
        442

    Example:
        >>> # Test case with kwargs
        >>> from ubelt.util_candidate import *  # NOQA
        >>> def func(a, e, f, *args, **kwargs):
        >>>     return a * e * f
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> func(**compatible(config, func))

    Ignore:
        >>> # xdoctest: +REQUIRES(PY3)
        >>> # Test case with positional only 3.x +
        >>> def func(a, e, /,  f):
        >>>     return a * e * f
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> import pytest
        >>> with pytest.raises(ValueError):
        ...     func(**compatible(config, func))
    """
    import inspect
    if hasattr(inspect, 'signature'):  # pragma :nobranch
        sig = inspect.signature(func)
        argnames = []
        has_kwargs = False
        for arg in sig.parameters.values():
            if arg.kind == inspect.Parameter.VAR_KEYWORD:
                has_kwargs = True
            elif arg.kind == inspect.Parameter.VAR_POSITIONAL:
                # Ignore variadic positional args
                pass
            elif arg.kind == inspect.Parameter.POSITIONAL_ONLY:
                raise ValueError('this does not work with positional only')
            elif arg.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD,
                              inspect.Parameter.KEYWORD_ONLY}:
                argnames.append(arg.name)
            else:  # nocover
                raise TypeError(arg.kind)
    else:  # nocover
        # For Python 2.7
        spec = inspect.getargspec(func)
        argnames = spec.args
        has_kwargs = spec.keywords

    if has_kwargs:
        # kwargs could be anything, so keep everything
        common = config
    else:
        common = {k: config[k] for k in argnames[start:]
                  if k in config}  # dict-isect
    return common
