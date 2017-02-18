# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


class NiceRepr(object):
    """
    Defines `__str__` and `__repr__` in terms of `__nice__` function
    Classes that inherit `NiceRepr` must define `__nice__`
    """
    def __repr__(self):
        try:
            classname = self.__class__.__name__
            devnice = self.__nice__()
            return '<%s(%s) at %s>' % (classname, devnice, hex(id(self)))
        except AttributeError:
            return object.__repr__(self)
            #return super(NiceRepr, self).__repr__()

    def __str__(self):
        try:
            classname = self.__class__.__name__
            devnice = self.__nice__()
            return '<%s(%s)>' % (classname, devnice)
        except AttributeError:
            warnings.warn('Error in __nice__ for %r' % (self.__class__,),
                          category=RuntimeWarning)
            if util_arg.SUPER_STRICT:
                raise
            else:
                return object.__str__(self)
