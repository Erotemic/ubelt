# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import expandvars
from os.path import join
from os.path import normpath
from os.path import realpath
from os.path import split
from os.path import splitext
import os
import sys
import shutil

__all__ = [
    'TempDir', 'augpath', 'compressuser', 'truepath', 'userhome',
    'ensuredir',
]


def augpath(path, suffix='', prefix='', ext=None, base=None):
    """
    Augments a path with a new basename, extension, prefix and/or suffix.

    A prefix is inserted before the basename. A suffix is inserted
    between the basename and the extension. The basename and extension can be
    replaced with a new one.

    Args:
        path (str): string representation of a path
        suffix (str): placed in front of the basename
        prefix (str): placed between the basename and trailing extension
        ext (str): if specified, replaces the trailing extension
        base (str): if specified, replaces the basename (without extension)

    Returns:
        str: newpath

    CommandLine:
        python -m ubelt.util_path augpath

    Example:
        >>> import ubelt as ub
        >>> path = 'foo.bar'
        >>> suffix = '_suff'
        >>> prefix = 'pref_'
        >>> ext = '.baz'
        >>> newpath = ub.augpath(path, suffix, prefix, ext=ext, base='bar')
        >>> print('newpath = %s' % (newpath,))
        newpath = pref_bar_suff.baz

    Example:
        >>> augpath('foo.bar')
        'foo.bar'
        >>> augpath('foo.bar', ext='.BAZ')
        'foo.BAZ'
        >>> augpath('foo.bar', suffix='_')
        'foo_.bar'
        >>> augpath('foo.bar', prefix='_')
        '_foo.bar'
        >>> augpath('foo.bar', base='baz')
        'baz.bar'
    """
    # Breakup path
    dpath, fname = split(path)
    fname_noext, orig_ext = splitext(fname)
    ext = orig_ext if ext is None else ext
    fname_noext = fname_noext if base is None else base
    # Augment and recombine into new path
    new_fname = ''.join((prefix, fname_noext, suffix, ext))
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


def compressuser(path, home='~'):
    """
    Inverse of `os.path.expanduser`

    Args:
        path (str): path in system file structure
        home (str): symbol used to replace the home path. Defaults to '~', but
            you might want to use '$HOME' or '%USERPROFILE%' instead.

    Returns:
        str: path: shortened path replacing the home directory with a tilde

    Example:
        >>> path = expanduser('~')
        >>> assert path != '~'
        >>> assert compressuser(path) == '~'
        >>> assert compressuser(path + '1') == path + '1'
        >>> assert compressuser(path + '/1') == join('~', '1')
        >>> assert compressuser(path + '/1', '$HOME') == join('$HOME', '1')
    """
    path = normpath(path)
    userhome_dpath = userhome()
    if path.startswith(userhome_dpath):
        if len(path) == len(userhome_dpath):
            path = home
        elif path[len(userhome_dpath)] == os.path.sep:
            path = home + path[len(userhome_dpath):]
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

    CommandLine:
        python -m ubelt.util_path truepath

    Example:
        >>> import ubelt as ub
        >>> assert ub.truepath('~/foo') == join(ub.userhome(), 'foo')
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


def ensuredir(dpath, mode=0o1777, verbose=None):
    r"""
    Ensures that directory will exist. creates new dir with sticky bits by
    default

    Args:
        dpath (str): dir to ensure. Can also be a tuple to send to join
        mode (int): octal mode of directory (default 0o1777)
        verbose (int): verbosity (default 0)

    Returns:
        str: path: the ensured directory

    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> cache_dpath = ub.ensure_app_cache_dir('ubelt')
        >>> dpath = join(cache_dpath, 'ensuredir')
        >>> if exists(dpath):
        ...     os.rmdir(dpath)
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
            print('Ensuring new directory (%r)' % dpath)
        try:
            os.makedirs(normpath(dpath), mode=mode)
        except OSError:  # nocover
            raise
    else:
        if verbose:  # nocover
            print('Ensuring existing directory (%r)' % dpath)
    return dpath


class TempDir(object):
    """
    Context for creating and cleaning up temporary directories.

    Example:
        >>> with TempDir() as self:
        >>>     dpath = self.dpath
        >>>     assert exists(dpath)
        >>> assert not exists(dpath)

    Example:
        >>> self = TempDir()
        >>> dpath = self.ensure()
        >>> assert exists(dpath)
        >>> self.cleanup()
        >>> assert not exists(dpath)
    """
    def __init__(self):
        self.dpath = None

    def __del__(self):
        self.cleanup()

    def ensure(self):
        import tempfile
        if not self.dpath:
            self.dpath = tempfile.mkdtemp()
        return self.dpath

    def cleanup(self):
        if self.dpath:
            shutil.rmtree(self.dpath)
            self.dpath = None

    def start(self):
        self.ensure()
        return self

    def __enter__(self):
        return self.start()

    def __exit__(self, type_, value, trace):
        self.cleanup()


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_path
        python -m ubelt.util_path all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
