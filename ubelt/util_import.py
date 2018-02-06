# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import sys
from os.path import join  # NOQA


__all__ = [
    'split_modpath',
    'modname_to_modpath',
    'modpath_to_modname',
    'import_module_from_name',
    'import_module_from_path',
]


def split_modpath(modpath):
    """
    Splits the modpath into the dir that must be in PYTHONPATH for the module
    to be imported and the modulepath relative to this directory.

    Args:
        modpath (str): module filepath

    Returns:
        str: directory

    Example:
        >>> from xdoctest import static_analysis
        >>> modpath = static_analysis.__file__
        >>> modpath = modpath.replace('.pyc', '.py')
        >>> dpath, rel_modpath = split_modpath(modpath)
        >>> assert join(dpath, rel_modpath) == modpath
        >>> assert rel_modpath == join('xdoctest', 'static_analysis.py')
    """
    from xdoctest import static_analysis as static
    return static.split_modpath(modpath)


def modpath_to_modname(modpath, hide_init=True, hide_main=False):
    r"""
    Determines importable name from file path

    Converts the path to a module (__file__) to the importable python name
    (__name__) without importing the module.

    The filename is converted to a module name, and parent directories are
    recursively included until a directory without an __init__.py file is
    encountered.

    Args:
        modpath (str): module filepath
        hide_init (bool): removes the __init__ suffix (default True)
        hide_init (bool): removes the __main__ suffix (default False)

    Returns:
        str: modname

    Example:
        >>> import ubelt.util_import
        >>> modpath = ubelt.util_import.__file__
        >>> print(modpath_to_modname(modpath))
        ubelt.util_import
    """
    from xdoctest import static_analysis as static
    return static.modpath_to_modname(modpath, hide_init, hide_main)


def modname_to_modpath(modname, hide_init=True, hide_main=True):  # nocover
    r"""
    Finds the path to a python module from its name.

    Determines the path to a python module without directly import it

    Converts the name of a module (__name__) to the path (__file__) where it is
    located without importing the module. Returns None if the module does not
    exist.

    Args:
        modname (str): module filepath
        hide_init (bool): if False, __init__.py will be returned for packages
        hide_main (bool): if False, and hide_init is True, __main__.py will be
            returned for packages, if it exists.

    Returns:
        str: modpath - path to the module, or None if it doesn't exist

    CommandLine:
        python -m ubelt.util_import modname_to_modpath

    Example:
        >>> from ubelt.util_import import *  # NOQA
        >>> import sys
        >>> modname = 'ubelt.progiter'
        >>> already_exists = modname in sys.modules
        >>> modpath = modname_to_modpath(modname)
        >>> print('modpath = %r' % (modpath,))
        >>> assert already_exists or modname not in sys.modules

    Example:
        >>> from ubelt.util_import import *  # NOQA
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


class PythonPathContext(object):
    """
    Context for temporarilly adding a dir to the PYTHONPATH.
    """
    def __init__(self, dpath):
        self.dpath = dpath

    def __enter__(self):
        sys.path.append(self.dpath)

    def __exit__(self, a, b, c):
        assert sys.path[-1] == self.dpath
        sys.path.pop()


def import_module_from_name(modname):
    r"""
    Imports a module from its string name (__name__)

    Args:
        modname (str): module name

    Returns:
        module: module

    Example:
        >>> # test with modules that wont be imported in normal circumstances
        >>> # todo write a test where we gaurentee this
        >>> modname_list = [
        >>>     #'test',
        >>>     'pickletools',
        >>>     'lib2to3.fixes.fix_apply',
        >>> ]
        >>> #assert not any(m in sys.modules for m in modname_list)
        >>> modules = [import_module_from_name(modname) for modname in modname_list]
        >>> assert [m.__name__ for m in modules] == modname_list
        >>> assert all(m in sys.modules for m in modname_list)
    """
    # The __import__ statment is weird
    if '.' in modname:
        fromlist = modname.split('.')[-1]
        fromlist_ = list(map(str, fromlist))  # needs to be ascii for python2.7
        module = __import__(modname, {}, {}, fromlist_, 0)
    else:
        module = __import__(modname, {}, {}, [], 0)
    return module


def import_module_from_path(modpath):
    """
    Imports a module via its path

    Args:
        modpath (str): path to the module

    References:
        https://stackoverflow.com/questions/67631/import-module-given-path

    Notes:
        If the module is part of a package, the package will be imported first.
        These modules may cause problems when reloading via IPython magic

    TODO:
        handle modules inside of zipfiles

    Example:
        >>> from ubelt import util_import
        >>> modpath = util_import.__file__
        >>> module = import_module_from_path(modpath)
        >>> assert module is util_import
    """
    # the importlib version doesnt work in pytest
    module = _custom_import_modpath(modpath)
    # TODO: use this implementation once pytest fixes importlib
    # module = _pkgutil_import_modpath(modpath)
    return module


def _custom_import_modpath(modpath):
    import xdoctest.static_analysis as static
    dpath, rel_modpath = static.split_modpath(modpath)
    modname = static.modpath_to_modname(modpath)
    with PythonPathContext(dpath):
        module = import_module_from_name(modname)
    return module


def _pkgutil_import_modpath(modpath):  # nocover
    import six
    import xdoctest.static_analysis as static
    dpath, rel_modpath = static.split_modpath(modpath)
    modname = static.modpath_to_modname(modpath)
    if six.PY2:  # nocover
        import imp
        module = imp.load_source(modname, modpath)
    elif sys.version_info[0:2] <= (3, 4):  # nocover
        assert sys.version_info[0:2] <= (3, 2), '3.0 to 3.2 is not supported'
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(modname, modpath).load_module()
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(modname, modpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module
