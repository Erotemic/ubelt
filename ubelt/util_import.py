r"""
Expose functions to simplify importing from module names and paths.

The :func:`ubelt.import_module_from_path` function does its best to load a
python file into th current set of global modules.

The :func:`ubelt.import_module_from_name` works similarly.

The :func:`ubelt.modname_to_modpath` and :func:`ubelt.modname_to_modpath` work
statically and convert between module names and file paths on disk.

The :func:`ubelt.split_modpath` function separates modules into a root and base
path depending on where the first ``__init__.py`` file is.
"""
from os.path import (abspath, basename, dirname, exists, expanduser, isdir,
                     isfile, join, realpath, relpath, split, splitext)
import os
import sys
import warnings

__all__ = [
    'split_modpath',
    'modname_to_modpath',
    'modpath_to_modname',
    'import_module_from_name',
    'import_module_from_path',
]


class PythonPathContext(object):
    """
    Context for temporarily adding a dir to the PYTHONPATH.

    Used in testing, and used as a helper in certain ubelt functions.

    Warning:
        Even though this context manager takes precautions, this modifies
        ``sys.path``, and things can go wrong when that happens.  This is
        generally safe as long as nothing else you do inside of this context
        modifies the path. If the path is modified in this context, we will try
        to detect it and warn.

    Args:
        dpath (str | PathLike): directory to insert into the PYTHONPATH
        index (int): position to add to. Typically either -1 or 0.

    Example:
        >>> with PythonPathContext('foo', -1):
        >>>     assert sys.path[-1] == 'foo'
        >>> assert sys.path[-1] != 'foo'
        >>> with PythonPathContext('bar', 0):
        >>>     assert sys.path[0] == 'bar'
        >>> assert sys.path[0] != 'bar'

    Example:
        >>> # xdoctest: +REQUIRES(module:pytest)
        >>> # Mangle the path inside the context
        >>> self = PythonPathContext('foo', 0)
        >>> self.__enter__()
        >>> sys.path.insert(0, 'mangled')
        >>> import pytest
        >>> with pytest.warns(UserWarning):
        >>>     self.__exit__(None, None, None)

    Example:
        >>> # xdoctest: +REQUIRES(module:pytest)
        >>> self = PythonPathContext('foo', 0)
        >>> self.__enter__()
        >>> sys.path.remove('foo')
        >>> import pytest
        >>> with pytest.raises(RuntimeError):
        >>>     self.__exit__(None, None, None)
    """
    def __init__(self, dpath, index=0):
        self.dpath = os.fspath(dpath)
        self.index = index

    def __enter__(self):
        if self.index < 0:
            self.index = len(sys.path) + self.index + 1
        sys.path.insert(self.index, self.dpath)

    def __exit__(self, type, value, trace):
        need_recover = False
        if len(sys.path) <= self.index:  # nocover
            msg_parts = [
                'sys.path changed while in PythonPathContext.',
                'len(sys.path) = {!r} but index is {!r}'.format(
                    len(sys.path), self.index),
            ]
            need_recover = True

        if sys.path[self.index] != self.dpath:  # nocover
            # The path is not where we put it, the path must have been mangled
            msg_parts = [
                'sys.path changed while in PythonPathContext',
                'Expected dpath={!r} at index={!r} in sys.path, but got '
                'dpath={!r}'.format(
                    self.dpath, self.index, sys.path[self.index]
                )
            ]
            need_recover = True

        if need_recover:
            # Try and find where the temporary path went
            try:
                real_index = sys.path.index(self.dpath)
            except ValueError:
                msg_parts.append('Expected dpath was not in sys.path')
                raise RuntimeError('\n'.join(msg_parts))
            else:
                # We were able to recover, but warn the user. This method of
                # recovery is a heuristic and does not work in some cases.
                msg_parts.append((
                    'Expected dpath was at index {}. '
                    'This could indicate conflicting module namespaces.'
                ).format(real_index))
                warnings.warn('\n'.join(msg_parts))
                sys.path.pop(real_index)
        else:
            sys.path.pop(self.index)


