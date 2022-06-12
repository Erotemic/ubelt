"""
This module defines :data:`ub.NoParam`. This is a robust sentinel value that
can act like ``None`` when None might be a valid value. The value of
:data:`NoParam` is robust to reloading, pickling, and copying (i.e. ``var is
ub.NoParam`` will return ``True`` after these operations).

Use cases that demonstrate the value of :data:`NoParam` can be found in
:mod:`ubelt.util_dict`, where it simplifies the implementation of methods that
behave like :meth:`dict.get`.

Example:
    >>> import ubelt as ub
    >>> def func(a=ub.NoParam):
    >>>     if a is ub.NoParam:
    >>>         print('no param specified')
    >>>     else:
    >>>         print('a = {}'.format(a))
    >>> func()
    no param specified
    >>> func(a=None)
    a = None
    >>> func(a=1)
    a = 1
    >>> # note: typically it is bad practice to use NoParam as an actual
    >>> # (non-default) parameter. It goes against the sprit of the idea.
    >>> func(a=ub.NoParam)
    no param specified
"""

__all__ = ['NoParam']


class NoParamType(object):
    r"""
    Class used to define :data:`NoParam`, a sentinel that acts like None when
    None might be a valid value. The value of :data:`NoParam` is robust to
    reloading, pickling, and copying. See [SO_41048643]_ for more details.

    However, try to never assign this value to a persistent variable.  Use this
    class sparingly.

    References:
        .. [SO_41048643]: http://stackoverflow.com/questions/41048643/a-second-none

    Example:
        >>> # Use case
        >>> # Imagine you need a function with a default argument, but you need to
        >>> # distinguish between cases where the user called it without specifying
        >>> # a default, versus the user specifying None. For instance, imagine you
        >>> # are writing the code for a dictionary ``get(key, default)``.
        >>> #
        >>> # You want the user to distinguish between the user calling it with
        >>> # None and the user not calling it at all.
        >>> #
        >>> # So you can't write it like this because you can't distinguish between
        >>> # the user passing default as None, or not passing a default at all.
        >>> def get(self, key, default=None):
        >>>     if default is None:
        >>>         ...  # What do?!
        >>> #
        >>> # You could write it like this, which is long and annoying
        >>> def get(self, key, *args, **kw):
        >>>     try:
        >>>         return self[key]
        >>>     except KeyError as ke:
        >>>         if len(args) > 0:
        >>>             return args[0]
        >>>         elif 'default' in kw:
        >>>             return kw['default']
        >>>         else:
        >>>             raise
        >>> #
        >>> # Instead write it like this, which is short and nice
        >>> from ubelt import NoParam
        >>> def get(self, key, default=NoParam):
        >>>     try:
        >>>         return self[key]
        >>>     except KeyError:
        >>>         if default is NoParam:
        >>>             raise
        >>>         return default
        >>> #
        >>> # setup some data
        >>> self = {}
        >>> key = 'spam'
        >>> #
        >>> # If the key is not in the dictionary, raise a KeyError
        >>> import pytest
        >>> with pytest.raises(KeyError):
        >>>     get(self, key)
        >>> #
        >>> # If the key is not in the dictionary, return ``default``
        >>> get(self, key, None)  # with positional args
        >>> get(self, key, default=None)  # with keyword args

    Example:
        >>> import ubelt as ub
        >>> from ubelt import util_const
        >>> from ubelt.util_const import NoParamType, NoParam
        >>> import pickle
        >>> import copy
        >>> id_ = id(NoParam)
        >>> versions = {
        ... 'ub.util_const.NoParam': ub.util_const.NoParam,
        ... 'NoParam': NoParam,
        ... 'NoParamType()': NoParamType(),
        ... 'ub.NoParam': ub.NoParam,
        ... 'copy': copy.copy(NoParam),
        ... 'deepcopy': copy.deepcopy(NoParam),
        ... 'pickle': pickle.loads(pickle.dumps(NoParam))
        ... }
        >>> print(versions)
        >>> assert all(id(v) == id_ for v in versions.values())
        >>> from importlib import reload
        >>> reload(util_const)
        >>> assert id(util_const.NoParam) == id_
        >>> assert all(id(v) == id_ for v in versions.values())
        >>> assert str(NoParam) == repr(NoParam)
        >>> assert not any(v for v in versions.values())
        >>> assert all(not v for v in versions.values())
        >>> assert all(not bool(v) for v in versions.values())
    """
    def __new__(cls):
        return NoParam
    def __reduce__(self):
        return (NoParamType, ())
    def __copy__(self):
        return NoParam
    def __deepcopy__(self, memo):
        return NoParam
    def __str__(cls):
        return 'NoParam'
    def __repr__(cls):
        return 'NoParam'
    def __bool__(self):
        # Ensure NoParam is Falsey
        return False

# Backwards compat
_NoParamType = NoParamType

# Create the only instance of NoParamType that should ever exist
try:
    # If the module is reloaded (via imp.reload), globals() will contain
    # NoParam. This skips the code that would instantiate a second object
    NoParam  # pragma: no cover
    # Note: it is possible to hack around this via
    # >>> del util_const.NoParam
    # >>> imp.reload(util_const)
except NameError:  # pragma: no cover
    # When the module is first loaded, globals() will not contain NoParam. A
    # NameError will be thrown, causing the first instance of NoParam to be
    # instantiated.
    NoParam = object.__new__(NoParamType)  # type: NoParamType
