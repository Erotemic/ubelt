# -*- coding: utf-8 -*-
"""
Functions for working with filesystem paths.

The :func:`expandpath` function expands the tilde to $HOME and environment
variables to their values.

The :func:`augpath` function creates variants of an existing path without
having to spend multiple lines of code splitting it up and stitching it back
together.

The :func:`shrinkuser` function replaces your home directory with a tilde.

The :func:`userhome` function reports the home directory of the current user of
the operating system.

The :func:`ensuredir` function operates like ``mkdir -p`` in unix.

The :class:`Path` object is an extension of :class:`pathlib.Path` that contains
extra convinience methods corresponding to the extra functional methods in this
module.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import (
    dirname, exists, expanduser, expandvars, join, normpath, split, splitext,
)
import os
import sys
import pathlib


PY2 = sys.version_info[0] == 2


__all__ = [
    'Path', 'TempDir', 'augpath', 'shrinkuser', 'userhome', 'ensuredir',
    'expandpath',
]


def augpath(path, suffix='', prefix='', ext=None, base=None, dpath=None,
            relative=None, multidot=False):
    """
    Create a new path with a different extension, basename, directory, prefix,
    and/or suffix.

    A prefix is inserted before the basename. A suffix is inserted
    between the basename and the extension. The basename and extension can be
    replaced with a new one. Essentially a path is broken down into components
    (dpath, base, ext), and then recombined as (dpath, prefix, base, suffix,
    ext) after replacing any specified component.

    Args:
        path (str | PathLike): a path to augment

        suffix (str, default=''):
            placed between the basename and extension

        prefix (str, default=''):
            placed in front of the basename

        ext (str | None, default=None):
            if specified, replaces the extension

        base (str | None, default=None):
            if specified, replaces the basename without extension.
            Note: this is refered to as stem in :class:`ub.Path`.

        dpath (str | PathLike | None, default=None):
            if specified, replaces the specified "relative" directory, which by
            default is the parent directory.

        relative (str | PathLike | None, default=None):
            Replaces ``relative`` with ``dpath`` in ``path``.
            Has no effect if ``dpath`` is not specified.
            Defaults to the dirname of the input ``path``.
            *experimental* not currently implemented.

        multidot (bool, default=False): Allows extensions to contain multiple
            dots. Specifically, if False, everything after the last dot in the
            basename is the extension. If True, everything after the first dot
            in the basename is the extension.

    Returns:
        str: augmented path

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
        >>> from ubelt.util_path import *  # NOQA
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
        >>> augpath('foo.tar.gz', ext='.zip', multidot=True)
        foo.zip
        >>> augpath('foo.tar.gz', ext='.zip', multidot=False)
        foo.tar.zip
        >>> augpath('foo.tar.gz', suffix='_new', multidot=True)
        foo_new.tar.gz
    """
    stem = base  # new nomenclature

    # Breakup path
    if relative is None:
        orig_dpath, fname = split(path)
    else:  # nocover
        # if path.startswith(relative):
        #     orig_dpath = relative
        #     fname = relpath(path, relative)
        # else:
        #     orig_dpath, fname = split(path)
        raise NotImplementedError('Not implemented yet')

    if multidot:
        # The first dot defines the extension
        parts = fname.split('.', 1)
        orig_base = parts[0]
        orig_ext = '' if len(parts) == 1 else '.' + parts[1]
    else:
        # The last dot defines the extension
        orig_base, orig_ext = splitext(fname)
    # Replace parts with specified augmentations
    if dpath is None:
        dpath = orig_dpath
    if ext is None:
        ext = orig_ext
    if stem is None:
        stem = orig_base
    # Recombine into new path
    new_fname = ''.join((prefix, stem, suffix, ext))
    newpath = join(dpath, new_fname)
    return newpath


def userhome(username=None):
    """
    Returns the path to some user's home directory.

    Args:
        username (str | None, default=None):
            name of a user on the system. If not specified, the current user is
            inferred.

    Returns:
        str: userhome_dpath - path to the specified home directory

    Raises:
        KeyError: if the specified user does not exist on the system

        OSError: if username is unspecified and the current user cannot be
            inferred

    Example:
        >>> from ubelt.util_path import *  # NOQA
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