def import_module_from_path(modpath, index=-1):
    """
    Imports a module via a filesystem path.

    This works by modifying ``sys.path``, importing the module name, and then
    attempting to undo the change to sys.path. This function may produce
    unexpected results in the case where the imported module itself itself
    modifies ``sys.path`` or if there is another conflicting module with the
    same name.

    Args:
        modpath (str | PathLike):
            Path to the module on disk or within a zipfile. Paths within a
            zipfile can be given by ``<path-to>.zip/<path-inside-zip>.py``.

        index (int):
            Location at which we modify PYTHONPATH if necessary.  If your
            module name does not conflict, the safest value is -1, However, if
            there is a conflict, then use an index of 0.  The default may
            change to 0 in the future.

    Returns:
        ModuleType: the imported module

    References:
        .. [SO_67631] https://stackoverflow.com/questions/67631/import-module-given-path

    Raises:
        IOError - when the path to the module does not exist
        ImportError - when the module is unable to be imported

    Note:
        If the module is part of a package, the package will be imported first.
        These modules may cause problems when reloading via IPython magic

        This can import a module from within a zipfile. To do this modpath
        should specify the path to the zipfile and the path to the module
        within that zipfile separated by a colon or pathsep.
        E.g. "/path/to/archive.zip:mymodule.pl"

    Warning:
        It is best to use this with paths that will not conflict with
        previously existing modules.

        If the modpath conflicts with a previously existing module name. And
        the target module does imports of its own relative to this conflicting
        path. In this case, the module that was loaded first will win.

        For example if you try to import '/foo/bar/pkg/mod.py' from the folder
        structure:

        .. code::

            - foo/
              +- bar/
                 +- pkg/
                    +  __init__.py
                    |- mod.py
                    |- helper.py

       If there exists another module named ``pkg`` already in sys.modules
       and mod.py does something like ``from . import helper``, Python will
       assume helper belongs to the ``pkg`` module already in sys.modules.
       This can cause a NameError or worse --- a incorrect helper module.

    SeeAlso:
        :func:`import_module_from_name`

    Example:
        >>> import xdoctest
        >>> modpath = xdoctest.__file__
        >>> module = import_module_from_path(modpath)
        >>> assert module is xdoctest

    Example:
        >>> # Test importing a module from within a zipfile
        >>> import zipfile
        >>> from xdoctest import utils
        >>> from os.path import join, expanduser, normpath
        >>> dpath = expanduser('~/.cache/xdoctest')
        >>> dpath = utils.ensuredir(dpath)
        >>> #dpath = utils.TempDir().ensure()
        >>> # Write to an external module named bar
        >>> external_modpath = join(dpath, 'bar.py')
        >>> # For pypy support we have to write this using with
        >>> with open(external_modpath, 'w') as file:
        >>>     file.write('testvar = 1')
        >>> internal = 'folder/bar.py'
        >>> # Move the external bar module into a zipfile
        >>> zippath = join(dpath, 'myzip.zip')
        >>> with zipfile.ZipFile(zippath, 'w') as myzip:
        >>>     myzip.write(external_modpath, internal)
        >>> # Import the bar module from within the zipfile
        >>> modpath = zippath + ':' + internal
        >>> modpath = zippath + os.path.sep + internal
        >>> module = import_module_from_path(modpath)
        >>> assert normpath(module.__name__) == normpath('folder/bar')
        >>> assert module.testvar == 1

    Example:
        >>> import pytest
        >>> with pytest.raises(IOError):
        >>>     import_module_from_path('does-not-exist')
        >>> with pytest.raises(IOError):
        >>>     import_module_from_path('does-not-exist.zip/')
    """
    if not os.path.exists(modpath):
        import re
        import zipimport
        # We allow (if not prefer or force) the colon to be a path.sep in order
        # to agree with the mod.__name__ attribute that will be produced
        # TODO: we could codify this by using `util_zip.split_archive`

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
                try:
                    try:
                        module = zimp_file.load_module(modname)
                    except Exception:  # nocover
                        module = zimp_file.load_module(modname.replace('\\', '/'))  # hack
                except Exception as ex:  # nocover
                    text = (
                        'Encountered error in import_module_from_path '
                        'while calling load_module: '
                        'modpath={modpath!r}, '
                        'internal={internal!r}, '
                        'modname={modname!r}, '
                        'archivepath={archivepath!r}, '
                        'ex={ex!r}'
                    ).format(
                        modpath=modpath,
                        internal=internal,
                        modname=modname,
                        archivepath=archivepath,
                        ex=ex)
                    print(text)
                    # raise
                    raise Exception(text)

                return module
        raise IOError('modpath={} does not exist'.format(modpath))
    else:
        # the importlib version does not work in pytest
        module = _custom_import_modpath(modpath, index=index)
        # TODO: use this implementation once pytest fixes importlib
        # module = _importlib_import_modpath(modpath)
        return module


