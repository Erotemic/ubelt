"""
Helpers for functional programming.

The :func:`identity` function simply returns its own inputs. This is useful for
bypassing print statements and many other cases. I also think it looks a little
nicer than ``lambda x: x``.

The :func:`inject_method` function "injects" another function into a class
instance as a method. This is useful for monkey patching.

The :func:`compatible` introspects a functions signature for accepted keyword
arguments and returns the subset of a configuration dictionary that agrees with
that signature.
"""


def identity(arg=None, *args, **kwargs):
    """
    Return the value of the first argument unchanged.

    All other positional and keyword inputs are ignored. Defaults to None if
    called without any args.

    The name identity is used in the mathematical sense [WikiIdentity]_.  This
    is slightly different than the pure identity function, which is defined
    strictly with a single argument. This implementation allows but ignores
    extra arguments, making it easier to use as a drop in replacement for
    functions that accept extra configuration arguments that change their
    behavior and aren't true inputs.

    The value of this utility is a cleaner way to write ``lambda x: x`` or more
    precisely ``lambda x=None, *a, **k: x`` or writing the function inline.
    Unlike the lambda variant, this does not trigger common linter errors when
    assigning it to a value.

    Args:
        arg (Any, default=None): The value to return unchanged.
        *args: Ignored
        **kwargs: Ignored

    Returns:
        Any: arg - The same value of the first positional argument.

    References:
        .. [WikiIdentity] https://en.wikipedia.org/wiki/Identity_function

    Example:
        >>> import ubelt as ub
        >>> ub.identity(42)
        42
        >>> ub.identity(42, 43)
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
        self (T):
            Instance to inject a function into.

        func (Callable[..., Any]):
            The function to inject (must contain an arg for self).

        name (str, default=None):
            Name of the method. optional. If not specified the name of the
            function is used.

    Example:
        >>> import ubelt as ub
        >>> class Foo(object):
        >>>     def bar(self):
        >>>         return 'bar'
        >>> def baz(self):
        >>>     return 'baz'
        >>> self = Foo()
        >>> assert self.bar() == 'bar'
        >>> assert not hasattr(self, 'baz')
        >>> ub.inject_method(self, baz)
        >>> assert not hasattr(Foo, 'baz'), 'should only change one instance'
        >>> assert self.baz() == 'baz'
        >>> ub.inject_method(self, baz, 'bar')
        >>> assert self.bar() == 'baz'
    """
    # TODO: if func is a bound method we should probably unbind it
    new_method = func.__get__(self, self.__class__)
    if name is None:
        name = func.__name__
    setattr(self, name, new_method)


def compatible(config, func, start=0, keywords=True):
    """
    Take the "compatible" subset of a dictionary that a function will accept as
    keyword arguments.

    A common pattern is to track the configuration of a program in a single
    dictionary. Often there will be functions that only require subsets of this
    dictionary, and they will be written such that those items are passed via
    keyword arguments. The :func:`ubelt.compatible` utility makes it easier
    select only the relevant config variables. It does this by inspecting the
    signature of the function to determine what keyword arguments it accepts,
    and returns the dictionary intersection of the full config and the allowed
    keywords. The user can then call the function with the normal ``**``
    mechanism.

    Args:
        config (Dict[str, Any]):
            A dictionary that contains keyword arguments that might be passed
            to a function.

        func (Callable):
            A function or method to check the arguments of

        start (int):
            Only take args after this position. Set to 1 if calling with an
            unbound method to avoid the ``self`` argument. Defaults to 0.

        keywords (bool | Iterable[str]):
            If True (default), and ``**kwargs`` is in the signature, prevent
            any filtering of the ``config`` dictionary. If False, then ignore
            that ``**kwargs`` is in the signature and only return the subset of
            ``config`` that matches the explicit signature. Otherwise if
            specified as a non-string iterable of strings, assume these are the
            allowed keys that are compatible with the way ``kwargs`` is handled
            in the function.

    Returns:
        Dict[str, Any] :
            A subset of ``config`` that only contains items compatible with the
            signature of ``func``.

    Example:
        >>> # An example use case is to select a subset of of a config
        >>> # that can be passed to some function as kwargs
        >>> import ubelt as ub
        >>> # Define a function with args that match some keys in a config.
        >>> def func(a, e, f):
        >>>     return a * e * f
        >>> # Define a config that has a superset of items needed by the func
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> # Call the function only with keys that are compatible
        >>> func(**ub.compatible(config, func))
        442

    Example:
        >>> # Test case with kwargs
        >>> import ubelt as ub
        >>> def func(a, e, f, *args, **kwargs):
        >>>     return a * e * f
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> func(**ub.compatible(config, func))
        442
        >>> print(sorted(ub.compatible(config, func)))
        ['a', 'b', 'c', 'd', 'e', 'f']
        >>> print(sorted(ub.compatible(config, func, keywords=False)))
        ['a', 'e', 'f']
        >>> print(sorted(ub.compatible(config, func, keywords={'b'})))
        ['a', 'b', 'e', 'f']

    Ignore:
        # xdoctest: +REQUIRES(syntax:python>=3.6)  todo: new xdoctest directive?
        # Test case with positional only 3.6 +
        import ubelt as ub
        def func(a, e, /,  f):
            return a * e * f
        config = {
          'a': 2, 'b': 3, 'c': 7,
          'd': 11, 'e': 13, 'f': 17,
        }
        func(1, 2, **ub.compatible(config, func))
    """
    import inspect
    sig = inspect.signature(func)
    argnames = []
    has_kwargs = False
    for arg in sig.parameters.values():
        if arg.kind == inspect.Parameter.VAR_KEYWORD:
            has_kwargs = True
        elif arg.kind == inspect.Parameter.VAR_POSITIONAL:
            pass  # Ignore variadic positional args
        elif arg.kind == inspect.Parameter.POSITIONAL_ONLY:
            pass  # Ignore positional only arguments
        elif arg.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD,
                          inspect.Parameter.KEYWORD_ONLY}:
            argnames.append(arg.name)
        else:  # nocover
            raise TypeError(arg.kind)

    # Test if keywords is a non-string iterable
    if not isinstance(keywords, (bool, str)):
        try:
            iter(keywords)
        except Exception:
            keywords = bool(keywords)
        else:
            argnames.extend(keywords)
            keywords = False

    if has_kwargs and keywords:
        # kwargs could be anything, so keep everything
        common = config
    else:
        common = {k: config[k] for k in argnames[start:]
                  if k in config}  # dict-intersection
    return common


# class Function:
#     """
#     TODO
#     """
#     ...
