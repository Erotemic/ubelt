# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import normpath, expanduser, join, exists
import os
import sys

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')


def platform_resource_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.
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
        str: dpath: writable cache directory
    """
    dpath = join(platform_resource_dir(), appname, *args)
    return dpath


def ensure_app_resource_dir(appname, *args):
    """
    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_resource_dir(appname, *args)
    ensuredir(dpath)
    return dpath


def get_app_cache_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_cache_dir(appname, *args)
    ensuredir(dpath)
    return dpath


def ensuredir(dpath, mode=0o1777, verbose=None):
    r"""
    Ensures that directory will exist. creates new dir with sticky bits by
    default

    Args:
        dpath (str): dir to ensure. Can also be a tuple to send to join
        mode (int): octal mode of directory (default 0o1777)
        verbose (int): verbosity (default 0)

    Returns:
        str: path - the ensured directory

    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> cache_dpath = ub.ensure_app_cache_dir('ubelt')
        >>> dpath = join(cache_dpath, 'ensuredir')
        >>> if exists(dpath):
        >>>     os.rmdir(dpath)
        >>> assert not exists(dpath)
        >>> ub.ensuredir(dpath)
        >>> assert exists(dpath)
        >>> os.rmdir(dpath)
    """
    if verbose is None:  # nocover
        verbose = 0
    if isinstance(dpath, (list, tuple)):  # nocover
        dpath = join(*dpath)
    if not exists(dpath):
        if verbose:  # nocover
            print('[ubelt] mkdir(%r)' % dpath)
        try:
            os.makedirs(normpath(dpath), mode=mode)
        except OSError as ex:  # nocover
            print('Error in ensuredir')
            raise
    return dpath


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