def shrinkuser(path, home='~'):
    """
    Inverse of :func:`os.path.expanduser`.

    Args:
        path (str | PathLike): path in system file structure
        home (str, default='~'): symbol used to replace the home path.
            Defaults to '~', but you might want to use '$HOME' or
            '%USERPROFILE%' instead.

    Returns:
        str: path - shortened path replacing the home directory with a tilde

    Example:
        >>> from ubelt.util_path import *  # NOQA
        >>> path = expanduser('~')
        >>> assert path != '~'
        >>> assert shrinkuser(path) == '~'
        >>> assert shrinkuser(path + '1') == path + '1'
        >>> assert shrinkuser(path + '/1') == join('~', '1')
        >>> assert shrinkuser(path + '/1', '$HOME') == join('$HOME', '1')
        >>> assert shrinkuser('.') == '.'
    """
    path = normpath(path)
    userhome_dpath = userhome()
    if path.startswith(userhome_dpath):
        if len(path) == len(userhome_dpath):
            path = home
        elif path[len(userhome_dpath)] == os.path.sep:
            path = home + path[len(userhome_dpath):]
    return path


def expandpath(path):
    """
    Shell-like environment variable and tilde path expansion.

    Less aggressive than truepath. Only expands environs and tilde. Does not
    change relative paths to absolute paths.

    Args:
        path (str | PathLike): string representation of a path

    Returns:
        str : expanded path

    Example:
        >>> from ubelt.util_path import *  # NOQA
        >>> import ubelt as ub
        >>> assert normpath(ub.expandpath('~/foo')) == join(ub.userhome(), 'foo')
        >>> assert ub.expandpath('foo') == 'foo'
    """
    path = expanduser(path)
    path = expandvars(path)
    return path


def ensuredir(dpath, mode=0o1777, verbose=0, recreate=False):
    r"""
    Ensures that directory will exist. Creates new dir with sticky bits by
    default

    Args:
        dpath (str | PathLike | Tuple[str | PathLike]): dir to ensure. Can also
            be a tuple to send to join
        mode (int, default=0o1777): octal mode of directory
        verbose (int, default=0): verbosity
        recreate (bool, default=False): if True removes the directory and
            all of its contents and creates a fresh new directory.
            USE CAREFULLY.

    Returns:
        str: path - the ensured directory

    SeeAlso:
        :method:`ub.Path.ensuredir`

    Note:
        This function is not thread-safe in Python2

    Example:
        >>> from ubelt.util_path import *  # NOQA
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
    if isinstance(dpath, (list, tuple)):
        dpath = join(*dpath)

    if recreate:
        import ubelt as ub
        ub.delete(dpath, verbose=verbose)

    if not exists(dpath):
        if verbose:
            print('Ensuring directory (creating {!r})'.format(dpath))
        if PY2:  # nocover
            os.makedirs(normpath(dpath), mode=mode)
        else:
            os.makedirs(normpath(dpath), mode=mode, exist_ok=True)
    else:
        if verbose:
            print('Ensuring directory (existing {!r})'.format(dpath))
    return dpath


class TempDir(object):
    """
    Context for creating and cleaning up temporary directories.

    Note:
        This exists because :class:`tempfile.TemporaryDirectory` was
        introduced in Python 3.2. Thus once ubelt no longer supports
        python 2.7, this class will be deprecated.

    Example:
        >>> from ubelt.util_path import *  # NOQA
        >>> with TempDir() as self:
        >>>     dpath = self.dpath
        >>>     assert exists(dpath)
        >>> assert not exists(dpath)

    Example:
        >>> from ubelt.util_path import *  # NOQA
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
            import shutil
            shutil.rmtree(self.dpath)
            self.dpath = None

    def start(self):
        self.ensure()
        return self

    def __enter__(self):
        return self.start()

    def __exit__(self, type_, value, trace):
        self.cleanup()


_PathBase = pathlib.WindowsPath if os.name == 'nt' else pathlib.PosixPath


