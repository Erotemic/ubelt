# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ast


class TopLevelDocstrVisitor(ast.NodeVisitor):
    """
    Other visit_<classname> values:
        http://greentreesnakes.readthedocs.io/en/latest/nodes.html
    """
    def __init__(self):
        super(TopLevelDocstrVisitor, self).__init__()
        self.docstrs = {}
        self._current_classname = None

    def visit_FunctionDef(self, node):
        funcname = node.name
        docstr = ast.get_docstring(node)
        if self._current_classname is None:
            self.docstrs[funcname] = docstr
        else:
            methodname = self._current_classname + '.' + funcname
            self.docstrs[methodname] = docstr

    def visit_ClassDef(self, node):
        classname = node.name
        docstr = ast.get_docstring(node)
        self._current_classname = classname
        self.docstrs[classname] = docstr
        self.generic_visit(node)
        self._current_classname = None

    def visit_Assign(self, node):
        # print('VISIT FunctionDef node = %r' % (node,))
        # print('VISIT FunctionDef node = %r' % (node.__dict__,))
        # for target in node.targets:
        #     print('target.id = %r' % (target.id,))
        # print('node.value = %r' % (node.value,))
        # TODO: assign constants to
        # self.const_lookup
        ast.NodeVisitor.generic_visit(self, node)


def parse_docstrs(source):
    r"""
    Statically finds docstrings in python source

    Args:
        source (str):

    CommandLine:
        python -m ubelt.static_analysis parse_docstrs

    Example:
        >>> import ubelt as ub
        >>> fpath = ub.static_analysis.__file__.replace('.pyc', '.py')
        >>> source = ub.readfrom(fpath)
        >>> parse_docstrs(source)
    """
    pt = ast.parse(source.encode('utf-8'))
    self = TopLevelDocstrVisitor()
    self.visit(pt)
    return self.docstrs


def package_modnames(package_name, with_pkg=False, with_mod=True,
                     ignore_prefix=[], ignore_suffix=[]):
    r"""
    Finds sub-packages and sub-modules belonging to a package.

    Args:
        package_name (str): package or module name
        with_pkg (bool): (default = False)
        with_mod (bool): (default = True)

    References:
        http://stackoverflow.com/questions/1707709/list-modules-in-py-package

    Example:
        >>> import ubelt as ub
        >>> package = ub
        >>> result = package_modnames(package)
        >>> print(result)
    """
    from os.path import isfile
    import pkgutil
    modpath = modname_to_modpath(package_name, hide_init=True)
    # If input is a file, just return it
    if isfile(modpath):
        return [package_name]
    # Otherwise, if it is a package, find sub-packages and sub-modules
    walker = pkgutil.walk_packages(
        [modpath], prefix=package_name + '.', onerror=lambda x: None)
    module_list = []
    for importer, modname, ispkg in walker:
        if any(modname.startswith(prefix) for prefix in ignore_prefix):
            continue
        if any(modname.endswith(suffix) for suffix in ignore_suffix):
            continue
        if not ispkg and with_mod:
            module_list.append(modname)
        if ispkg and with_pkg:
            module_list.append(modname)
    return module_list


def modpath_to_modname(modpath):
    r"""
    returns importable name from file path

    Args:
        modpath (str): module filepath

    Returns:
        str: modname

    Example:
        >>> modpath = ut.util_path.__file__
        >>> modname = ut.get_modname_from_modpath(modpath)
        >>> result = modname
        >>> print(result)
        utool.util_path
    """
    from os.path import join, exists, expanduser, realpath, split, splitext
    modpath_ = realpath(expanduser(modpath))
    full_dpath, fname_ext = split(modpath_)
    fname, ext = splitext(fname_ext)
    _modsubdir_list = [fname]
    # Recurse down directories until we are out of the package
    dpath = full_dpath
    while exists(join(dpath, '__init__.py')):
        dpath, dname = split(dpath)
        _modsubdir_list.append(dname)
    modsubdir_list = _modsubdir_list[::-1]
    modname = '.'.join(modsubdir_list)
    modname = modname.replace('.__init__', '').strip()
    modname = modname.replace('.__main__', '').strip()
    return modname



def modname_to_modpath(modname, hide_init=True, hide_main=True):
    r"""
    Determines the path to a python module without directly import it

    Args:
        modname (str): module filepath

    Returns:
        str: modpath

    Example:
        >>> import sys
        >>> modname = 'ubelt.progiter'
        >>> modpath = modname_to_modpath(modname)
        >>> assert modname not in sys.modules
    """
    from os.path import dirname, basename, join, exists
    import pkgutil
    init_name = '__init__.py'
    main_name = '__main__.py'
    loader = pkgutil.find_loader(modname)
    modpath = loader.get_filename().replace('.pyc', '.py')
    if '.' not in basename(modpath):
        modpath = join(modpath, init_name)
    if hide_init:
        if modpath.endswith(init_name) or modpath.endswith(main_name):
            modpath = dirname(modpath)
    if not hide_main:
        if modpath.endswith(init_name):
            main_modpath = modpath[:-len(init_name)] + main_name
            if exists(main_modpath):
                modpath = main_modpath
    return modpath


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.static_analysis
        python -m ubelt.static_analysis --allexamples
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
