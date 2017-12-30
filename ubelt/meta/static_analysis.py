# -*- coding: utf-8 -*-
"""
The static_analysis module in xdoctest should be used instead
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import pkgutil
from os.path import (join, exists, expanduser, abspath, split, splitext,
                     isfile, dirname)


def modpath_to_modname(modpath):
    r"""
    Determines importable name from file path

    Args:
        modpath (str): module filepath

    Returns:
        str: modname

    Example:
        >>> from ubelt.meta.static_analysis import *  # NOQA
        >>> import ubelt.meta.static_analysis
        >>> modpath = ubelt.meta.static_analysis.__file__
        >>> modpath = modpath.replace('.pyc', '.py')
        >>> print('modpath = %r' % (modpath))
        >>> modname = modpath_to_modname(modpath)
        >>> print('modname = %r' % (modname,))
        >>> assert modname == 'ubelt.meta.static_analysis'
    """
    from xdoctest import static_analysis as static
    return static.modpath_to_modname(modpath)


def modname_to_modpath(modname, hide_init=True, hide_main=True):  # nocover
    r"""
    Determines the path to a python module without directly import it

    Args:
        modname (str): module filepath

    Returns:
        str: modpath

    CommandLine:
        python -m ubelt.meta.static_analysis modname_to_modpath

    TODO:
        Test with a module we know wont be imported by ubelt.
        Maybe make this a non-doctest and put in tests directory.

    Example:
        >>> from ubelt.meta.static_analysis import *  # NOQA
        >>> import sys
        >>> modname = 'ubelt.progiter'
        >>> already_exists = modname in sys.modules
        >>> modpath = modname_to_modpath(modname)
        >>> print('modpath = %r' % (modpath,))
        >>> assert already_exists or modname not in sys.modules

    Example:
        >>> from ubelt.meta.static_analysis import *  # NOQA
        >>> import sys
        >>> modname = 'ubelt.__main__'
        >>> modpath = modname_to_modpath(modname, hide_main=False)
        >>> print('modpath = %r' % (modpath,))
        >>> assert modpath.endswith('__main__.py')
        >>> modname = 'ubelt'
        >>> modpath = modname_to_modpath(modname, hide_init=False)
        >>> print('modpath = %r' % (modpath,))
        >>> assert modpath.endswith('__init__.py')
        >>> modname = 'ubelt'
        >>> modpath = modname_to_modpath(modname, hide_init=False, hide_main=False)
        >>> print('modpath = %r' % (modpath,))
        >>> assert modpath.endswith('__init__.py')
    """
    from xdoctest import static_analysis as static
    return static.modname_to_modpath(modname, hide_init, hide_main)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.meta.static_analysis
        python -m ubelt.meta.static_analysis all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