class Path(_PathBase):
    """
    An extension of :class:`pathlib.Path` with extra convinience methods
    """

    def ensuredir(self, mode=0o777):
        """
        Concise alias of ``self.mkdir(parents=True, exist_ok=True)``

        Returns:
            Path: returns itself

        Example:
            >>> import ubelt as ub
            >>> cache_dpath = ub.ensure_app_cache_dir('ubelt')
            >>> dpath = ub.Path(join(cache_dpath, 'ensuredir'))
            >>> if dpath.exists():
            ...     os.rmdir(dpath)
            >>> assert not dpath.exists()
            >>> dpath.ensuredir()
            >>> assert dpath.exists()
            >>> dpath.rmdir()
            """
        if PY2:
            if not self.exists():
                self.mkdir(mode=mode, parents=True)
        else:
            self.mkdir(mode=mode, parents=True, exist_ok=True)
        return self

    def expandvars(self):
        """
        As discussed in CPythonIssue21301_, CPython wont be adding expandvars
        to pathlib. I think this is a mistake, so I added it in this extension.

        Returns:
            Path: path with expanded environment variables

        References:
            .. [CPythonIssue21301] https://bugs.python.org/issue21301
        """
        return self.__class__(os.path.expandvars(str(self)))

    def expand(self):
        """
        Expands user tilde and environment variables.

        Concise alias of `Path(os.path.expandvars(self.expanduser()))`

        Returns:
            Path: path with expanded environment variables and tildes

        Example:
            >>> import ubelt as ub
            >>> #home_v1 = ub.Path('$HOME').expand()
            >>> home_v2 = ub.Path('~/').expand()
            >>> assert isinstance(home_v2, ub.Path)
            >>> # xdoctest: +REQUIRES(PY3)
            >>> home_v3 = ub.Path.home()
            >>> #print('home_v1 = {!r}'.format(home_v1))
            >>> print('home_v2 = {!r}'.format(home_v2))
            >>> print('home_v3 = {!r}'.format(home_v3))
            >>> assert home_v3 == home_v2 # == home_v1
        """
        if PY2:  # nocover
            return self.__class__(os.path.expanduser(str(self.expandvars())))
        else:
            return self.expandvars().expanduser()

    def shrinkuser(self, home='~'):
        """
        Inverse of :func:`os.path.expanduser`.

        Args:
            home (str, default='~'): symbol used to replace the home path.
                Defaults to '~', but you might want to use '$HOME' or
                '%USERPROFILE%' instead.

        Returns:
            str: path - shortened path replacing the home directory with a tilde

        Example:
            >>> import ubelt as ub
            >>> path = ub.Path('~').expand()
            >>> assert str(path.shrinkuser()) == '~'
            >>> assert str(ub.Path((str(path) + '1')).shrinkuser()) == str(path) + '1'
            >>> assert str((path / '1').shrinkuser()) == join('~', '1')
            >>> assert str((path / '1').shrinkuser('$HOME')) == join('$HOME', '1')
            >>> assert str(ub.Path('.').shrinkuser()) == '.'
        """
        shrunk = shrinkuser(str(self), home)
        new = self.__class__(shrunk)
        return new

    def augment(self, suffix='', prefix='', ext=None, stem=None, dpath=None,
                relative=None, multidot=False):
        """
        Create a new path with a different extension, basename, directory,
        prefix, and/or suffix.

        See :func:`augpath` for more details.

        Args:
            suffix (str, default=''):
                placed between the stem and extension

            prefix (str, default=''):
                placed in front of the stem

            ext (str | None, default=None):
                if specified, replaces the extension

            stem (str | None, default=None):
                if specified, replaces the stem (i.e. basename without
                extension). Note: named base in :func:`augpath`.

            dpath (str | PathLike | None, default=None):
                if specified, replaces the specified "relative" directory,
                which by default is the parent directory.

            relative (str | PathLike | None, default=None):
                Replaces ``relative`` with ``dpath`` in ``path``.
                Has no effect if ``dpath`` is not specified.
                Defaults to the dirname of the input ``path``.
                *experimental* not currently implemented.

            multidot (bool, default=False): Allows extensions to contain
                multiple dots. Specifically, if False, everything after the
                last dot in the basename is the extension. If True, everything
                after the first dot in the basename is the extension.

        Returns:
            Path: augmented path

        Example:
            >>> import ubelt as ub
            >>> path = ub.Path('foo.bar')
            >>> suffix = '_suff'
            >>> prefix = 'pref_'
            >>> ext = '.baz'
            >>> newpath = path.augment(suffix, prefix, ext=ext, stem='bar')
            >>> print('newpath = {!r}'.format(newpath))
            newpath = Path('pref_bar_suff.baz')
        """
        aug = augpath(str(self), suffix=suffix, prefix=prefix, ext=ext,
                          base=stem, dpath=dpath, relative=relative,
                          multidot=multidot)
        new = self.__class__(aug)
        return new
