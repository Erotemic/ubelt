# -*- coding: utf-8 -*-
"""
This module defines the `NiceRepr` mixin class, which defines a `__repr__` and
`__str__` method that only depend on a custom `__nice__` method, which you must
define. This means you only have to overload one function instead of two.
Furthermore, if the object defines a `__len__` method, then the `__nice__`
method defaults to something sensible, otherwise it is treated as abstract and
raises `NotImplementedError`.

To use simply have your object inherit from `NiceRepr` (multi-inheritance
should be ok).

CommandLine:
    xdoctest -m ubelt.util_mixins __doc__

Example:
    >>> # Objects that define __nice__ have a default __str__ and __repr__
    >>> import ubelt as ub
    >>> class Student(ub.NiceRepr):
    ...    def __init__(self, name):
    ...        self.name = name
    ...    def __nice__(self):
    ...        return self.name
    >>> s1 = Student('Alice')
    >>> s2 = Student('Bob')
    >>> print('s1 = {}'.format(s1))
    >>> print('s2 = {}'.format(s2))
    s1 = <Student(Alice)>
    s2 = <Student(Bob)>

Example:
    >>> # Objects that define __len__ have a default __nice__
    >>> import ubelt as ub
    >>> class Group(ub.NiceRepr):
    ...    def __init__(self, data):
    ...        self.data = data
    ...    def __len__(self):
    ...        return len(self.data)
    >>> g = Group([1, 2, 3])
    >>> print('g = {}'.format(g))
    g = <Group(3)>

"""
from __future__ import absolute_import, division, print_function, unicode_literals
import warnings


class NiceRepr(object):
    """
    Defines `__str__` and `__repr__` in terms of `__nice__` function
    Classes that inherit from `NiceRepr` must define `__nice__`

    Example:
        >>> import ubelt as ub
        >>> class Foo(ub.NiceRepr):
        ...    def __nice__(self):
        ...        return 'info'
        >>> foo = Foo()
        >>> assert str(foo) == '<Foo(info)>'
        >>> assert repr(foo).startswith('<Foo(info) at ')

    Example:
        >>> import ubelt as ub
        >>> class Bar(ub.NiceRepr):
        ...    pass
        >>> bar = Bar()
        >>> import pytest
        >>> with pytest.warns(None) as record:
        >>>     assert 'object at' in str(bar)
        >>>     assert 'object at' in repr(bar)

    Example:
        >>> import ubelt as ub
        >>> class Baz(ub.NiceRepr):
        ...    def __len__(self):
        ...        return 5
        >>> baz = Baz()
        >>> assert str(baz) == '<Baz(5)>'
    """

    def __nice__(self):
        if hasattr(self, '__len__'):
            # It is a common pattern for objects to use __len__ in __nice__
            # As a convenience we define a default __nice__ for these objects
            return str(len(self))
        else:
            # In all other cases force the subclass to overload __nice__
            raise NotImplementedError(
                'Define the __nice__ method for %r' % (self.__class__,))

    def __repr__(self):
        try:
            devnice = self.__nice__()
            classname = self.__class__.__name__
            return '<%s(%s) at %s>' % (classname, devnice, hex(id(self)))
        except NotImplementedError as ex:
            warnings.warn(str(ex), category=RuntimeWarning)
            return object.__repr__(self)

    def __str__(self):
        try:
            classname = self.__class__.__name__
            devnice = self.__nice__()
            return '<%s(%s)>' % (classname, devnice)
        except NotImplementedError as ex:
            warnings.warn(str(ex), category=RuntimeWarning)
            return object.__repr__(self)