def import_module_from_name(modname):
    """
    Imports a module from its string name (i.e. ``__name__``)

    This is a simple wrapper around :func:`importlib.import_module`, but is
    provided as a companion function to :func:`import_module_from_path`, which
    contains functionality not provided in the Python standard library.

    Args:
        modname (str): module name

    Returns:
        ModuleType: module

    SeeAlso:
        :func:`import_module_from_path`

    Example:
        >>> # test with modules that won't be imported in normal circumstances
        >>> # todo write a test where we guarantee this
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
    else:  # nocover
        # The __import__ statement is weird
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

    Returns:
        List[str]
    """
    import sysconfig
    tags = []
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

    Returns:
        tuple
    """
    import sysconfig
    valid_exts = []
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

        sys_path (None | List[str | PathLike]):
            The paths to search for the module.
            If unspecified, defaults to ``sys.path``.

        exclude (List[str | PathLike] | None):
            If specified prevents these directories from being searched.
            Defaults to None.

    Returns:
        str: path to the module.

    Note:
        This is much slower than the pkgutil mechanisms.

        There seems to be a change to the editable install mechanism:
        https://github.com/pypa/setuptools/issues/3548
        Trying to find more docs about it.

        TODO: add a test where we make an editable install, regular install,
        standalone install, and check that we always find the right path.

    Example:
        >>> print(_syspath_modname_to_modpath('xdoctest.static_analysis'))
        ...static_analysis.py
        >>> print(_syspath_modname_to_modpath('xdoctest'))
        ...xdoctest
        >>> # xdoctest: +REQUIRES(CPython)
        >>> print(_syspath_modname_to_modpath('_ctypes'))
        ..._ctypes...
        >>> assert _syspath_modname_to_modpath('xdoctest', sys_path=[]) is None
        >>> assert _syspath_modname_to_modpath('xdoctest.static_analysis', sys_path=[]) is None
        >>> assert _syspath_modname_to_modpath('_ctypes', sys_path=[]) is None
        >>> assert _syspath_modname_to_modpath('this', sys_path=[]) is None

    Example:
        >>> # test what happens when the module is not visible in the path
        >>> from ubelt.util_import import *  # NOQA
        >>> from ubelt.util_import import _syspath_modname_to_modpath
        >>> modname = 'xdoctest.static_analysis'
        >>> modpath = _syspath_modname_to_modpath(modname)
        >>> exclude = [split_modpath(modpath)[0]]
        >>> found = _syspath_modname_to_modpath(modname, exclude=exclude)
        >>> if found is not None:
        >>>     # Note: the basic form of this test may fail if there are
        >>>     # multiple versions of the package installed. Try and fix that.
        >>>     other = split_modpath(found)[0]
        >>>     assert other not in exclude
        >>>     exclude.append(other)
        >>>     found = _syspath_modname_to_modpath(modname, exclude=exclude)
        >>> if found is not None:
        >>>     raise AssertionError(
        >>>         'should not have found {}.'.format(found) +
        >>>         ' because we excluded: {}.'.format(exclude) +
        >>>         ' cwd={} '.format(os.getcwd()) +
        >>>         ' sys.path={} '.format(sys.path)
        >>>     )
    """
    import glob

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

    def check_dpath(dpath):
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

    _pkg_name = _fname_we.split(os.path.sep)[0]
    _pkg_name_hypen = _pkg_name.replace('_', '-')

    _egglink_fname1 = _pkg_name + '.egg-link'
    _egglink_fname2 = _pkg_name_hypen + '.egg-link'
    # FIXME! suffixed modules will clobber break!
    # Currently mitigating this by looping over all possible matches,
    # but it would be nice to ensure we are not matching suffixes.
    # however, we should probably match and handle different versions.
    _editable_fname_pth_pat = '__editable__.' + _pkg_name + '-*.pth'
    _editable_fname_finder_py_pat = '__editable___' + _pkg_name + '_*finder.py'

    found_modpath = None
    for dpath in candidate_dpaths:
        modpath = check_dpath(dpath)
        if modpath:
            found_modpath = modpath
            break

        # Attempt to handle PEP660 import hooks.
        # We should look for a finder path first, because a pth might
        # not contain a real path, but code to load the finder.
        # Which one is used is defined in setuptools/editable_wheel.py
        # It will depend on an "Editable Strategy".
        # Basically a finder will be used for "complex" structures and
        # basic pth will be used for "simple" structures (which means has a
        # src/modname folder).
        new_editable_finder_paths = sorted(glob.glob(join(dpath, _editable_fname_finder_py_pat)))
        if new_editable_finder_paths:  # nocover
            # This makes some assumptions, which may not hold in general
            # We may need to fallback entirely on pkgutil, which would
            # ultimately be good. Hopefully the new standards mean it does not
            # break with pytest anymore? Nope, pytest still doesn't work right
            # with it.
            for finder_fpath in new_editable_finder_paths:
                mapping = _static_parse('MAPPING', finder_fpath)
                try:
                    target = dirname(mapping[_pkg_name])
                except KeyError:
                    ...
                else:
                    if not exclude or normalize(target) not in real_exclude:  # pragma: nobranch
                        modpath = check_dpath(target)
                        if modpath:  # pragma: nobranch
                            found_modpath = modpath
                            break
            if found_modpath is not None:
                break

        # If a finder does not exist, then the __editable__ pth file might hold
        # the path itself. Check for that.
        new_editable_pth_paths = sorted(glob.glob(join(dpath, _editable_fname_pth_pat)))
        if new_editable_pth_paths:  # nocover
            # Disable coverage because the test that covers this is too slow.
            # It can be made faster, re-enable when that lands.
            import pathlib
            for editable_pth in new_editable_pth_paths:
                editable_pth = pathlib.Path(editable_pth)
                target = editable_pth.read_text().strip().split('\n')[-1]
                if not exclude or normalize(target) not in real_exclude:
                    modpath = check_dpath(target)
                    if modpath:  # pragma: nobranch
                        found_modpath = modpath
                        break
            if found_modpath is not None:
                break

        # If file path checks fails, check for egg-link based modules
        # (Python usually puts egg links into sys.path, but if the user is
        #  providing the path then it is important to check them explicitly)
        linkpath1 = join(dpath, _egglink_fname1)
        linkpath2 = join(dpath, _egglink_fname2)
        linkpath = None
        if isfile(linkpath1):  # nocover
            linkpath = linkpath1
        elif isfile(linkpath2):  # nocover
            linkpath = linkpath2
        if linkpath is not None:  # nocover
            # We exclude this from coverage because its difficult to write a
            # unit test where we can enforce that there is a module installed
            # in development mode.
            # Note: the new test_editable_modules.py test can do this, but
            # this old method may no longer be supported.

            # TODO: ensure this is the correct way to parse egg-link files
            # https://setuptools.readthedocs.io/en/latest/formats.html#egg-links
            # The docs state there should only be one line, but I see two.
            with open(linkpath, 'r') as file:
                target = file.readline().strip()
            if not exclude or normalize(target) not in real_exclude:
                modpath = check_dpath(target)
                if modpath:
                    found_modpath = modpath
                    break

    return found_modpath


