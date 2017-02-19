# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import normpath, expanduser, join, exists
import os
import sys

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')


def get_resource_dir():
    """
    Returns a directory which should be writable for any application
    """
    #resource_prefix = '~'
    if WIN32:
        dpath_ = '~/AppData/Roaming'
    elif LINUX:
        dpath_ = '~/.config'
    elif DARWIN:
        dpath_  = '~/Library/Application Support'
    else:
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def get_app_resource_dir(appname, *args):
    r"""
    Returns a writable directory for an application

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory
    """
    dpath = join(get_resource_dir(), appname, *args)
    return dpath


def ensure_app_resource_dir(appname, *args):
    dpath = get_app_resource_dir(appname, *args)
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
    """
    if verbose is None:
        verbose = 0
    if isinstance(dpath, (list, tuple)):
        dpath = join(*dpath)
    if not exists(dpath):
        if verbose:
            print('[util_path] mkdir(%r)' % dpath)
        try:
            os.makedirs(normpath(dpath), mode=mode)
        except OSError as ex:
            print('Error in ensuredir')
            raise
    return dpath

