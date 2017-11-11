# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
from os.path import (splitext, split, join, expanduser, expandvars, realpath,
                     abspath, normpath, dirname, exists)


def augpath(path, suffix='', prefix=''):
    """
    Augments a filename with a suffix and/or a prefix while maintaining the
    extension.

    Args:
        path (str): string representation of a path
        suffix (str): augment filename before extension

    Returns:
        str: newpath

    Example:
        >>> import ubelt as ub
        >>> path = 'foo.bar'
        >>> suffix = '_suff'
        >>> prefix = 'pref_'
        >>> newpath = ub.augpath(path, suffix, prefix)
        >>> print('newpath = %s' % (newpath,))
        newpath = pref_foo_suff.bar
    """
    # Breakup path
    dpath, fname = split(path)
    fname_noext, orig_ext = splitext(fname)
    # Augment and recombine into new path
    new_fname = ''.join((prefix, fname_noext, suffix, orig_ext))
    newpath = join(dpath, new_fname)
    return newpath


# def username():
#     """
#     Returns the current user's name

#     Returns:
#         str: name: current users name

#     Example:
#         >>> from ubelt.util_platform import *
#         >>> assert userhome() == expanduser('~')
#     """
#     # if 'USER' in os.environ:
#     #     name = os.environ['USER']
#     # else:
#     import pwd
#     name = pwd.getpwuid(os.getuid()).pw_name
#     import getpass
#     getpass.getuser()
#     return name


def userhome(username=None):
    """
    Returns the user's home directory.
    If `username` is None, this is the directory for the current user.

    Args:
        username (str): name of a user on the system

    Returns:
        str: userhome_dpath: path to the home directory

    Example:
        >>> import getpass
        >>> username = getpass.getuser()
        >>> assert userhome() == expanduser('~')
        >>> assert userhome(username) == expanduser('~')
    """
    if username is None:
        # get home directory for the current user
        if 'HOME' in os.environ:
            userhome_dpath = os.environ['HOME']
        else:  # nocover
            if sys.platform.startswith('win32'):
                # win32 fallback when HOME is not defined
                if 'USERPROFILE' in os.environ:
                    userhome_dpath = os.environ['USERPROFILE']
                elif 'HOMEPATH' in os.environ:
                    drive = os.environ.get('HOMEDRIVE', '')
                    userhome_dpath = join(drive, os.environ['HOMEPATH'])
                else:
                    raise OSError("Cannot determine the user's home directory")
            else:
                # posix fallback when HOME is not defined
                import pwd
                userhome_dpath = pwd.getpwuid(os.getuid()).pw_dir
    else:
        # A specific user directory was requested
        if sys.platform.startswith('win32'):  # nocover
            # get the directory name for the current user
            c_users = dirname(userhome())
            userhome_dpath = join(c_users, username)
            if not exists(userhome_dpath):
                raise KeyError('Unknown user: {}'.format(username))
        else:
            import pwd
            try:
                pwent = pwd.getpwnam(username)
            except KeyError:  # nocover
                raise KeyError('Unknown user: {}'.format(username))
            userhome_dpath = pwent.pw_dir
    return userhome_dpath


def compressuser(path):
    """
    Inverse of `os.path.expanduser`

    Args:
        path (str): path in system file structure

    Returns:
        str: path: shortened path replacing the home directory with a tilde

    Example:
        >>> path = expanduser('~')
        >>> assert path != '~'
        >>> assert compressuser(path) == '~'
        >>> assert compressuser(path + '1') == path + '1'
        >>> assert compressuser(path + '/1') == join('~', '1')
    """
    path = normpath(path)
    userhome_dpath = userhome()
    if path.startswith(userhome_dpath):
        if len(path) == len(userhome_dpath):
            path = '~'
        elif path[len(userhome_dpath)] == os.path.sep:
            path = '~' + path[len(userhome_dpath):]
    return path


def truepath(path, real=False):
    """
    Normalizes a string representation of a path and does shell-like expansion.

    Args:
        path (str): string representation of a path
        real (bool): if True, all symbolic links are followed. (default: False)

    Returns:
        str : normalized path

    Note:
        This function is simlar to the composition of expanduser, expandvars,
        normpath, and (realpath if `real` else abspath). However, on windows
        backslashes are then replaced with forward slashes to offer a
        consistent unix-like experience across platforms.

        On windows expanduser will expand environment variables formatted as
        %name%, whereas on unix, this will not occur.

    Example:
        >>> import ubelt as ub
        >>> assert ub.truepath('~/foo') == ub.truepath('$HOME/foo')
        >>> assert ub.truepath('~/foo') == ub.truepath('~/foo/bar/..')
        >>> assert ub.truepath('~/foo', real=True) == ub.truepath('~/foo')
    """
    path = expanduser(path)
    path = expandvars(path)
    if real:
        path = realpath(path)
    else:
        path = abspath(path)
    path = normpath(path)
    return path


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_path
        python -m ubelt.util_path all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
