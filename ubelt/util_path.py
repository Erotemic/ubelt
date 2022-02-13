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
from os.path import (
    dirname, exists, expanduser, expandvars, join, normpath, split, splitext,
)
import os
import sys
from ubelt import util_io
import pathlib


__all__ = [
    'Path', 'TempDir', 'augpath', 'shrinkuser', 'userhome', 'ensuredir',
    'expandpath',
]


def augpath(path, suffix='', prefix='', ext=None, tail='', base=None,
            dpath=None, relative=None, multidot=False):
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

        suffix (str):
            placed between the basename and extension

        prefix (str):
            placed in front of the basename

        ext (str | None):
            if specified, replaces the extension

        tail (str | None):
            If specified, appends this text to the extension

        base (str | None):
            if specified, replaces the basename without extension.
            Note: this is referred to as stem in :class:`ub.Path`.

        dpath (str | PathLike | None):
            if specified, replaces the specified "relative" directory, which by
            default is the parent directory.

        relative (str | PathLike | None):
            Replaces ``relative`` with ``dpath`` in ``path``.
            Has no effect if ``dpath`` is not specified.
            Defaults to the dirname of the input ``path``.
            *experimental* not currently implemented.

        multidot (bool): Allows extensions to contain multiple
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
        >>> augpath('foo.tar.gz', suffix='_new', tail='.cache', multidot=True)
        foo_new.tar.gz.cache
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
    new_fname = ''.join((prefix, stem, suffix, ext, tail))
    newpath = join(dpath, new_fname)
    return newpath


def userhome(username=None):
    """
    Returns the path to some user's home directory.

    Args:
        username (str | None):
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
        home (str): symbol used to replace the home path.
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
        mode (int): octal mode of directory
        verbose (int): verbosity
        recreate (bool): if True removes the directory and
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
        os.makedirs(normpath(dpath), mode=mode, exist_ok=True)
    else:
        if verbose:
            print('Ensuring directory (existing {!r})'.format(dpath))
    return dpath


class TempDir(object):
    """
    Context for creating and cleaning up temporary directories.

    DEPRECATE

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

    Note:
        New methods are:
            * augment
            * ensuredir
            * expand
            * expandvars
            * shrinkuser

        Modified methods are:
            * touch

    Example:
        >>> # Ubelt extends pathlib functionality
        >>> import ubelt as ub
        >>> dpath = ub.Path('~/.cache/ubelt/demo_path').expand().ensuredir()
        >>> fpath = dpath / 'text_file.txt'
        >>> aug_fpath = fpath.augment(suffix='.aux', ext='.jpg').touch()
        >>> aug_dpath = dpath.augment('demo_path2')
        >>> assert aug_fpath.read_text() == ''
        >>> fpath.write_text('text data')
        >>> assert aug_fpath.exists()
        >>> assert not aug_fpath.delete().exists()
        >>> assert dpath.exists()
        >>> assert not dpath.delete().exists()
        >>> print(f'{str(fpath.shrinkuser()).replace(os.path.sep, "/")}')
        >>> print(f'{str(dpath.shrinkuser()).replace(os.path.sep, "/")}')
        >>> print(f'{str(aug_fpath.shrinkuser()).replace(os.path.sep, "/")}')
        >>> print(f'{str(aug_dpath.shrinkuser()).replace(os.path.sep, "/")}')
        ~/.cache/ubelt/demo_path/text_file.txt
        ~/.cache/ubelt/demo_path
        ~/.cache/ubelt/demo_path/text_file.aux.jpg
        ~/.cache/ubelt/demo_pathdemo_path2
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
        super().touch(mode=mode, exist_ok=exist_ok)
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
        return self.__class__(os.path.expandvars(self))

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
        return self.expandvars().expanduser()

    def shrinkuser(self, home='~'):
        """
        Inverse of :func:`os.path.expanduser`.

        Args:
            home (str): symbol used to replace the home path.
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
        shrunk = shrinkuser(self, home)
        new = self.__class__(shrunk)
        return new

    def augment(self, suffix='', prefix='', ext=None, stem=None, dpath=None,
                tail='', relative=None, multidot=False):
        """
        Create a new path with a different extension, basename, directory,
        prefix, and/or suffix.

        See :func:`augpath` for more details.

        Args:
            suffix (str):
                Text placed between the stem and extension. Default to ''.

            prefix (str):
                Text placed in front of the stem. Defaults to ''.

            ext (str | None):
                If specified, replaces the extension

            stem (str | None):
                If specified, replaces the stem (i.e. basename without
                extension). Note: named base in :func:`augpath`.

            dpath (str | PathLike | None):
                If specified, replaces the specified "relative" directory,
                which by default is the parent directory.

            tail (str | None):
                If specified, appends this text to the extension.

            relative (str | PathLike | None):
                Replaces ``relative`` with ``dpath`` in ``path``.
                Has no effect if ``dpath`` is not specified.
                Defaults to the dirname of the input ``path``.
                *experimental* not currently implemented.

            multidot (bool): Allows extensions to contain
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
        aug = augpath(self, suffix=suffix, prefix=prefix, ext=ext, base=stem,
                      dpath=dpath, relative=relative, multidot=multidot,
                      tail=tail)
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
        util_io.delete(self)
        return self

    @classmethod
    def appdir(cls, appname, *args, type='cache'):
        """
        Returns an operating system appropriate writable directory for an
        application to be used for cache, configs, or data.

        Args:
            appname (str): the name of the application
            *args[str] : optional subdirs
            type (str): can be 'cache', 'config', or 'data'.

        Returns:
            Path: a new path object

        Example:
            >>> import ubelt as ub
            >>> print(ub.Path.appdir('ubelt', type='cache').shrinkuser())
            >>> print(ub.Path.appdir('ubelt', type='config').shrinkuser())
            >>> print(ub.Path.appdir('ubelt', type='data').shrinkuser())

            # TODO: fix "want" string on the mac
            ~/.cache/ubelt
            ~/.config/ubelt
            ~/.local/share/ubelt

            >>> import pytest
            >>> with pytest.raises(KeyError):
            >>>     ub.Path.appdir('ubelt', type='other')
        """
        from ubelt import util_platform
        if type == 'cache':
            return cls(util_platform.get_app_cache_dir(appname, *args))
        elif type == 'config':
            return cls(util_platform.get_app_config_dir(appname, *args))
        elif type == 'data':
            return cls(util_platform.get_app_data_dir(appname, *args))
        else:
            raise KeyError(type)