def _custom_import_modpath(modpath, index=-1):
    dpath, rel_modpath = split_modpath(modpath)
    modname = modpath_to_modname(modpath)
    try:
        with PythonPathContext(dpath, index=index):
            module = import_module_from_name(modname)
    except Exception as ex:  # nocover
        msg_parts = [
            'ERROR: Failed to import modname={} with modpath={}'.format(
                modname, modpath)
        ]
        msg_parts.append('Caused by: {}'.format(repr(ex)))
        raise RuntimeError('\n'.join(msg_parts))
    return module


def _importlib_import_modpath(modpath):  # nocover
    """
    Alternative to import_module_from_path using importlib mechainsms

    Args:
        modname (str): the module name.
    """
    dpath, rel_modpath = split_modpath(modpath)
    modname = modpath_to_modname(modpath)
    import importlib.util
    spec = importlib.util.spec_from_file_location(modname, modpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pkgutil_modname_to_modpath(modname):  # nocover
    """
    faster version of :func:`_syspath_modname_to_modpath` using builtin python
    mechanisms, but unfortunately it doesn't play nice with pytest.

    Args:
        modname (str): the module name.

    Example:
        >>> # xdoctest: +SKIP
        >>> modname = 'xdoctest.static_analysis'
        >>> _pkgutil_modname_to_modpath(modname)
        ...static_analysis.py
        >>> # xdoctest: +REQUIRES(CPython)
        >>> _pkgutil_modname_to_modpath('_ctypes')
        ..._ctypes...

    Ignore:
        >>> _pkgutil_modname_to_modpath('cv2')
    """
    import pkgutil
    loader = pkgutil.find_loader(modname)
    if loader is None:
        raise Exception('No module named {} in the PYTHONPATH'.format(modname))
    modpath = loader.get_filename().replace('.pyc', '.py')
    return modpath


def modname_to_modpath(modname, hide_init=True, hide_main=False, sys_path=None):
    """
    Finds the path to a python module from its name.

    Determines the path to a python module without directly import it

    Converts the name of a module (__name__) to the path (__file__) where it is
    located without importing the module. Returns None if the module does not
    exist.

    Args:
        modname (str):
            The name of a module in ``sys_path``.

        hide_init (bool):
            if False, __init__.py will be returned for packages.
            Defaults to True.

        hide_main (bool):
            if False, and ``hide_init`` is True, __main__.py will be returned
            for packages, if it exists. Defautls to False.

        sys_path (None | List[str | PathLike]):
            The paths to search for the module.
            If unspecified, defaults to ``sys.path``.

    Returns:
        str | None:
            modpath - path to the module, or None if it doesn't exist

    Example:
        >>> modname = 'xdoctest.__main__'
        >>> modpath = modname_to_modpath(modname, hide_main=False)
        >>> assert modpath.endswith('__main__.py')
        >>> modname = 'xdoctest'
        >>> modpath = modname_to_modpath(modname, hide_init=False)
        >>> assert modpath.endswith('__init__.py')
        >>> # xdoctest: +REQUIRES(CPython)
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

    Args:
        modpath (str | PathLike):
            path to a module

        hide_init (bool):
            if True, always return package modules as __init__.py files
            otherwise always return the dpath. Defaults to True.

        hide_main (bool):
            if True, always strip away main files otherwise ignore __main__.py.
            Defaults to False.

    Returns:
        str | PathLike: a normalized path to the module

    Note:
        Adds __init__ if reasonable, but only removes __main__ by default

    Example:
        >>> from xdoctest import static_analysis as module
        >>> modpath = module.__file__
        >>> assert normalize_modpath(modpath) == modpath.replace('.pyc', '.py')
        >>> dpath = dirname(modpath)
        >>> res0 = normalize_modpath(dpath, hide_init=0, hide_main=0)
        >>> res1 = normalize_modpath(dpath, hide_init=0, hide_main=1)
        >>> res2 = normalize_modpath(dpath, hide_init=1, hide_main=0)
        >>> res3 = normalize_modpath(dpath, hide_init=1, hide_main=1)
        >>> assert res0.endswith('__init__.py')
        >>> assert res1.endswith('__init__.py')
        >>> assert not res2.endswith('.py')
        >>> assert not res3.endswith('.py')
    """
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
        hide_init (bool, default=True): removes the __init__ suffix
        hide_main (bool, default=False): removes the __main__ suffix
        check (bool, default=True): if False, does not raise an error if
            modpath is a dir and does not contain an __init__ file.
        relativeto (str, default=None): if specified, all checks are ignored
            and this is considered the path to the root module.

    TODO:
        - [ ] Does this need modification to support PEP 420?
              https://www.python.org/dev/peps/pep-0420/

    Returns:
        str: modname

    Raises:
        ValueError: if check is True and the path does not exist

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
        >>> # xdoctest: +REQUIRES(CPython)
        >>> modpath = modname_to_modpath('_ctypes')
        >>> modname = modpath_to_modname(modpath)
        >>> assert modname == '_ctypes'

    Example:
        >>> modpath = '/foo/libfoobar.linux-x86_64-3.6.so'
        >>> modname = modpath_to_modname(modpath, check=False)
        >>> assert modname == 'libfoobar'
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
        modname, abi_tag = modname.split('.', 1)
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
            directory and does not contain an ``__init__.py`` file.

    Returns:
        Tuple[str, str]: (directory, rel_modpath)

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


def is_modname_importable(modname, sys_path=None, exclude=None):
    """
    Determines if a modname is importable based on your current sys.path

    Args:
        modname (str): name of module to check
        sys_path (list, default=None): if specified overrides ``sys.path``
        exclude (list): list of directory paths. if specified prevents these
            directories from being searched.

    Returns:
        bool: True if the module can be imported

    Example:
        >>> is_modname_importable('xdoctest')
        True
        >>> is_modname_importable('not_a_real_module')
        False
        >>> is_modname_importable('xdoctest', sys_path=[])
        False
    """
    modpath = _syspath_modname_to_modpath(modname, sys_path=sys_path,
                                          exclude=exclude)
    flag = bool(modpath is not None)
    return flag


def _static_parse(varname, fpath):
    """
    Statically parse the a constant variable from a python file

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('tests/import/staticparse').ensuredir()
        >>> fpath = (dpath / 'foo.py')
        >>> fpath.write_text('a = {1: 2}')
        >>> assert _static_parse('a', fpath) == {1: 2}
        >>> fpath.write_text('a = 2')
        >>> assert _static_parse('a', fpath) == 2
        >>> fpath.write_text('a = "3"')
        >>> assert _static_parse('a', fpath) == "3"
        >>> fpath.write_text('a = ["3", 5, 6]')
        >>> assert _static_parse('a', fpath) == ["3", 5, 6]
        >>> fpath.write_text('a = ("3", 5, 6)')
        >>> assert _static_parse('a', fpath) == ("3", 5, 6)
        >>> fpath.write_text('b = 10' + chr(10) + 'a = None')
        >>> assert _static_parse('a', fpath) is None
        >>> import pytest
        >>> with pytest.raises(TypeError):
        >>>     fpath.write_text('a = list(range(10))')
        >>>     assert _static_parse('a', fpath) is None
        >>> with pytest.raises(AttributeError):
        >>>     fpath.write_text('a = list(range(10))')
        >>>     assert _static_parse('c', fpath) is None
    """
    import ast

    if not exists(fpath):
        raise ValueError('fpath={!r} does not exist'.format(fpath))
    with open(fpath, 'r') as file_:
        sourcecode = file_.read()
    pt = ast.parse(sourcecode)

    class StaticVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if getattr(target, 'id', None) == varname:
                    self.static_value = _parse_static_node_value(node.value)

    visitor = StaticVisitor()
    visitor.visit(pt)
    try:
        value = visitor.static_value
    except AttributeError:
        value = 'Unknown {}'.format(varname)
        raise AttributeError(value)
    return value


def _parse_static_node_value(node):
    """
    Extract a constant value from a node if possible
    """
    import ast
    from collections import OrderedDict
    # TODO: ast.Constant for 3.8
    if isinstance(node, ast.Num):
        value = node.n
    elif isinstance(node, ast.Str):
        value = node.s
    elif isinstance(node, ast.List):
        value = list(map(_parse_static_node_value, node.elts))
    elif isinstance(node, ast.Tuple):
        value = tuple(map(_parse_static_node_value, node.elts))
    elif isinstance(node, (ast.Dict)):
        keys = map(_parse_static_node_value, node.keys)
        values = map(_parse_static_node_value, node.values)
        value = OrderedDict(zip(keys, values))
        # value = dict(zip(keys, values))
    elif isinstance(node, (ast.NameConstant)):
        value = node.value
    else:
        print(node.__dict__)
        raise TypeError('Cannot parse a static value from non-static node '
                        'of type: {!r}'.format(type(node)))
    return value
