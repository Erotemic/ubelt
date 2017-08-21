# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import warnings


class NiceRepr(object):
    """
    Defines `__str__` and `__repr__` in terms of `__nice__` function
    Classes that inherit `NiceRepr` must define `__nice__`

    Example:
        >>> import ubelt as ub
        >>> class Foo(ub.NiceRepr):
        ...    pass
        >>> class Bar(ub.NiceRepr):
        ...    def __nice__(self):
        ...        return 'info'
        >>> foo = Foo()
        >>> bar = Bar()
        >>> assert str(bar) == '<Bar(info)>'
        >>> assert repr(bar).startswith('<Bar(info) at ')
        >>> assert 'object at' in str(foo)
        >>> assert 'object at' in repr(foo)
    """
    def __repr__(self):
        try:
            classname = self.__class__.__name__
            devnice = self.__nice__()
            return '<%s(%s) at %s>' % (classname, devnice, hex(id(self)))
        except AttributeError:
            if hasattr(self, '__nice__'):
                raise
            warnings.warn('Define the __nice__ method for %r' %
                          (self.__class__,), category=RuntimeWarning)
            return object.__repr__(self)
            #return super(NiceRepr, self).__repr__()

    def __str__(self):
        try:
            classname = self.__class__.__name__
            devnice = self.__nice__()
            return '<%s(%s)>' % (classname, devnice)
        except AttributeError:
            if hasattr(self, '__nice__'):
                raise
            warnings.warn('Define the __nice__ method for %r' %
                          (self.__class__,), category=RuntimeWarning)
            return object.__str__(self)
            #return super(NiceRepr, self).__str__()
