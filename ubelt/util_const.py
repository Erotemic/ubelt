# -*- coding: utf-8 -*-
"""
This module defines `ub.NoParam`. This is a robust sentinel value that can act
like None when None might be a valid value. The value of `NoParam` is robust to
reloading, pickling, and copying (i.e. var is ub.NoParam will return True after
these operations)

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
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['NoParam']


class _NoParamType(object):
    r"""
    Class used to define `NoParam`, a sentinel that acts like None when None
    might be a valid value. The value of `NoParam` is robust to reloading,
    pickling, and copying.

    However, try to never assign this value to a persistent variable.  Use this
    class sparingly.

    CommandLine:
        xdoctest ubelt.util_const _NoParamType

    References:
        http://stackoverflow.com/questions/41048643/a-second-none

    Example:
        >>> import ubelt as ub
        >>> from ubelt import util_const
        >>> from ubelt.util_const import _NoParamType, NoParam
        >>> from six.moves import cPickle as pickle
        >>> import copy
        >>> id_ = id(NoParam)
        >>> versions = {
        ... 'ub.util_const.NoParam': ub.util_const.NoParam,
        ... 'NoParam': NoParam,
        ... '_NoParamType()': _NoParamType(),
        ... 'ub.NoParam': ub.NoParam,
        ... 'copy': copy.copy(NoParam),
        ... 'deepcopy': copy.deepcopy(NoParam),
        ... 'pickle': pickle.loads(pickle.dumps(NoParam))
        ... }
        >>> #print(ub.align(ub.repr4(ub.map_vals(id, versions)), ':'))
        >>> print(versions)
        >>> assert all(id(v) == id_ for v in versions.values())
        >>> import six
        >>> if six.PY2:
        >>>     from imp import reload
        >>> else:
        >>>     from importlib import reload
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
        return (_NoParamType, ())
    def __copy__(self):
        return NoParam
    def __deepcopy__(self, memo):
        return NoParam
    def __call__(self, default):
        pass
    def __str__(cls):
        return 'NoParam'
    def __repr__(cls):
        return 'NoParam'
        # return "<type 'NoParamType'>"
    def __bool__(self):
        # Ensure NoParam is Falsey
        return False
    # Same thing as __bool__ in Python 2.7
    __nonzero__ = __bool__


# Create the only instance of _NoParamType that should ever exist
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
    NoParam = object.__new__(_NoParamType)  # pragma: no cover
