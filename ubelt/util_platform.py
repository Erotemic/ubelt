# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import exists
from os.path import expanduser
from os.path import join
from os.path import normpath
import os
import sys
import pipes
import six
import warnings
from ubelt import util_path
from ubelt import util_io

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')
POSIX = 'posix' in sys.builtin_module_names


def platform_resource_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.

    Returns:
        str : path to the resource dir used by the current operating system
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Roaming'
    elif LINUX:  # nocover
        dpath_ = '~/.config'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Application Support'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def platform_cache_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for temporary deletable data.

    Returns:
        str : path to the cache dir used by the current operating system
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Local'
    elif LINUX:  # nocover
        dpath_ = '~/.cache'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Caches'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def get_app_resource_dir(appname, *args):
    r"""
    Returns a writable directory for an application
    This should be used for persistent configuration files.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable resource directory for this application

    SeeAlso:
        ensure_app_resource_dir
    """
    dpath = join(platform_resource_dir(), appname, *args)
    return dpath


def ensure_app_resource_dir(appname, *args):
    """
    Calls `get_app_resource_dir` but ensures the directory exists.

    SeeAlso:
        get_app_resource_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_resource_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def get_app_cache_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory for this application

    SeeAlso:
        ensure_app_cache_dir
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Calls `get_app_cache_dir` but ensures the directory exists.

    SeeAlso:
        get_app_cache_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_cache_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def startfile(fpath, verbose=True):  # nocover
    """
    Uses default program defined by the system to open a file.

    Args:
        fpath (str): a file to open using the program associated with the
            files extension type.
        verbose (int): verbosity

    References:
        http://stackoverflow.com/questions/2692873/quote-posix

    DisableExample:
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> base = ub.ensure_app_cache_dir('ubelt')
        >>> fpath1 = join(base, 'test_open.txt')
        >>> ub.touch(fpath1)
        >>> proc = ub.startfile(fpath1)
    """
    import ubelt as ub
    if verbose:
        print('[ubelt] startfile("{}")'.format(fpath))
    fpath = normpath(fpath)
    if not exists(fpath):
        raise Exception('Cannot start nonexistant file: %r' % fpath)
    if not WIN32:
        fpath = pipes.quote(fpath)
    if LINUX:
        info = ub.cmd(('xdg-open', fpath), detatch=True, verbose=verbose)
    elif DARWIN:
        info = ub.cmd(('open', fpath), detatch=True, verbose=verbose)
    elif WIN32:
        os.startfile(fpath)
        info = None
    else:
        raise RuntimeError('Unknown Platform')
    if info is not None:
        if not info['proc']:
            raise Exception('startfile failed')


def editfile(fpath, verbose=True):  # nocover
    """
    Opens a file or python module in your preferred visual editor.

    Your preferred visual editor is gvim... unless you specify one using the
    VISUAL environment variable. This function is extremely useful in an
    IPython development environment.

    Args:
        fpath (str): a file path or python module / function
        verbose (int): verbosity

    DisableExample:
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> ub.editfile(ub.util_platform.__file__)
        >>> ub.editfile(ub)
        >>> ub.editfile(ub.editfile)
    """
    from six import types
    import ubelt as ub
    if not isinstance(fpath, six.string_types):
        if isinstance(fpath, types.ModuleType):
            fpath = fpath.__file__
        else:
            fpath =  sys.modules[fpath.__module__].__file__
        fpath_py = fpath.replace('.pyc', '.py')
        if exists(fpath_py):
            fpath = fpath_py

    if verbose:
        print('[ubelt] editfile("{}")'.format(fpath))

    editor = os.environ.get('VISUAL', 'gvim')

    if not exists(fpath):
        raise IOError('Cannot start nonexistant file: %r' % fpath)
    ub.cmd([editor, fpath], fpath, detatch=True)


def symlink(real_path, link_path, overwrite=False, on_error='raise',
            verbose=0):
    """
    Attempt to create a symbolic link.

    Args:
        path (str): path to real file or directory
        link_path (str): path to desired location for symlink
        overwrite (bool): overwrite existing symlinks.
            This will not overwrite real files.  (default = False)
        on_error (str): strategy for dealing with errors.
            raise or ignore
        verbose (int):  verbosity level (default=0)

    Returns:
        str: link path

    CommandLine:
        python -m ubelt.util_platform symlink

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.get_app_resource_dir('ubelt')
        >>> real_path = join(dpath, 'real_file.txt')
        >>> link_path = join(dpath, 'link_file.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_path, link_path)
        >>> assert ub.readfrom(result) == 'foo'
        >>> [ub.delete(p) for p in [real_path, link_path]]

    Example:
        >>> import ubelt as ub
        >>> real_dpath = ub.get_app_resource_dir('ubelt', 'real_dpath')
        >>> link_dpath = ub.augpath(real_dpath, base='link_dpath')
        >>> real_path = join(real_dpath, 'afile.txt')
        >>> link_path = join(link_dpath, 'afile.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.ensuredir(real_dpath)
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_dpath, link_dpath)
        >>> assert ub.readfrom(link_path) == 'foo', 'read should be same'
        >>> ub.writeto(link_path, 'bar')
        >>> assert ub.readfrom(link_path) == 'bar'
        >>> assert ub.readfrom(real_path) == 'bar', 'changing link did not change real'
        >>> ub.writeto(real_path, 'baz')
        >>> assert ub.readfrom(real_path) == 'bar'
        >>> assert ub.readfrom(link_path) == 'baz', 'changing real did not change link'
        >>> ub.delete(link_dpath, verbose=0)
        >>> assert not exists(link_dpath), 'link should not exist'
        >>> assert exists(real_path), 'real path should exist'
        >>> ub.delete(real_dpath, verbose=0)
        >>> assert not exists(real_path)

    TODO:
        Can this be fixed on windows?
        The main issue is that you need admin rights on Windows to symlink.
    """
    path = normpath(real_path)
    link = normpath(link_path)
    if verbose:
        print('Creating symlink: path={} link={}'.format(path, link))
    if os.path.islink(link):
        if verbose:
            print('symlink already exists')
        os_readlink = getattr(os, "readlink", None)
        if callable(os_readlink):
            if os_readlink(link) == path:
                if verbose > 1:
                    print('[path] ... and points to the right place')
                return link
        else:
            warnings.warn('Warning, symlinks are not implemented')
        if verbose > 1:
            print('... but it points somewhere else')
        if overwrite:
            util_io.delete(link, verbose > 1)
        elif on_error == 'ignore':
            return False
    try:
        if sys.platform.startswith('win32'):
            _symlink_win32(path, link)
        else:
            os_symlink = getattr(os, "symlink", None)
            if os_symlink is None:
                raise NotImplementedError('')
            os_symlink(path, link)
    except Exception as ex:
        do_raise = (on_error == 'raise')
        if do_raise:
            raise
    return link


def _symlink_win32(path, link):  # nocover
    """
    https://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
    """
    import os
    if False:
        from ubelt import util_cmd
        if os.path.isdir(path):
            info = util_cmd.cmd('mklink /D {} {}'.format(link, path), shell=True)
        else:
            info = util_cmd.cmd('mklink {} {}'.format(link, path), shell=True)
        if info['ret'] != 0:
            raise Exception(str(info))
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(path) else 0
        if csl(link, path, flags) == 0:
            raise ctypes.WinError('cannot create win32 symlink')


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
        pytest ubelt/util_platform.py
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
