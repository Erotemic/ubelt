# -*- coding: utf-8 -*-
r"""
Expose functions to simplify importing from module names and paths.

Partial Autogenerate:
    import netharn as nh
    closer = nh.export.closer.Closer()
    from xdoctest import static_analysis as static
    from xdoctest import utils

    closer.add_dynamic(static.split_modpath)
    closer.add_dynamic(static.modpath_to_modname)
    closer.add_dynamic(static.modname_to_modpath)
    closer.add_dynamic(utils.import_module_from_name)
    closer.add_dynamic(utils.import_module_from_path)

    closer.expand(['xdoctest'])
    text = closer.current_sourcecode()
    print(text)

    text = text.replace('    from xdoctest.static_analysis import split_modpath, modpath_to_modname\n', '')

    fpath = ub.expandpath('~/code/ubelt/ubelt/_autogen_util_import.py')
    open(fpath, 'w').write(text + '\n')
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import (abspath, exists, expanduser, isdir, join, split, dirname,
                     relpath, splitext, basename, isfile, realpath,)
import os
import six
import sys


__all__ = [
    'split_modpath',
    'modname_to_modpath',
    'modpath_to_modname',
    'import_module_from_name',
    'import_module_from_path',
]


class PythonPathContext(object):
    """
    Context for temporarily adding a dir to the PYTHONPATH. Used in testing

    Args:
        dpath (str): directory to insert into the PYTHONPATH
        index (int): position to add to. Typically either -1 or 0.

    Example:
        >>> with PythonPathContext('foo', -1):
        >>>     assert sys.path[-1] == 'foo'
        >>> assert sys.path[-1] != 'foo'
        >>> with PythonPathContext('bar', 0):
        >>>     assert sys.path[0] == 'bar'
        >>> assert sys.path[0] != 'bar'
    """
    def __init__(self, dpath, index=-1):
        self.dpath = dpath
        self.index = index

    def __enter__(self):
        if self.index < 0:
            self.index = len(sys.path) + self.index + 1
        sys.path.insert(self.index, self.dpath)

    def __exit__(self, type, value, trace):
        msg_parts = [
            'sys.path significantly changed while in PythonPathContext.'
        ]
        if len(sys.path) <= self.index:  # nocover
            msg_parts.append(
                'len(sys.path) = {!r} but index is {!r}'.format(
                    len(sys.path), self.index))
            raise AssertionError('\n'.join(msg_parts))

        if sys.path[self.index] != self.dpath:  # nocover
            msg_parts.append(
                'Expected {!r} at index {!r} but got {!r}'.format(
                    self.dpath, self.index, sys.path[self.index]
                ))
            try:
                real_index = sys.path.index(self.dpath)
                msg_parts.append('Expected dpath was at index {}'.format(real_index))
                msg_parts.append('This could indicate conflicting module namespaces')
            except IndexError:
                msg_parts.append('Expected dpath was not in sys.path')
            raise AssertionError('\n'.join(msg_parts))
        sys.path.pop(self.index)


def _custom_import_modpath(modpath, index=-1):
    dpath, rel_modpath = split_modpath(modpath)
    modname = modpath_to_modname(modpath)
    try:
        with PythonPathContext(dpath, index=index):
            module = import_module_from_name(modname)
    except Exception:  # nocover
        print('Failed to import modname={} with modpath={}'.format(
            modname, modpath))
        raise
    return module


def import_module_from_path(modpath, index=-1):
    """
    Imports a module via its path

    Args:
        modpath (PathLike): path to the module on disk or within a zipfile.

    Returns:
        module: the imported module

    References:
        https://stackoverflow.com/questions/67631/import-module-given-path

    Notes:
        If the module is part of a package, the package will be imported first.
        These modules may cause problems when reloading via IPython magic

        This can import a module from within a zipfile. To do this modpath
        should specify the path to the zipfile and the path to the module
        within that zipfile separated by a colon or pathsep.
        E.g. `/path/to/archive.zip:mymodule.py`

    Warning:
        It is best to use this with paths that will not conflict with
        previously existing modules.

        If the modpath conflicts with a previously existing module name. And
        the target module does imports of its own relative to this conflicting
        path. In this case, the module that was loaded first will win.

        For example if you try to import '/foo/bar/pkg/mod.py' from the folder
        structure:
          - foo/
            +- bar/
               +- pkg/
                  +  __init__.py
                  |- mod.py
                  |- helper.py

       If there exists another module named `pkg` already in sys.modules
       and mod.py does something like `from . import helper`, Python will
       assume helper belongs to the `pkg` module already in sys.modules.
       This can cause a NameError or worse --- a incorrect helper module.

    Example:
        >>> import xdoctest
        >>> modpath = xdoctest.__file__
        >>> module = import_module_from_path(modpath)
        >>> assert module is xdoctest

    Example:
        >>> # Test importing a module from within a zipfile
        >>> import zipfile
        >>> from xdoctest import utils
        >>> from os.path import join, expanduser
        >>> dpath = expanduser('~/.cache/xdoctest')
        >>> dpath = utils.ensuredir(dpath)
        >>> #dpath = utils.TempDir().ensure()
        >>> # Write to an external module named bar
        >>> external_modpath = join(dpath, 'bar.py')
        >>> open(external_modpath, 'w').write('testvar = 1')
        >>> internal = 'folder/bar.py'
        >>> # Move the external bar module into a zipfile
        >>> zippath = join(dpath, 'myzip.zip')
        >>> with zipfile.ZipFile(zippath, 'w') as myzip:
        >>>     myzip.write(external_modpath, internal)
        >>> # Import the bar module from within the zipfile
        >>> modpath = zippath + ':' + internal
        >>> modpath = zippath + os.path.sep + internal
        >>> module = import_module_from_path(modpath)
        >>> assert module.__name__ == os.path.normpath('folder/bar')
        >>> assert module.testvar == 1

    Doctest:
        >>> import pytest
        >>> with pytest.raises(IOError):
        >>>     import_module_from_path('does-not-exist')
        >>> with pytest.raises(IOError):
        >>>     import_module_from_path('does-not-exist.zip/')
    """
    import os
    if not os.path.exists(modpath):
        import re
        import zipimport
        # We allow (if not prefer or force) the colon to be a path.sep in order
        # to agree with the mod.__name__ attribute that will be produced

        # zip followed by colon or slash
        pat = '(.zip[' + re.escape(os.path.sep) + '/:])'
        parts = re.split(pat, modpath, flags=re.IGNORECASE)
        if len(parts) > 2:
            archivepath = ''.join(parts[:-1])[:-1]
            internal = parts[-1]
            modname = os.path.splitext(internal)[0]
            modname = os.path.normpath(modname)
            if os.path.exists(archivepath):
                zimp_file = zipimport.zipimporter(archivepath)
                module = zimp_file.load_module(modname)
                return module
        raise IOError('modpath={} does not exist'.format(modpath))
    else:
        # the importlib version doesnt work in pytest
        module = _custom_import_modpath(modpath)
        # TODO: use this implementation once pytest fixes importlib
        # module = _pkgutil_import_modpath(modpath)
        return module


def import_module_from_name(modname):
    """
    Imports a module from its string name (__name__)

    Args:
        modname (str):  module name

    Returns:
        module: module

    Example:
        >>> # test with modules that wont be imported in normal circumstances
        >>> # todo write a test where we gaurentee this
        >>> modname_list = [
        >>>     'pickletools',
        >>>     'lib2to3.fixes.fix_apply',
        >>> ]
        >>> #assert not any(m in sys.modules for m in modname_list)
        >>> modules = [import_module_from_name(modname) for modname in modname_list]
        >>> assert [m.__name__ for m in modules] == modname_list
        >>> assert all(m in sys.modules for m in modname_list)
    """
    if True:
        # See if this fixes the Docker issue we saw but were unable to
        # reproduce on another environment. Either way its better to use the
        # standard importlib implementation than the one I wrote a long time
        # ago.
        import importlib
        module = importlib.import_module(modname)
    else:
        # The __import__ statment is weird
        if '.' in modname:
            fromlist = modname.split('.')[-1]
            fromlist_ = list(map(str, fromlist))  # needs to be ascii for python2.7
            module = __import__(modname, {}, {}, fromlist_, 0)
        else:
            module = __import__(modname, {}, {}, [], 0)
    return module


def _extension_module_tags():
    """
    Returns valid tags an extension module might have
    """
    import sysconfig
    tags = []
    if six.PY2:
        # see also 'SHLIB_EXT'
        multiarch = sysconfig.get_config_var('MULTIARCH')
        if multiarch is not None:
            tags.append(multiarch)
    else:
        # handle PEP 3149 -- ABI version tagged .so files
        # ABI = application binary interface
        tags.append(sysconfig.get_config_var('SOABI'))
        tags.append('abi3')  # not sure why this one is valid but it is
    tags = [t for t in tags if t]
    return tags


def _platform_pylib_exts():  # nocover
    """
    Returns .so, .pyd, or .dylib depending on linux, win or mac.
    On python3 return the previous with and without abi (e.g.
    .cpython-35m-x86_64-linux-gnu) flags. On python2 returns with
    and without multiarch.
    """
    import sysconfig
    valid_exts = []
    if six.PY2:
        # see also 'SHLIB_EXT'
        base_ext = '.' + sysconfig.get_config_var('SO').split('.')[-1]
    else:
        # return with and without API flags
        # handle PEP 3149 -- ABI version tagged .so files
        base_ext = '.' + sysconfig.get_config_var('EXT_SUFFIX').split('.')[-1]
    for tag in _extension_module_tags():
        valid_exts.append('.' + tag + base_ext)
    valid_exts.append(base_ext)
    return tuple(valid_exts)


def _syspath_modname_to_modpath(modname, sys_path=None, exclude=None):
    """
    syspath version of modname_to_modpath

    Args:
        modname (str): name of module to find
        sys_path (List[PathLike], default=None):
            if specified overrides `sys.path`
        exclude (List[PathLike], default=None):
            list of directory paths. if specified prevents these directories
            from being searched.

    Notes:
        This is much slower than the pkgutil mechanisms.

    CommandLine:
        python -m xdoctest.static_analysis _syspath_modname_to_modpath

    Example:
        >>> print(_syspath_modname_to_modpath('xdoctest.static_analysis'))
        ...static_analysis.py
        >>> print(_syspath_modname_to_modpath('xdoctest'))
        ...xdoctest
        >>> print(_syspath_modname_to_modpath('_ctypes'))
        ..._ctypes...
        >>> assert _syspath_modname_to_modpath('xdoctest', sys_path=[]) is None
        >>> assert _syspath_modname_to_modpath('xdoctest.static_analysis', sys_path=[]) is None
        >>> assert _syspath_modname_to_modpath('_ctypes', sys_path=[]) is None
        >>> assert _syspath_modname_to_modpath('this', sys_path=[]) is None

    Example:
        >>> # test what happens when the module is not visible in the path
        >>> modname = 'xdoctest.static_analysis'
        >>> modpath = _syspath_modname_to_modpath(modname)
        >>> exclude = [split_modpath(modpath)[0]]
        >>> found = _syspath_modname_to_modpath(modname, exclude=exclude)
        >>> # this only works if installed in dev mode, pypi fails
        >>> assert found is None, 'should not have found {}'.format(found)
    """

    def _isvalid(modpath, base):
        # every directory up to the module, should have an init
        subdir = dirname(modpath)
        while subdir and subdir != base:
            if not exists(join(subdir, '__init__.py')):
                return False
            subdir = dirname(subdir)
        return True

    _fname_we = modname.replace('.', os.path.sep)
    candidate_fnames = [
        _fname_we + '.py',
        # _fname_we + '.pyc',
        # _fname_we + '.pyo',
    ]
    # Add extension library suffixes
    candidate_fnames += [_fname_we + ext for ext in _platform_pylib_exts()]

    if sys_path is None:
        sys_path = sys.path

    # the empty string in sys.path indicates cwd. Change this to a '.'
    candidate_dpaths = ['.' if p == '' else p for p in sys_path]

    if exclude:
        def normalize(p):
            if sys.platform.startswith('win32'):  # nocover
                return realpath(p).lower()
            else:
                return realpath(p)
        # Keep only the paths not in exclude
        real_exclude = {normalize(p) for p in exclude}
        candidate_dpaths = [p for p in candidate_dpaths
                            if normalize(p) not in real_exclude]

    for dpath in candidate_dpaths:
        # Check for directory-based modules (has presidence over files)
        modpath = join(dpath, _fname_we)
        if exists(modpath):
            if isfile(join(modpath, '__init__.py')):
                if _isvalid(modpath, dpath):
                    return modpath

        # If that fails, check for file-based modules
        for fname in candidate_fnames:
            modpath = join(dpath, fname)
            if isfile(modpath):
                if _isvalid(modpath, dpath):
                    return modpath


def modname_to_modpath(modname, hide_init=True, hide_main=False, sys_path=None):
    """
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
        sys_path (list): if specified overrides `sys.path` (default None)

    Returns:
        str: modpath - path to the module, or None if it doesn't exist

    CommandLine:
        python -m xdoctest.static_analysis modname_to_modpath:0
        pytest  /home/joncrall/code/xdoctest/xdoctest/static_analysis.py::modname_to_modpath:0

    Example:
        >>> modname = 'xdoctest.__main__'
        >>> modpath = modname_to_modpath(modname, hide_main=False)
        >>> assert modpath.endswith('__main__.py')
        >>> modname = 'xdoctest'
        >>> modpath = modname_to_modpath(modname, hide_init=False)
        >>> assert modpath.endswith('__init__.py')
        >>> modpath = basename(modname_to_modpath('_ctypes'))
        >>> assert 'ctypes' in modpath
    """
    modpath = _syspath_modname_to_modpath(modname, sys_path)
    if modpath is None:
        return None

    modpath = normalize_modpath(modpath, hide_init=hide_init,
                                hide_main=hide_main)
    return modpath


def normalize_modpath(modpath, hide_init=True, hide_main=False):
    """
    Normalizes __init__ and __main__ paths.

    Notes:
        Adds __init__ if reasonable, but only removes __main__ by default

    Args:
        hide_init (bool): if True, always return package modules
           as __init__.py files otherwise always return the dpath.
        hide_init (bool): if True, always strip away main files otherwise
           ignore __main__.py.

    CommandLine:
        xdoctest -m xdoctest.static_analysis normalize_modpath

    Example:
        >>> import xdoctest.static_analysis as static
        >>> modpath = static.__file__
        >>> assert static.normalize_modpath(modpath) == modpath.replace('.pyc', '.py')
        >>> dpath = dirname(modpath)
        >>> res0 = static.normalize_modpath(dpath, hide_init=0, hide_main=0)
        >>> res1 = static.normalize_modpath(dpath, hide_init=0, hide_main=1)
        >>> res2 = static.normalize_modpath(dpath, hide_init=1, hide_main=0)
        >>> res3 = static.normalize_modpath(dpath, hide_init=1, hide_main=1)
        >>> assert res0.endswith('__init__.py')
        >>> assert res1.endswith('__init__.py')
        >>> assert not res2.endswith('.py')
        >>> assert not res3.endswith('.py')
    """
    if six.PY2:
        if modpath.endswith('.pyc'):
            modpath = modpath[:-1]
    if hide_init:
        if basename(modpath) == '__init__.py':
            modpath = dirname(modpath)
            hide_main = True
    else:
        # add in init, if reasonable
        modpath_with_init = join(modpath, '__init__.py')
        if exists(modpath_with_init):
            modpath = modpath_with_init
    if hide_main:
        # We can remove main, but dont add it
        if basename(modpath) == '__main__.py':
            # corner case where main might just be a module name not in a pkg
            parallel_init = join(dirname(modpath), '__init__.py')
            if exists(parallel_init):
                modpath = dirname(modpath)
    return modpath


def modpath_to_modname(modpath, hide_init=True, hide_main=False, check=True,
                       relativeto=None):
    """
    Determines importable name from file path

    Converts the path to a module (__file__) to the importable python name
    (__name__) without importing the module.

    The filename is converted to a module name, and parent directories are
    recursively included until a directory without an __init__.py file is
    encountered.

    Args:
        modpath (str): module filepath
        hide_init (bool): removes the __init__ suffix (default True)
        hide_main (bool): removes the __main__ suffix (default False)
        check (bool): if False, does not raise an error if modpath is a dir
            and does not contain an __init__ file.
        relativeto (str, optional): if specified, all checks are ignored and
            this is considered the path to the root module.

    Returns:
        str: modname

    Raises:
        ValueError: if check is True and the path does not exist

    CommandLine:
        xdoctest -m xdoctest.static_analysis modpath_to_modname

    Example:
        >>> from xdoctest import static_analysis
        >>> modpath = static_analysis.__file__.replace('.pyc', '.py')
        >>> modpath = modpath.replace('.pyc', '.py')
        >>> modname = modpath_to_modname(modpath)
        >>> assert modname == 'xdoctest.static_analysis'

    Example:
        >>> import xdoctest
        >>> assert modpath_to_modname(xdoctest.__file__.replace('.pyc', '.py')) == 'xdoctest'
        >>> assert modpath_to_modname(dirname(xdoctest.__file__.replace('.pyc', '.py'))) == 'xdoctest'

    Example:
        >>> modpath = modname_to_modpath('_ctypes')
        >>> modname = modpath_to_modname(modpath)
        >>> assert modname == '_ctypes'
    """
    if check and relativeto is None:
        if not exists(modpath):
            raise ValueError('modpath={} does not exist'.format(modpath))
    modpath_ = abspath(expanduser(modpath))

    modpath_ = normalize_modpath(modpath_, hide_init=hide_init,
                                 hide_main=hide_main)
    if relativeto:
        dpath = dirname(abspath(expanduser(relativeto)))
        rel_modpath = relpath(modpath_, dpath)
    else:
        dpath, rel_modpath = split_modpath(modpath_, check=check)

    modname = splitext(rel_modpath)[0]
    if '.' in modname:
        modname, abi_tag = modname.split('.')
    modname = modname.replace('/', '.')
    modname = modname.replace('\\', '.')
    return modname


def split_modpath(modpath, check=True):
    """
    Splits the modpath into the dir that must be in PYTHONPATH for the module
    to be imported and the modulepath relative to this directory.

    Args:
        modpath (str): module filepath
        check (bool): if False, does not raise an error if modpath is a
            directory and does not contain an `__init__.py` file.

    Returns:
        tuple: (directory, rel_modpath)

    Raises:
        ValueError: if modpath does not exist or is not a package

    Example:
        >>> from xdoctest import static_analysis
        >>> modpath = static_analysis.__file__.replace('.pyc', '.py')
        >>> modpath = abspath(modpath)
        >>> dpath, rel_modpath = split_modpath(modpath)
        >>> recon = join(dpath, rel_modpath)
        >>> assert recon == modpath
        >>> assert rel_modpath == join('xdoctest', 'static_analysis.py')
    """
    if six.PY2:
        if modpath.endswith('.pyc'):
            modpath = modpath[:-1]
    modpath_ = abspath(expanduser(modpath))
    if check:
        if not exists(modpath_):
            if not exists(modpath):
                raise ValueError('modpath={} does not exist'.format(modpath))
            raise ValueError('modpath={} is not a module'.format(modpath))
        if isdir(modpath_) and not exists(join(modpath, '__init__.py')):
            # dirs without inits are not modules
            raise ValueError('modpath={} is not a module'.format(modpath))
    full_dpath, fname_ext = split(modpath_)
    _relmod_parts = [fname_ext]
    # Recurse down directories until we are out of the package
    dpath = full_dpath
    while exists(join(dpath, '__init__.py')):
        dpath, dname = split(dpath)
        _relmod_parts.append(dname)
    relmod_parts = _relmod_parts[::-1]
    rel_modpath = os.path.sep.join(relmod_parts)
    return dpath, rel_modpath
