# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import sys


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
        >>>     'test',
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
        if the module is part of a package, the package will be imported first

    Example:
        >>> from ubelt import util_import
        >>> modpath = util_import.__file__
        >>> module = import_module_from_path(modpath)
        >>> assert module is util_import
    """
    # the importlib version doesnt work in pytest
    import xdoctest.static_analysis as static
    dpath, rel_modpath = static.split_modpath(modpath)
    modname = static.modpath_to_modname(modpath)
    with PythonPathContext(dpath):
        module = import_module_from_name(modname)
    # TODO: use this implementation once pytest fixes importlib
    # if six.PY2:  # nocover
    #     import imp
    #     module = imp.load_source(modname, modpath)
    # elif sys.version_info[0:2] <= (3, 4):  # nocover
    #     assert sys.version_info[0:2] <= (3, 2), '3.0 to 3.2 is not supported'
    #     from importlib.machinery import SourceFileLoader
    #     module = SourceFileLoader(modname, modpath).load_module()
    # else:
    #     import importlib.util
    #     spec = importlib.util.spec_from_file_location(modname, modpath)
    #     module = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(module)
    return module
