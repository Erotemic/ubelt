# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import exists
from os.path import expanduser
from os.path import join
from os.path import normpath
from os.path import islink
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

if WIN32:
    from ubelt import _win32_links


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


def symlink(real_path, link_path, overwrite=False, verbose=0):
    """
    Create a symbolic link.

    Args:
        path (str): path to real file or directory
        link_path (str): path to desired location for symlink
        overwrite (bool): overwrite existing symlinks.
            This will not overwrite real files on systems with proper symlinks.
            However, on older versions of windows junctions are
            indistinguishable from real files, so we cannot make this
            guarantee.  (default = False)
        verbose (int):  verbosity level (default=0)

    Notes:
        There seems to be a corner case on Python2 and some versions of Windows
        (whatever appveyor is using). However, my windows box works so idk.

    Returns:
        str: link path

    CommandLine:
        python -m ubelt.util_platform symlink:0

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'test_symlink0')
        >>> real_path = join(dpath, 'real_file.txt')
        >>> link_path = join(dpath, 'link_file.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_path, link_path)
        >>> assert ub.readfrom(result) == 'foo'
        >>> [ub.delete(p) for p in [real_path, link_path]]

    Example:
        >>> import ubelt as ub
        >>> from os.path import dirname
        >>> test_links = ub.import_module_from_path(dirname(__file__) + '/tests/test_links.py')
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'test_symlink1')
        >>> ub.delete(dpath)
        >>> ub.ensuredir(dpath)
        >>> test_links.dirstats(dpath)
        >>> real_dpath = ub.ensuredir((dpath, 'real_dpath'))
        >>> link_dpath = ub.augpath(real_dpath, base='link_dpath')
        >>> real_path = join(dpath, 'afile.txt')
        >>> link_path = join(dpath, 'afile.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_dpath, link_dpath)
        >>> assert ub.readfrom(link_path) == 'foo', 'read should be same'
        >>> ub.writeto(link_path, 'bar')
        >>> test_links.dirstats(dpath)
        >>> assert ub.readfrom(link_path) == 'bar', 'very bad bar'
        >>> assert ub.readfrom(real_path) == 'bar', 'changing link did not change real'
        >>> ub.writeto(real_path, 'baz')
        >>> test_links.dirstats(dpath)
        >>> assert ub.readfrom(real_path) == 'baz', 'very bad baz'
        >>> assert ub.readfrom(link_path) == 'baz', 'changing real did not change link'
        >>> ub.delete(link_dpath, verbose=1)
        >>> test_links.dirstats(dpath)
        >>> assert not exists(link_dpath), 'link should not exist'
        >>> assert exists(real_path), 'real path should exist'
        >>> test_links.dirstats(dpath)
        >>> ub.delete(dpath, verbose=1)
        >>> test_links.dirstats(dpath)
        >>> assert not exists(real_path)

    TODO:
        Can this be fixed on windows?
        The main issue is that you need admin rights on Windows to symlink.
    """
    path = normpath(real_path)
    link = normpath(link_path)
    if verbose:
        print('Creating symlink: path={} link={}'.format(path, link))
    if islink(link):
        if verbose:
            print('symlink already exists')
        if _readlink(link) == path:
            if verbose > 1:
                print('... and points to the right place')
            return link
        if verbose > 1:
            if not exists(link):
                print('... but it is broken and points somewhere else')
            else:
                print('... but it points somewhere else')
        if overwrite:
            util_io.delete(link, verbose > 1)

    if WIN32:  # nocover
        if exists(link) and not islink(link):
            # On windows a broken link might still exist as a hard link or a
            # junction. Overwrite it if it is a file and we cannot symlink.
            # However, if it is a non-junction directory then do not overwrite
            if verbose:
                print('link location already exists')
            is_junc = _win32_links._win32_is_junction(link)
            # NOTE:
            # in python2 broken junctions are directories and exist
            # in python3 broken junctions are directories and do not exist
            if os.path.isdir(link):
                if is_junc:
                    pointed = _win32_links._win32_read_junction(link)
                    if path == pointed:
                        if verbose:
                            print('...and is a junction that points to the same place')
                        return link
                    else:
                        if verbose:
                            if not exists(pointed):
                                print('...and is a broken junction that points somewhere else')
                            else:
                                print('...and is a junction that points somewhere else')
                else:
                    if verbose:
                        print('...and is an existing real directory!')
                    raise IOError('Cannot overwrite a real directory')

            elif os.path.isfile(link):
                if _win32_links._win32_is_hardlinked(link, path):
                    if verbose:
                        print('...and is a hard link that points to the same place')
                    return link
                else:
                    if verbose:
                        print('...and is a hard link that points somewhere else')
                    if _can_symlink():
                        raise IOError('Cannot overwrite potentially real file if we can symlink')
            if overwrite:
                if verbose:
                    print('...overwriting')
                util_io.delete(link, verbose > 1)
            else:
                if exists(link):
                    raise IOError('Link already exists')

        _win32_links._win32_symlink2(path, link, verbose=verbose)
    else:
        os.symlink(path, link)
    return link


def _readlink(link):
    try:
        return os.readlink(link)
    except Exception:  # nocover
        # On modern operating systems, we should never get here. (I think)
        warnings.warn('Reading symlinks seems to not be supported')
        raise


def _can_symlink(verbose=0):  # nocover
    """
    Return true if we have permission to create real symlinks.
    This check always returns True on non-win32 systems.  If this check returns
    false, then we still may be able to use junctions.

    CommandLine:
        python -m ubelt.util_platform _can_symlink

    Example:
        >>> # Script
        >>> print(_can_symlink(verbose=1))
    """
    if WIN32:
        return _win32_links._win32_can_symlink(verbose)
    else:
        return True


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
        pytest ubelt/util_platform.py
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
