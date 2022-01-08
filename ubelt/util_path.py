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
extra convenience methods corresponding to the extra functional methods in this
module.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import (
    dirname, exists, expanduser, expandvars, join, normpath, split, splitext,
)
import os
import sys
from ubelt import util_io

PY2 = sys.version_info[0] == 2
PY_LE_35 = sys.version_info[0:2] <= (3, 5)

if PY2:
    # Use pathlib2 backport in Python2
    import pathlib2 as pathlib
else:
    import pathlib


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
            Note: this is referred to as stem in :class:`ub.Path`.

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
        str: path - shortened path replacing the home directory with a symbol

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
        :func:`ubelt.Path.ensuredir`

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
    An extension of :class:`pathlib.Path` with extra convenience methods
    """

    def touch(self, mode=0o666, exist_ok=True):
        """
        Create this file with the given access mode, if it doesn't exist.

        Returns:
            Path: returns itself

        Notes:
            The :func:`ubelt.util_io.touch` function currently has a slightly
            different implementation. This uses whatever the pathlib version
            is. This may change in the future.
        """
        # modify touch to return self
        # Note: util_io.touch is more expressive than standard python
        # touch, may want to use that instead.
        super(Path, self).touch(mode=mode, exist_ok=exist_ok)
        return self

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
        As discussed in [CPythonIssue21301]_, CPython won't be adding
        expandvars to pathlib. I think this is a mistake, so I added it in this
        extension.

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
            Path: path - shortened path replacing the home directory with a symbol

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

    def delete(self):
        """
        Removes a file or recursively removes a directory.
        If a path does not exist, then this is does nothing.

        SeeAlso:
            :func:`ubelt.delete`

        Returns:
            Path: reference to self

        Example:
            >>> import ubelt as ub
            >>> from os.path import join
            >>> base = ub.Path(ub.ensure_app_cache_dir('ubelt', 'delete_test2'))
            >>> dpath1 = (base / 'dir').ensuredir()
            >>> (base / 'dir' / 'subdir').ensuredir()
            >>> (base / 'dir' / 'to_remove1.txt').touch()
            >>> fpath1 = (base / 'dir' / 'subdir' / 'to_remove3.txt').touch()
            >>> fpath2 = (base / 'dir' / 'subdir' / 'to_remove2.txt').touch()
            >>> assert all(p.exists() for p in [dpath1, fpath1, fpath2])
            >>> fpath1.delete()
            >>> assert all(p.exists() for p in [dpath1, fpath2])
            >>> assert not fpath1.exists()
            >>> dpath1.delete()
            >>> assert not any(p.exists() for p in [dpath1, fpath1, fpath2])
        """
        if PY_LE_35:  # nocover
            util_io.delete(str(self))
        else:
            util_io.delete(self)
        return self

    def __fspath__(self):
        # Only for 3.5. Remove after 3.5 support is removed.
        return str(self)


if PY_LE_35:  # nocover
    def _fspath(path):
        """
        Return the file system path representation of the object.

        If the object is str or bytes, then allow it to pass through as-is. If
        the object defines __fspath__(), then return the result of that method.
        All other types raise a TypeError.

        Internal helper for cases where os.fspath does not exist on older Python
        """
        import six
        string_types = six.string_types

        if isinstance(path, string_types):
            return path

        # Work from the object's type to match method resolution of other magic
        # methods.
        path_type = type(path)
        try:
            path_repr = path_type.__fspath__(path)
        except AttributeError:
            if hasattr(path_type, '__fspath__'):
                raise
            else:
                raise TypeError("expected str, bytes or os.PathLike object, "
                                "not " + path_type.__name__)
        if isinstance(path_repr, string_types):
            return path_repr
        else:
            raise TypeError("expected {}.__fspath__() to return str or bytes, "
                            "not {}".format(path_type.__name__,
                                            type(path_repr).__name__))
else:
    _fspath = os.fspath
