"""
Path and filesystem utilities.

The :class:`Path` object is an extension of :class:`pathlib.Path` that contains
extra convenience methods corresponding to the extra functional methods in this
module. (New in 0.11.0). See the class documentation for more details.

This module also defines functional path-related utilities, but moving forward
users should prefer using :class:`Path` over standalone functional methods. The
functions methods will still be available for the forseable future, but their
functionality is made redundant by :class:`Path`. For completeness these
functions are listed

The :func:`expandpath` function expands the tilde to ``$HOME`` and environment
variables to their values.

The :func:`augpath` function creates variants of an existing path without
having to spend multiple lines of code splitting it up and stitching it back
together.

The :func:`shrinkuser` function replaces your home directory with a tilde.

The :func:`userhome` function reports the home directory of the current user of
the operating system.

The :func:`ensuredir` function operates like ``mkdir -p`` in unix.

Note:
    In the future the part of this module that defines Path may be renamed to
    util_pathlib.
"""
from os.path import (
    dirname, exists, expanduser, expandvars, join, normpath, split, splitext,
)
import os
import sys
import pathlib
import warnings
from ubelt import util_io


__all__ = [
    'Path', 'TempDir', 'augpath', 'shrinkuser', 'userhome', 'ensuredir',
    'expandpath', 'ChDir',
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
            Note: this is referred to as stemsuffix in :func:`ub.Path.augment`.

        prefix (str):
            placed in front of the basename

        ext (str | None):
            if specified, replaces the extension

        tail (str | None):
            If specified, appends this text to the extension

        base (str | None):
            if specified, replaces the basename without extension.
            Note: this is referred to as stem in :func:`ub.Path.augment`.

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
            name of a user on the system. If unspecified, the current user is
            inferred from standard environment variables.

    Returns:
        str: path to the specified home directory

    Raises:
        KeyError: if the specified user does not exist on the system

        OSError: if username is unspecified and the current user cannot be
            inferred

    Example:
        >>> import ubelt as ub
        >>> import os
        >>> import getpass
        >>> username = getpass.getuser()
        >>> userhome_target = os.path.expanduser('~')
        >>> userhome_got1 = ub.userhome()
        >>> userhome_got2 = ub.userhome(username)
        >>> print(f'username={username}')
        >>> print(f'userhome_got1={userhome_got1}')
        >>> print(f'userhome_got2={userhome_got2}')
        >>> print(f'userhome_target={userhome_target}')
        >>> assert userhome_got1 == userhome_target
        >>> assert userhome_got2 == userhome_target
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
            Defaults to ``'~'``, but you might want to use ``'$HOME'`` or
            ``'%USERPROFILE%'`` instead.

    Returns:
        str: shortened path replacing the home directory with a symbol

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
        str: expanded path

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
        dpath (str | PathLike | Tuple[str | PathLike]):
            directory to create if it does not exist.

        mode (int):
            octal permissions if a new directory is created.
            Defaults to 0o1777.

        verbose (int): verbosity

        recreate (bool): if True removes the directory and
            all of its contents and creates a new empty directory.
            DEPRECATED: Use ``ub.Path(dpath).delete().ensuredir()`` instead.

    Returns:
        str: the ensured directory

    SeeAlso:
        :func:`ubelt.Path.ensuredir`

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('ubelt', 'ensuredir')
        >>> dpath.delete()
        >>> assert not dpath.exists()
        >>> ub.ensuredir(dpath)
        >>> assert dpath.exists()
        >>> dpath.delete()
    """
    if isinstance(dpath, (list, tuple)):
        dpath = join(*dpath)

    if recreate:
        from ubelt import schedule_deprecation
        schedule_deprecation(
            modname='ubelt',
            migration='Use ``ub.Path(dpath).delete().ensuredir()`` instead', name='recreate',
            type='argument of ensuredir', deprecate='1.3.0', error='2.0.0',
            remove='2.1.0',
        )
        util_io.delete(dpath, verbose=verbose)

    if not exists(dpath):
        if verbose:
            print('Ensuring directory (creating {!r})'.format(dpath))
        os.makedirs(normpath(dpath), mode=mode, exist_ok=True)
    else:
        if verbose:
            print('Ensuring directory (existing {!r})'.format(dpath))
    return dpath


class ChDir:
    """
    Context manager that changes the current working directory and then
    returns you to where you were.

    This is nearly the same as the stdlib :func:`contextlib.chdir`, with the
    exception that it will do nothing if the input path is None (i.e. the user
    did not want to change directories).

    SeeAlso:
        :func:`contextlib.chdir`

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('ubelt/tests/chdir').ensuredir()
        >>> dir1 = (dpath / 'dir1').ensuredir()
        >>> dir2 = (dpath / 'dir2').ensuredir()
        >>> with ChDir(dpath):
        >>>     assert ub.Path.cwd() == dpath
        >>>     # change to the given directory, and then returns back
        >>>     with ChDir(dir1):
        >>>         assert ub.Path.cwd() == dir1
        >>>         with ChDir(dir2):
        >>>             assert ub.Path.cwd() == dir2
        >>>             # changes inside the context manager will be reset
        >>>             os.chdir(dpath)
        >>>         assert ub.Path.cwd() == dir1
        >>>     assert ub.Path.cwd() == dpath
        >>>     with ChDir(dir1):
        >>>         assert ub.Path.cwd() == dir1
        >>>         with ChDir(None):
        >>>             assert ub.Path.cwd() == dir1
        >>>             # When disabled, the cwd does *not* reset at context exit
        >>>             os.chdir(dir2)
        >>>         assert ub.Path.cwd() == dir2
        >>>         os.chdir(dir1)
        >>>         # Dont change dirs, but reset to your cwd at context end
        >>>         with ChDir('.'):
        >>>             os.chdir(dir2)
        >>>         assert ub.Path.cwd() == dir1
        >>>     assert ub.Path.cwd() == dpath
    """
    def __init__(self, dpath):
        """
        Args:
            dpath (str | PathLike | None):
                The new directory to work in.
                If None, then the context manager is disabled.
        """
        self._context_dpath = dpath
        self._orig_dpath = None

    def __enter__(self):
        """
        Returns:
            ChDir: self
        """
        if self._context_dpath is not None:
            self._orig_dpath = os.getcwd()
            os.chdir(self._context_dpath)
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        if self._context_dpath is not None:
            os.chdir(self._orig_dpath)


class TempDir:
    """
    Context for creating and cleaning up temporary directories.

    Warning:

        DEPRECATED. Use :mod:`tempfile` instead.

    Note:
        This exists because :class:`tempfile.TemporaryDirectory` was
        introduced in Python 3.2. Thus once ubelt no longer supports
        python 2.7, this class will be deprecated.

    Attributes:
        dpath (str | None): the temporary path

    Note:
        # WE MAY WANT TO KEEP THIS FOR WINDOWS.

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
        from ubelt import schedule_deprecation
        schedule_deprecation(
            modname='ubelt',
            migration='Use tempfile instead', name='TempDir',
            type='class', deprecate='1.2.0', error='1.4.0',
            remove='1.5.0',
        )
        self.dpath = None

    def __del__(self):
        self.cleanup()

    def ensure(self):
        """
        Returns:
            str: the path
        """
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
        """
        Returns:
            TempDir: self
        """
        self.ensure()
        return self

    def __enter__(self):
        """
        Returns:
            TempDir: self
        """
        return self.start()

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        self.cleanup()


_PathBase = pathlib.WindowsPath if os.name == 'nt' else pathlib.PosixPath


class Path(_PathBase):
    """
    This class extends :class:`pathlib.Path` with extra functionality and
    convenience methods.

    New methods are designed to support chaining.

    In addition to new methods this class supports the addition (``+``)
    operator via which allows for better drop-in compatibility with code using
    existing string-based paths.

    Note:
        On windows this inherits from :class:`pathlib.WindowsPath`.

    New methods are

        * :py:meth:`ubelt.Path.ensuredir` - Like mkdir but with easier defaults.

        * :py:meth:`ubelt.Path.delete` - Previously pathlib could only remove one file at a time.

        * :py:meth:`ubelt.Path.copy` - Pathlib has no similar functionality.

        * :py:meth:`ubelt.Path.move` - Pathlib has no similar functionality.

        * :py:meth:`ubelt.Path.augment` - Unifies and extends disparate functionality across pathlib.

        * :py:meth:`ubelt.Path.expand` - Unifies existing environ and home expansion.

        * :py:meth:`ubelt.Path.ls` - Like iterdir, but more interactive.

        * :py:meth:`ubelt.Path.shrinkuser` - Python has no similar functionality.

        * :py:meth:`ubelt.Path.walk` - Pathlib had no similar functionality.

    New classmethods are

        * :py:meth:`ubelt.Path.appdir` - application directories

    Modified methods are

        * :py:meth:`ubelt.Path.touch` - returns self to support chaining

        * :py:meth:`ubelt.Path.chmod` - returns self to support chaining and
            now accepts string-based permission codes.

    Example:
        >>> # Ubelt extends pathlib functionality
        >>> import ubelt as ub
        >>> # Chain expansion and mkdir with cumbersome args.
        >>> dpath = ub.Path('~/.cache/ubelt/demo_path').expand().ensuredir()
        >>> fpath = dpath / 'text_file.txt'
        >>> # Augment is concise and chainable
        >>> aug_fpath = fpath.augment(stemsuffix='.aux', ext='.jpg').touch()
        >>> aug_dpath = dpath.augment(stemsuffix='demo_path2')
        >>> assert aug_fpath.read_text() == ''
        >>> fpath.write_text('text data')
        >>> assert aug_fpath.exists()
        >>> # Delete is akin to "rm -rf" and is also chainable.
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

    Inherited unmodified properties from :class:`pathlib.Path` are:

        * :py:data:`pathlib.PurePath.anchor`
        * :py:data:`pathlib.PurePath.name`
        * :py:data:`pathlib.PurePath.parts`
        * :py:data:`pathlib.PurePath.parent`
        * :py:data:`pathlib.PurePath.parents`
        * :py:data:`pathlib.PurePath.suffix`
        * :py:data:`pathlib.PurePath.suffixes`
        * :py:data:`pathlib.PurePath.stem`
        * :py:data:`pathlib.PurePath.drive`
        * :py:data:`pathlib.PurePath.root`

    Inherited unmodified classmethods from :class:`pathlib.Path` are:

        * :py:meth:`pathlib.Path.cwd`
        * :py:meth:`pathlib.Path.home`

    Inherited unmodified methods from :class:`pathlib.Path` are:

        * :py:meth:`pathlib.Path.samefile`
        * :py:meth:`pathlib.Path.iterdir`

        * :py:meth:`pathlib.Path.glob`
        * :py:meth:`pathlib.Path.rglob`

        * :py:meth:`pathlib.Path.resolve`

        * :py:meth:`pathlib.Path.lstat`
        * :py:meth:`pathlib.Path.stat`
        * :py:meth:`pathlib.Path.owner`
        * :py:meth:`pathlib.Path.group`

        * :py:meth:`pathlib.Path.open`
        * :py:meth:`pathlib.Path.read_bytes`
        * :py:meth:`pathlib.Path.read_text`
        * :py:meth:`pathlib.Path.write_bytes`
        * :py:meth:`pathlib.Path.write_text`
        * :py:meth:`pathlib.Path.readlink`

        * :py:meth:`pathlib.Path.mkdir` - we recommend :py:meth:`ubelt.Path.ensuredir` instead.

        * :py:meth:`pathlib.Path.lchmod`

        * :py:meth:`pathlib.Path.unlink`
        * :py:meth:`pathlib.Path.rmdir`

        * :py:meth:`pathlib.Path.rename`
        * :py:meth:`pathlib.Path.replace`

        * :py:meth:`pathlib.Path.symlink_to`
        * :py:meth:`pathlib.Path.hardlink_to`
        * :py:meth:`pathlib.Path.link_to` - deprecated

        * :py:meth:`pathlib.Path.exists`
        * :py:meth:`pathlib.Path.is_dir`
        * :py:meth:`pathlib.Path.is_file`
        * :py:meth:`pathlib.Path.is_mount`
        * :py:meth:`pathlib.Path.is_symlink`
        * :py:meth:`pathlib.Path.is_block_device`
        * :py:meth:`pathlib.Path.is_char_device`
        * :py:meth:`pathlib.Path.is_fifo`
        * :py:meth:`pathlib.Path.is_socket`

        * :py:meth:`pathlib.Path.expanduser` - we recommend :py:meth:`ubelt.Path.expand` instead.

        * :py:meth:`pathlib.PurePath.as_posix`
        * :py:meth:`pathlib.PurePath.as_uri`

        * :py:meth:`pathlib.PurePath.with_name` - we recommend :py:meth:`ubelt.Path.augment` instead.
        * :py:meth:`pathlib.PurePath.with_stem`  - we recommend :py:meth:`ubelt.Path.augment` instead.
        * :py:meth:`pathlib.PurePath.with_suffix` - we recommend :py:meth:`ubelt.Path.augment` instead.

        * :py:meth:`pathlib.PurePath.relative_to`

        * :py:meth:`pathlib.PurePath.joinpath`

        * :py:meth:`pathlib.PurePath.is_relative_to`
        * :py:meth:`pathlib.PurePath.is_absolute`
        * :py:meth:`pathlib.PurePath.is_reserved`

        * :py:meth:`pathlib.PurePath.match`
    """
    __slots__ = ()

    @classmethod
    def appdir(cls, appname=None, *args, type='cache'):
        """
        Returns a standard platform specific directory for an application to
        use as cache, config, or data.

        The default root location depends on the platform and is specified the
        the following table:

        TextArt:

                   | POSIX            | Windows        | MacOSX
            data   | $XDG_DATA_HOME   | %APPDATA%      | ~/Library/Application Support
            config | $XDG_CONFIG_HOME | %APPDATA%      | ~/Library/Application Support
            cache  | $XDG_CACHE_HOME  | %LOCALAPPDATA% | ~/Library/Caches


            If an environment variable is not specified the defaults are:
                APPDATA      = ~/AppData/Roaming
                LOCALAPPDATA = ~/AppData/Local

                XDG_DATA_HOME   = ~/.local/share
                XDG_CACHE_HOME  = ~/.cache
                XDG_CONFIG_HOME = ~/.config

        Args:
            appname (str | None):
                The name of the application.

            *args : optional subdirs

            type (str):
                the type of data the expected to be stored in this application
                directory. Valid options are 'cache', 'config', or 'data'.

        Returns:
            Path: a new path object for the specified application directory.

        SeeAlso:
            This provides functionality similar to the
            `appdirs <https://pypi.org/project/appdirs/>`_ -
            and
            `platformdirs <https://platformdirs.readthedocs.io/en/latest/api.html>`_ -
            packages.

        Example:
            >>> # xdoctest: +IGNORE_WANT
            >>> import ubelt as ub
            >>> print(ub.Path.appdir('ubelt', type='cache').shrinkuser())
            >>> print(ub.Path.appdir('ubelt', type='config').shrinkuser())
            >>> print(ub.Path.appdir('ubelt', type='data').shrinkuser())
            ~/.cache/ubelt
            ~/.config/ubelt
            ~/.local/share/ubelt
            >>> import pytest
            >>> with pytest.raises(KeyError):
            >>>     ub.Path.appdir('ubelt', type='other')

        Example:
            >>> # xdoctest: +IGNORE_WANT
            >>> import ubelt as ub
            >>> # Can now call appdir without any arguments
            >>> print(ub.Path.appdir().shrinkuser())
            ~/.cache
        """
        from ubelt import util_platform
        if type == 'cache':
            base = util_platform.platform_cache_dir()
        elif type == 'config':
            base = util_platform.platform_config_dir()
        elif type == 'data':
            base = util_platform.platform_data_dir()
        else:
            raise KeyError(type)

        if appname is None:
            return cls(base, *args)
        else:
            return cls(base, appname, *args)

    def augment(self, prefix='', stemsuffix='', ext=None, stem=None, dpath=None,
                tail='', relative=None, multidot=False, suffix=''):
        """
        Create a new path with a different extension, basename, directory,
        prefix, and/or suffix.

        See :func:`augpath` for more details.

        Args:
            prefix (str):
                Text placed in front of the stem. Defaults to ''.

            stemsuffix (str):
                Text placed between the stem and extension. Defaults to ''.

            ext (str | None):
                If specified, replaces the extension

            stem (str | None):
                If specified, replaces the stem (i.e. basename without
                extension).

            dpath (str | PathLike | None):
                If specified, replaces the specified "relative" directory,
                which by default is the parent directory.

            tail (str | None):
                If specified, appends this text the very end of the path -
                after the extension.

            relative (str | PathLike | None):
                Replaces ``relative`` with ``dpath`` in ``path``.
                Has no effect if ``dpath`` is not specified.
                Defaults to the dirname of the input ``path``.
                *experimental* not currently implemented.

            multidot (bool): Allows extensions to contain
                multiple dots. Specifically, if False, everything after the
                last dot in the basename is the extension. If True, everything
                after the first dot in the basename is the extension.

        SeeAlso:
            :py:meth:`pathlib.Path.with_stem`
            :py:meth:`pathlib.Path.with_name`
            :py:meth:`pathlib.Path.with_suffix`

        Returns:
            Path: augmented path

        Warning:
            NOTICE OF BACKWARDS INCOMPATABILITY.

            THE INITIAL RELEASE OF Path.augment suffered from an unfortunate
            variable naming decision that conflicts with pathlib.Path

            .. code:: python

                p = ub.Path('the.entire.fname.or.dname.is.the.name.exe')
                print(f'p     ={p}')
                print(f'p.name={p.name}')
                p = ub.Path('the.stem.ends.here.ext')
                print(f'p     ={p}')
                print(f'p.stem={p.stem}')
                p = ub.Path('only.the.last.dot.is.the.suffix')
                print(f'p       ={p}')
                print(f'p.suffix={p.suffix}')
                p = ub.Path('but.all.suffixes.can.be.recovered')
                print(f'p         ={p}')
                print(f'p.suffixes={p.suffixes}')

        Example:
            >>> import ubelt as ub
            >>> path = ub.Path('foo.bar')
            >>> suffix = '_suff'
            >>> prefix = 'pref_'
            >>> ext = '.baz'
            >>> newpath = path.augment(prefix=prefix, stemsuffix=suffix, ext=ext, stem='bar')
            >>> print('newpath = {!r}'.format(newpath))
            newpath = Path('pref_bar_suff.baz')

        Example:
            >>> import ubelt as ub
            >>> path = ub.Path('foo.bar')
            >>> stemsuffix = '_suff'
            >>> prefix = 'pref_'
            >>> ext = '.baz'
            >>> newpath = path.augment(prefix=prefix, stemsuffix=stemsuffix, ext=ext, stem='bar')
            >>> print('newpath = {!r}'.format(newpath))

        Example:
            >>> # Compare our augpath(ext=...) versus pathlib with_suffix(...)
            >>> import ubelt as ub
            >>> cases = [
            >>>     ub.Path('no_ext'),
            >>>     ub.Path('one.ext'),
            >>>     ub.Path('double..dot'),
            >>>     ub.Path('two.many.cooks'),
            >>>     ub.Path('path.with.three.dots'),
            >>>     ub.Path('traildot.'),
            >>>     ub.Path('doubletraildot..'),
            >>>     ub.Path('.prefdot'),
            >>>     ub.Path('..doubleprefdot'),
            >>> ]
            >>> for path in cases:
            >>>     print('--')
            >>>     print('path = {}'.format(ub.repr2(path, nl=1)))
            >>>     ext = '.EXT'
            >>>     method_pathlib = path.with_suffix(ext)
            >>>     method_augment = path.augment(ext=ext)
            >>>     if method_pathlib == method_augment:
            >>>         print(ub.color_text('sagree', 'green'))
            >>>     else:
            >>>         print(ub.color_text('disagree', 'red'))
            >>>     print('path.with_suffix({}) = {}'.format(ext, ub.repr2(method_pathlib, nl=1)))
            >>>     print('path.augment(ext={}) = {}'.format(ext, ub.repr2(method_augment, nl=1)))
            >>>     print('--')
        """
        if suffix:  # nocover
            from ubelt.util_deprecate import schedule_deprecation
            schedule_deprecation(
                'ubelt', 'suffix', 'arg',
                deprecate='1.1.3', remove='1.4.0',
                migration='Use stemsuffix instead',
            )
            if not stemsuffix:
                stemsuffix = suffix
            warnings.warn(
                'DEVELOPER NOTICE: The ubelt.Path.augment function may '
                'experience a BACKWARDS INCOMPATIBLE update in the future '
                'having to do with the suffix argument to ub.Path.augment '
                'To avoid any issue use the ``stemsuffix` argument or use the '
                '``ubelt.augpath`` function instead. '
                'If you see this warning, please make an '
                'issue on https://github.com/Erotemic/ubelt/issues indicating '
                'that there are users of this function in the wild. If there '
                'are none, then this signature will be "fixed", but if anyone '
                'depends on this feature then we will continue to support it as '
                'is.'
            )

        aug = augpath(self, suffix=stemsuffix, prefix=prefix, ext=ext, base=stem,
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
            >>> base = ub.Path.appdir('ubelt', 'delete_test2')
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

    def ensuredir(self, mode=0o777):
        """
        Concise alias of ``self.mkdir(parents=True, exist_ok=True)``

        Args:
            mode (int):
                octal permissions if a new directory is created.
                Defaults to 0o777.

        Returns:
            Path: returns itself

        Example:
            >>> import ubelt as ub
            >>> cache_dpath = ub.Path.appdir('ubelt').ensuredir()
            >>> dpath = ub.Path(cache_dpath, 'newdir')
            >>> dpath.delete()
            >>> assert not dpath.exists()
            >>> dpath.ensuredir()
            >>> assert dpath.exists()
            >>> dpath.rmdir()
        """
        self.mkdir(mode=mode, parents=True, exist_ok=True)
        return self

    def mkdir(self, mode=511, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.

        Note:
            The ubelt extension is the same as the original pathlib method,
            except this returns returns the path instead of None.

        Args:
            mode (int) : permission bits
            parents (bool) : create parents
            exist_ok (bool) : fail if exists

        Returns:
            Path: returns itself
        """
        super().mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
        return self

    def expand(self):
        """
        Expands user tilde and environment variables.

        Concise alias of ``Path(os.path.expandvars(self.expanduser()))``

        Returns:
            Path: path with expanded environment variables and tildes

        Example:
            >>> import ubelt as ub
            >>> home_v1 = ub.Path('~/').expand()
            >>> home_v2 = ub.Path.home()
            >>> print('home_v1 = {!r}'.format(home_v1))
            >>> print('home_v2 = {!r}'.format(home_v2))
            >>> assert home_v1 == home_v2
        """
        return self.expandvars().expanduser()

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

    def ls(self, pattern=None):
        """
        A convenience function to list all paths in a directory.

        This is a wrapper around iterdir that returns the results as a list
        instead of a generator. This is mainly for faster navigation in
        IPython. In production code ``iterdir`` or ``glob`` should be used
        instead.

        Args:
            pattern (None | str):
                if specified, performs a glob instead of an iterdir.

        Returns:
            List['Path']: an eagerly evaluated list of paths

        Note:
            When pattern is specified only paths matching the pattern are
            returned, not the paths inside matched directories.  This is
            different than bash semantics where the pattern is first expanded
            and then ls is performed on all matching paths.

        Example:
            >>> import ubelt as ub
            >>> self = ub.Path.appdir('ubelt/tests/ls')
            >>> (self / 'dir1').ensuredir()
            >>> (self / 'dir2').ensuredir()
            >>> (self / 'file1').touch()
            >>> (self / 'file2').touch()
            >>> (self / 'dir1/file3').touch()
            >>> (self / 'dir2/file4').touch()
            >>> children = self.ls()
            >>> assert isinstance(children, list)
            >>> print(ub.repr2(sorted([p.relative_to(self) for p in children])))
            [
                Path('dir1'),
                Path('dir2'),
                Path('file1'),
                Path('file2'),
            ]
            >>> children = self.ls('dir*/*')
            >>> assert isinstance(children, list)
            >>> print(ub.repr2(sorted([p.relative_to(self) for p in children])))
            [
                Path('dir1/file3'),
                Path('dir2/file4'),
            ]
        """
        if pattern is None:
            return list(self.iterdir())
        else:
            return list(self.glob(pattern))

    # TODO:
    # def _glob(self):
    #     """
    #     I would like some way of globbing using patterns contained in the path
    #     itself. Perhaps this goes into expand?
    #     """
    #     import glob
    #     yield from map(self.__class__, glob.glob(self))

    def shrinkuser(self, home='~'):
        """
        Shrinks your home directory by replacing it with a tilde.

        This is the inverse of :func:`os.path.expanduser`.

        Args:
            home (str): symbol used to replace the home path.
                Defaults to '~', but you might want to use '$HOME' or
                '%USERPROFILE%' instead.

        Returns:
            Path: shortened path replacing the home directory with a symbol

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

    def chmod(self, mode, follow_symlinks=True):
        """
        Change the permissions of the path, like os.chmod().

        Args:
            mode (int | str): either a stat code to pass directly to
                :func:`os.chmod` or a string-based code to construct modified
                permissions. See note for details on the string-based chmod
                codes.

            follow_symlinks (bool):
                if True, and this path is a symlink, modify permission of the
                file it points to, otherwise if False, modify the link
                permission.

        Note:
            From the chmod man page:

            The format of a symbolic mode is [ugoa...][[-+=][perms...]...], where
            perms is either zero or more letters from the set rwxXst, or a single
            letter from the set  ugo.   Multiple symbolic modes can be given,
            separated by commas.

        Note:
            Like :func:`os.chmod`, this may not work on Windows or on certain
            filesystems.

        Returns:
            Path: returns self for chaining

        Example:
            >>> # xdoctest: +REQUIRES(POSIX)
            >>> import ubelt as ub
            >>> from ubelt.util_path import _encode_chmod_int
            >>> dpath = ub.Path.appdir('ubelt/tests/chmod').ensuredir()
            >>> fpath = (dpath / 'file.txt').touch()
            >>> fpath.chmod('ugo+rw,ugo-x')
            >>> print(_encode_chmod_int(fpath.stat().st_mode))
            u=rw,g=rw,o=rw
            >>> fpath.chmod('o-rwx')
            >>> print(_encode_chmod_int(fpath.stat().st_mode))
            u=rw,g=rw
            >>> fpath.chmod(0o646)
            >>> print(_encode_chmod_int(fpath.stat().st_mode))
            u=rw,g=r,o=rw
        """
        if isinstance(mode, str):
            # Resolve mode
            # Follow symlinks was added to pathlib.Path.stat in 3.10
            # but os.stat has had it since 3.3, so use that instead.
            old_mode = os.stat(self, follow_symlinks=follow_symlinks).st_mode
            # old_mode = self.stat(follow_symlinks=follow_symlinks).st_mode
            mode = _resolve_chmod_code(old_mode, mode)
        os.chmod(self, mode, follow_symlinks=follow_symlinks)
        return self

    # Should not need to modify unless we want chanability here.
    # def lchmod(self, mode):
    #     """
    #     Like chmod(), except if the path points to a symlink, the symlink's
    #     permissions are changed, rather than its target's.
    #
    #     Args:
    #         mode (int | str): either a stat code to pass directly to
    #             :func:`os.chmod` or a string-based code to construct modified
    #             permissions.
    #
    #     Returns:
    #         Path: returns self for chaining
    #
    #     Example:
    #         >>> import ubelt as ub
    #         >>> from ubelt.util_path import _encode_chmod_int
    #         >>> dpath = ub.Path.appdir('ubelt/tests/chmod').ensuredir()
    #         >>> fpath = (dpath / 'file1.txt').delete().touch()
    #         >>> lpath = (dpath / 'link1.txt').delete()
    #         >>> lpath.symlink_to(fpath)
    #         >>> print(_encode_chmod_int(fpath.stat().st_mode))
    #         >>> lpath.lchmod('a+rwx')
    #         >>> print(_encode_chmod_int(fpath.stat().st_mode))
    #     """
    #     return self.chmod(mode, follow_symlinks=False)

    def touch(self, mode=0o666, exist_ok=True):
        """
        Create this file with the given access mode, if it doesn't exist.

        Returns:
            Path: returns itself

        Note:
            The :func:`ubelt.util_io.touch` function currently has a slightly
            different implementation. This uses whatever the pathlib version
            is. This may change in the future.
        """
        # modify touch to return self
        # Note: util_io.touch is more expressive than standard python
        # touch, may want to use that instead.
        super().touch(mode=mode, exist_ok=exist_ok)
        return self

    def walk(self, topdown=True, onerror=None, followlinks=False):
        """
        A variant of :func:`os.walk` for pathlib

        Args:
            topdown (bool):
                if True starts yield nodes closer to the root first otherwise
                yield nodes closer to the leaves first.

            onerror (Callable[[OSError], None] | None):
                A function with one argument of type OSError. If the
                error is raised the walk is aborted, otherwise it continues.

            followlinks (bool):
                if True recurse into symbolic directory links

        Yields:
            Tuple['Path', List[str], List[str]]:
                the root path, directory names, and file names

        Example:
            >>> import ubelt as ub
            >>> self = ub.Path.appdir('ubelt/tests/ls')
            >>> (self / 'dir1').ensuredir()
            >>> (self / 'dir2').ensuredir()
            >>> (self / 'file1').touch()
            >>> (self / 'file2').touch()
            >>> (self / 'dir1/file3').touch()
            >>> (self / 'dir2/file4').touch()
            >>> subdirs = list(self.walk())
            >>> assert len(subdirs) == 3

        Example:
            >>> # Modified from the stdlib
            >>> import os
            >>> from os.path import join, getsize
            >>> import email
            >>> import ubelt as ub
            >>> base = ub.Path(email.__file__).parent
            >>> for root, dirs, files in base.walk():
            >>>     print(root, " consumes", end="")
            >>>     print(sum(getsize(join(root, name)) for name in files), end="")
            >>>     print("bytes in ", len(files), " non-directory files")
            >>>     if 'CVS' in dirs:
            >>>         dirs.remove('CVS')  # don't visit CVS directories
        """
        cls = self.__class__
        walker = os.walk(self, topdown=topdown, onerror=onerror,
                         followlinks=followlinks)
        for root, dnames, fnames in walker:
            yield (cls(root), dnames, fnames)

    def __add__(self, other):
        """
        Returns a new string starting with this fspath representation.

        Returns:
            str

        Allows ubelt.Path to be a better drop-in replacement when working with
        string-based paths.

        Note:
            It is not recommended to write new code that uses this behavior.
            This exists to make it easier to transition existing str-based
            paths to pathlib.

        Example:
            >>> import ubelt as ub
            >>> base = ub.Path('base')
            >>> base_ = ub.Path('base/')
            >>> base2 = ub.Path('base/2')
            >>> assert base + 'foo' == 'basefoo'
            >>> assert base_ + 'foo' == 'basefoo'
            >>> assert base2 + 'foo' == str(base2.augment(tail='foo'))
        """
        return os.fspath(self) + other

    def __radd__(self, other):
        """
        Returns a new string ending with this fspath representation.

        Returns:
            str

        Allows ubelt.Path to be a better drop-in replacement when working with
        string-based paths.

        Note:
            It is not recommended to write new code that uses this behavior.
            This exists to make it easier to transition existing str-based
            paths to pathlib.

        Example:
            >>> import ubelt as ub
            >>> base = ub.Path('base')
            >>> base_ = ub.Path('base/')
            >>> base2 = ub.Path('base/2')
            >>> assert 'foo' + base == 'foobase'
            >>> assert 'foo' + base_ == 'foobase'
            >>> assert 'foo' + base2 == str(base2.augment(dpath='foobase'))
        """
        return other + os.fspath(self)

    def endswith(self, suffix, *args):
        """
        Test if the fspath representation ends with ``suffix``.

        Allows ubelt.Path to be a better drop-in replacement when working with
        string-based paths.

        Args:
            suffix (str | Tuple[str, ...]):
                One or more suffixes to test for

            *args:
                start (int): if specified begin testing at this position.
                end (int): if specified stop testing at this position.

        Returns:
            bool: True if any of the suffixes match.

        Example:
            >>> import ubelt as ub
            >>> base = ub.Path('base')
            >>> assert base.endswith('se')
            >>> assert not base.endswith('be')
            >>> # test start / stop cases
            >>> assert ub.Path('aabbccdd').endswith('cdd', 5)
            >>> assert not ub.Path('aabbccdd').endswith('cdd', 6)
            >>> assert ub.Path('aabbccdd').endswith('cdd', 5, 10)
            >>> assert not ub.Path('aabbccdd').endswith('cdd', 5, 7)
            >>> # test tuple case
            >>> assert ub.Path('aabbccdd').endswith(('foo', 'cdd'))
            >>> assert ub.Path('foo').endswith(('foo', 'cdd'))
            >>> assert not ub.Path('bar').endswith(('foo', 'cdd'))
        """
        return os.fspath(self).endswith(suffix, *args)

    def startswith(self, prefix, *args):
        """
        Test if the fspath representation starts with ``prefix``.

        Allows ubelt.Path to be a better drop-in replacement when working with
        string-based paths.

        Args:
            prefix (str | Tuple[str, ...]):
                One or more prefixes to test for

            *args:
                start (int): if specified begin testing at this position.
                end (int): if specified stop testing at this position.

        Returns:
            bool: True if any of the prefixes match.

        Example:
            >>> import ubelt as ub
            >>> base = ub.Path('base')
            >>> assert base.startswith('base')
            >>> assert not base.startswith('all your')
            >>> # test start / stop cases
            >>> assert ub.Path('aabbccdd').startswith('aab', 0)
            >>> assert ub.Path('aabbccdd').startswith('aab', 0, 5)
            >>> assert not ub.Path('aabbccdd').startswith('aab', 1, 5)
            >>> assert not ub.Path('aabbccdd').startswith('aab', 0, 2)
            >>> # test tuple case
            >>> assert ub.Path('aabbccdd').startswith(('foo', 'aab'))
            >>> assert ub.Path('foo').startswith(('foo', 'aab'))
            >>> assert not ub.Path('bar').startswith(('foo', 'aab'))
        """
        return os.fspath(self).startswith(prefix, *args)

    # More shutil functionality
    # This is discussed in https://peps.python.org/pep-0428/#filesystem-modification

    def _request_copy_function(self, follow_file_symlinks=True,
                               follow_dir_symlinks=True, meta='stats'):
        """
        Get a copy_function based on specified capabilities
        """
        import shutil
        from functools import partial
        if meta is None:
            copy_function = partial(shutil.copyfile, follow_symlinks=follow_file_symlinks)
        elif meta == 'stats':
            copy_function = partial(shutil.copy2, follow_symlinks=follow_file_symlinks)
        elif meta == 'mode':
            copy_function = partial(shutil.copy, follow_symlinks=follow_file_symlinks)
        else:
            raise KeyError(meta)
        return copy_function

    def copy(self, dst, follow_file_symlinks=False, follow_dir_symlinks=False,
             meta='stats', overwrite=False):
        """
        Copy this file or directory to dst.

        By default files are never overwritten and symlinks are copied as-is.

        At a basic level (i.e. ignoring symlinks) for each path argument
        (``src`` and ``dst``) these can either be files, directories, or not
        exist. Given these three states, the following table summarizes how
        this function copies this path to its destination.

        TextArt:

            +----------+------------------------+------------------------+----------+
            | dst      | dir                    | file                   | no-exist |
            +----------+                        |                        |          |
            | src      |                        |                        |          |
            +==========+========================+========================+==========+
            | dir      | error-or-overwrite-dst | error                  | dst      |
            +----------+------------------------+------------------------+----------+
            | file     | dst / src.name         | error-or-overwrite-dst | dst      |
            +----------+------------------------+------------------------+----------+
            | no-exist | error                  | error                  | error    |
            +----------+------------------------+------------------------+----------+

        In general, the contents of src will be the contents of dst, except for
        the one case where a file is copied into an existing directory. In this
        case the name is used to construct a fully qualified destination.

        Args:
            dst (str | PathLike):
                if ``src`` is a file and ``dst`` does not exist, copies this to ``dst``
                if ``src`` is a file and ``dst`` is a directory, copies this to ``dst / src.name``

                if ``src`` is a directory and ``dst`` does not exist, copies this to ``dst``
                if ``src`` is a directory and ``dst`` is a directory, errors unless
                overwrite is True, in which case, copies this to ``dst`` and
                overwrites anything conflicting path.

            follow_file_symlinks (bool):
                If True and src is a link, the link will be resolved before
                it is copied (i.e. the data is duplicated), otherwise just
                the link itself will be copied.

            follow_dir_symlinks (bool):
                if True when src is a directory and contains symlinks to
                other directories, the contents of the linked data are
                copied, otherwise when False only the link itself is
                copied.

            meta (str | None):
                Indicates what metadata bits to copy. This can be 'stats' which
                tries to copy all metadata (i.e. like :py:func:`shutil.copy2`),
                'mode' which copies just the permission bits (i.e. like
                :py:func:`shutil.copy`), or None, which ignores all metadata
                (i.e.  like :py:func:`shutil.copyfile`).

            overwrite (bool):
                if False, and target file exists, this will raise an error,
                otherwise the file will be overwritten.

        Returns:
            Path: where the path was copied to

        Note:
            This is implemented with a combination of :func:`shutil.copy`,
            :func:`shutil.copy2`, and :func:`shutil.copytree`, but the defaults
            and behavior here are different (and ideally safer and more
            intuitive).

        Note:
            Unlike cp on Linux, copying a src directory into a dst directory
            will not implicitly add the src directory name to the dst
            directory. This means we cannot copy directory ``<parent>/<dname>``
            to ``<dst>`` and expect the result to be ``<dst>/<dname>``.

            Conceptually you can expect ``<parent>/<dname>/<contents>``
            to exist in ``<dst>/<contents>``.

        Example:
            >>> import ubelt as ub
            >>> root = ub.Path.appdir('ubelt', 'tests', 'path', 'copy').delete().ensuredir()
            >>> paths = {}
            >>> dpath = (root / 'orig').ensuredir()
            >>> clone0 = (root / 'dst_is_explicit').ensuredir()
            >>> clone1 = (root / 'dst_is_parent').ensuredir()
            >>> paths['fpath'] = (dpath / 'file0.txt').touch()
            >>> paths['empty_dpath'] = (dpath / 'empty_dpath').ensuredir()
            >>> paths['nested_dpath'] = (dpath / 'nested_dpath').ensuredir()
            >>> (dpath / 'nested_dpath/d0').ensuredir()
            >>> (dpath / 'nested_dpath/d0/f1.txt').touch()
            >>> (dpath / 'nested_dpath/d0/f2.txt').touch()
            >>> print('paths = {}'.format(ub.repr2(paths, nl=1)))
            >>> assert all(p.exists() for p in paths.values())
            >>> paths['fpath'].copy(clone0 / 'file0.txt')
            >>> paths['fpath'].copy(clone1)
            >>> paths['empty_dpath'].copy(clone0 / 'empty_dpath')
            >>> paths['empty_dpath'].copy((clone1 / 'empty_dpath_alt').ensuredir(), overwrite=True)
            >>> paths['nested_dpath'].copy(clone0 / 'nested_dpath')
            >>> paths['nested_dpath'].copy((clone1 / 'nested_dpath_alt').ensuredir(), overwrite=True)

        Ignore:
            # Enumerate cases
            rows = [
                {'src': 'no-exist', 'dst': 'no-exist', 'result': 'error'},
                {'src': 'no-exist', 'dst': 'file',     'result': 'error'},
                {'src': 'no-exist', 'dst': 'dir',      'result': 'error'},

                {'src': 'file', 'dst': 'no-exist', 'result': 'dst'},
                {'src': 'file', 'dst': 'dir',      'result': 'dst / src.name'},
                {'src': 'file', 'dst': 'file',     'result': 'error-or-overwrite-dst'},

                {'src': 'dir', 'dst': 'no-exist', 'result': 'dst'},
                {'src': 'dir', 'dst': 'dir',      'result': 'error-or-overwrite-dst'},
                {'src': 'dir', 'dst': 'file',     'result': 'error'},
            ]
            import pandas as pd
            df = pd.DataFrame(rows)
            piv = df.pivot(['src'], ['dst'], 'result')
            print(piv.to_markdown(tablefmt="grid", index=True))

            See: ~/code/ubelt/tests/test_path.py for test cases
        """
        import shutil
        copy_function = self._request_copy_function(
            follow_file_symlinks=follow_file_symlinks,
            follow_dir_symlinks=follow_dir_symlinks, meta=meta)
        if self.is_dir():
            if sys.version_info[0:2] < (3, 8):  # nocover
                copytree = _compat_copytree
            else:
                copytree = shutil.copytree
            dst = copytree(
                self, dst, copy_function=copy_function,
                symlinks=not follow_dir_symlinks, dirs_exist_ok=overwrite)
        elif self.is_file():
            if not overwrite:
                dst = Path(dst)
                if dst.is_dir():
                    real_dst = dst / self.name
                else:
                    real_dst = dst
                if real_dst.exists():
                    raise FileExistsError('Cannot overwrite existing file unless overwrite=True')
            dst = copy_function(self, dst)
        else:
            raise FileExistsError('The source path does not exist')
        return Path(dst)

    def move(self, dst, follow_file_symlinks=False, follow_dir_symlinks=False,
             meta='stats'):
        """
        Move a file from one location to another, or recursively move a
        directory from one location to another.

        This method will refuse to overwrite anything, and there is currently
        no overwrite option for technical reasons. This may change in the
        future.

        Args:
            dst (str | PathLike):
                A non-existing path where this file will be moved.

            follow_file_symlinks (bool):
                If True and src is a link, the link will be resolved before
                it is copied (i.e. the data is duplicated), otherwise just
                the link itself will be copied.

            follow_dir_symlinks (bool):
                if True when src is a directory and contains symlinks to
                other directories, the contents of the linked data are
                copied, otherwise when False only the link itself is
                copied.

            meta (str | None):
                Indicates what metadata bits to copy. This can be 'stats' which
                tries to copy all metadata (i.e. like shutil.copy2), 'mode'
                which copies just the permission bits (i.e. like shutil.copy),
                or None, which ignores all metadata (i.e.  like
                shutil.copyfile).

        Note:
            This method will refuse to overwrite anything.

            This is implemented via :func:`shutil.move`, which depends heavily
            on :func:`os.rename` semantics. For this reason, this function
            will error if it would overwrite any data. If you want an
            overwriting variant of move we recommend you either either copy the
            data, and then delete the original (potentially inefficient), or
            use :func:`shutil.move` directly if you know how :func:`os.rename`
            works on your system.

        Returns:
            Path: where the path was moved to

        Example:
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('ubelt', 'tests', 'path', 'move').delete().ensuredir()
            >>> paths = {}
            >>> paths['dpath0'] = (dpath / 'dpath0').ensuredir()
            >>> paths['dpath00'] = (dpath / 'dpath0' / 'sub0').ensuredir()
            >>> paths['fpath000'] = (dpath / 'dpath0' / 'sub0' / 'f0.txt').touch()
            >>> paths['fpath001'] = (dpath / 'dpath0' / 'sub0' / 'f1.txt').touch()
            >>> paths['dpath01'] = (dpath / 'dpath0' / 'sub1').ensuredir()
            >>> print('paths = {}'.format(ub.repr2(paths, nl=1)))
            >>> assert all(p.exists() for p in paths.values())
            >>> paths['dpath0'].move(dpath / 'dpath1')
        """
        # Behave more like POSIX move to avoid potential confusing behavior
        if exists(dst):
            raise FileExistsError(
                'Moves are only allowed to locations that dont exist')
        import shutil
        copy_function = self._request_copy_function(
            follow_file_symlinks=follow_file_symlinks,
            follow_dir_symlinks=follow_dir_symlinks, meta=meta)
        real_dst = shutil.move(self, dst, copy_function=copy_function)
        return Path(real_dst)


def _parse_chmod_code(code):
    """
    Expand a chmod code into a list of actions.

    Args:
        code (str): of the form: [ugoa…][-+=]perms…[,…]
            perms is either zero or more letters from the set rwxXst, or a
            single letter from the set ugo.

    Yields:
        Tuple[str, str, str]: target, op, and perms.

            The target is modified by the operation using the value.
            target -- specified 'u' for user, 'g' for group, 'o' for other.
            op -- specified as '+' to add, '-' to remove, or '=' to assign.
            val -- specified as 'r' for read, 'w' for write, or 'x' for execute.

    Example:
        >>> from ubelt.util_path import _parse_chmod_code
        >>> print(list(_parse_chmod_code('ugo+rw,+r,g=rwx')))
        >>> print(list(_parse_chmod_code('o+x')))
        >>> print(list(_parse_chmod_code('u-x')))
        >>> print(list(_parse_chmod_code('x')))
        >>> print(list(_parse_chmod_code('ugo+rwx')))
        [('ugo', '+', 'rw'), ('ugo', '+', 'r'), ('g', '=', 'rwx')]
        [('o', '+', 'x')]
        [('u', '-', 'x')]
        [('u', '+', 'x')]
        [('ugo', '+', 'rwx')]
        >>> import pytest
        >>> with pytest.raises(ValueError):
        >>>     list(_parse_chmod_code('a+b+c'))
    """
    import re
    pat = re.compile(r'([\+\-\=])')
    parts = code.split(',')
    for part in parts:
        ab = pat.split(part)
        len_ab = len(ab)
        if len_ab == 3:
            targets, op, perms = ab
        elif len_ab == 1:
            perms = ab[0]
            op = '+'
            targets = 'u'
        else:
            raise ValueError('unknown chmod code pattern: part={part}')
        if targets == '' or targets == 'a':
            targets = 'ugo'
        yield (targets, op, perms)


def _resolve_chmod_code(old_mode, code):
    """
    Modifies integer stat permissions based on a string code.

    Args:
        old_mode (int): old mode from st_stat
        code (str): chmod style codeold mode from st_stat

    Returns:
        int : new code

    Example:
        >>> from ubelt.util_path import _resolve_chmod_code
        >>> print(oct(_resolve_chmod_code(0, '+rwx')))
        >>> print(oct(_resolve_chmod_code(0, 'ugo+rwx')))
        >>> print(oct(_resolve_chmod_code(0, 'a-rwx')))
        >>> print(oct(_resolve_chmod_code(0, 'u+rw,go+r,go-wx')))
        >>> print(oct(_resolve_chmod_code(0o777, 'u+rw,go+r,go-wx')))
        0o777
        0o777
        0o0
        0o644
        0o744
        >>> import pytest
        >>> with pytest.raises(NotImplementedError):
        >>>     print(oct(_resolve_chmod_code(0, 'u=rw')))
        >>> with pytest.raises(ValueError):
        >>>     _resolve_chmod_code(0, 'u?w')
    """
    import stat
    import itertools as it
    action_lut = {
        # TODO: handle suid, sgid, and sticky?
        # suid = stat.S_ISUID
        # sgid = stat.S_ISGID
        # sticky = stat.S_ISVTX
        'ur' : stat.S_IRUSR,
        'uw' : stat.S_IWUSR,
        'ux' : stat.S_IXUSR,

        'gr' : stat.S_IRGRP,
        'gw' : stat.S_IWGRP,
        'gx' : stat.S_IXGRP,

        'or' : stat.S_IROTH,
        'ow' : stat.S_IWOTH,
        'ox' : stat.S_IXOTH,
    }
    actions = _parse_chmod_code(code)
    new_mode = int(old_mode)  # (could optimize to modify inplace if needed)
    for action in actions:
        targets, op, perms = action
        try:
            action_keys = (target + perm for target, perm in it.product(targets, perms))
            action_values = (action_lut[key] for key in action_keys)
            action_values = list(action_values)
            if op == '+':
                for val in action_values:
                    new_mode |= val
            elif op == '-':
                for val in action_values:
                    new_mode &= (~val)
            elif op == '=':
                raise NotImplementedError(f'new chmod code for op={op}')
            else:
                raise AssertionError(
                    f'should not be able to get here. unknown op code: op={op}')
        except KeyError:
            # Give a better error message if something goes wrong
            raise ValueError(f'Unknown action: {action}')
    return new_mode


def _encode_chmod_int(int_code):
    """
    Convert a chmod integer code to a string

    Currently unused, but may be useful in the future.

    Example:
        >>> from ubelt.util_path import _encode_chmod_int
        >>> int_code = 0o744
        >>> print(_encode_chmod_int(int_code))
        u=rwx,g=r,o=r
    """
    import stat
    action_lut = {
        'ur' : stat.S_IRUSR,
        'uw' : stat.S_IWUSR,
        'ux' : stat.S_IXUSR,

        'gr' : stat.S_IRGRP,
        'gw' : stat.S_IWGRP,
        'gx' : stat.S_IXGRP,

        'or' : stat.S_IROTH,
        'ow' : stat.S_IWOTH,
        'ox' : stat.S_IXOTH,
    }
    from collections import defaultdict
    target_to_perms = defaultdict(list)
    for key, val in action_lut.items():
        target, perm = key
        if int_code & val:
            target_to_perms[target].append(perm)
    parts = [k + '=' + ''.join(vs) for k, vs in target_to_perms.items()]
    code = ','.join(parts)
    return code


if sys.version_info[0:2] < (3, 8):  # nocover

    # Vendor in a nearly modern copytree for Python 3.6 and 3.7
    def _compat_copytree(src, dst, symlinks=False, ignore=None,
                         copy_function=None, ignore_dangling_symlinks=False,
                         dirs_exist_ok=False):
        """
        A vendored shutil.copytree for older pythons based on the 3.10
        implementation
        """
        from shutil import Error, copystat, copy2, copy
        with os.scandir(src) as itr:
            entries = list(itr)

        if ignore is not None:
            ignored_names = ignore(os.fspath(src), [x.name for x in entries])
        else:
            ignored_names = set()

        os.makedirs(dst, exist_ok=dirs_exist_ok)
        errors = []
        use_srcentry = copy_function is copy2 or copy_function is copy

        for srcentry in entries:
            if srcentry.name in ignored_names:
                continue
            srcname = os.path.join(src, srcentry.name)
            dstname = os.path.join(dst, srcentry.name)
            srcobj = srcentry if use_srcentry else srcname
            try:
                is_symlink = srcentry.is_symlink()
                if is_symlink and os.name == 'nt':
                    # Special check for directory junctions, which appear as
                    # symlinks but we want to recurse.
                    # Not available on 3.6, use our impl instead
                    # lstat = srcentry.stat(follow_symlinks=False)
                    # if lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    #   is_symlink = False
                    from ubelt._win32_links import _win32_is_junction
                    if _win32_is_junction(srcentry):
                        is_symlink = False
                if is_symlink:
                    linkto = os.readlink(srcname)
                    if symlinks:
                        # We can't just leave it to `copy_function` because legacy
                        # code with a custom `copy_function` may rely on copytree
                        # doing the right thing.
                        os.symlink(linkto, dstname)
                        copystat(srcobj, dstname, follow_symlinks=not symlinks)
                    else:
                        # ignore dangling symlink if the flag is on
                        if not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        # otherwise let the copy occur. copy2 will raise an error
                        if srcentry.is_dir():
                            _compat_copytree(srcobj, dstname, symlinks, ignore,
                                             copy_function,
                                             dirs_exist_ok=dirs_exist_ok)
                        else:
                            copy_function(srcobj, dstname)
                elif srcentry.is_dir():
                    _compat_copytree(srcobj, dstname, symlinks, ignore,
                                     copy_function,
                                     dirs_exist_ok=dirs_exist_ok)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    copy_function(srcobj, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            copystat(src, dst)
        except OSError as why:
            # Copying file access times may fail on Windows
            if getattr(why, 'winerror', None) is None:
                errors.append((src, dst, str(why)))
        if errors:
            raise Error(errors)
        return dst
