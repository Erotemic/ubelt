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

The :func:`expandpath` function expands the tilde to $HOME and environment
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
from ubelt import util_io
import pathlib
import warnings


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
        >>> import ubelt as ub
        >>> import getpass
        >>> username = getpass.getuser()
        >>> userhome_target = expanduser('~')
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
        >>> cache_dpath = ub.Path.appdir('ubelt').ensuredir()
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

    Note:
        This class will be DEPRECATED. The exact deprecation version and
        mitigation plan has not yet been developed.

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
        import ubelt as ub
        ub.schedule_deprecation(
            modname='ubelt',
            migration='Use tempfile instead', name='TempDir',
            type='class', deprecate='1.2.0', error='1.4.0',
            remove='1.5.0',
        )
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

        * :py:meth:`pathlib.Path.chmod`
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
                Text placed between the stem and extension. Default to ''.
                Note: this is just called suffix in :func:`ub.augpath`.

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

            suffix (str):
                DEPRECAETD

        SeeAlso:
            :py:meth:`pathlib.Path.with_stem`
            :py:meth:`pathlib.Path.with_name`
            :py:meth:`pathlib.Path.with_suffix`

        Returns:
            Path: augmented path

        Note:
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

            p.name
            p.stem
            p.suffixes
            p.parts

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
                deprecate='1.1.3', remove='2.0.0',
                migration='Use stemsuffix instead',
            )
            if not stemsuffix:
                stemsuffix = suffix
            import warnings
            warnings.warn(
                'DEVELOPER NOTICE: The ubelt.Path.augment function may '
                'experience a BACKWARDS INCOMPATIBLE update in the future '
                'having to do with the suffix argument to ub.Path.augment '
                'To avoid any issue use the ``ubelt.augment`` function '
                'instead for now. If you see this warning, please make an '
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

        Returns:
            Path: returns itself

        Example:
            >>> import ubelt as ub
            >>> cache_dpath = ub.Path.appdir('ubelt').ensuredir()
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

    def mkdir(self, mode=511, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.

        Note:
            The ubelt variant is the same, except it returns the path as well.

        Args:
            mode (int) : perms
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

    def ls(self):
        """
        A convenience function to list all paths in a directory.

        This is simply a wraper around iterdir that returns the results as a
        list instead of a generator. This is mainly for faster navigation in
        IPython. In production code `iterdir` should be used instead.

        Returns:
            List[Path]

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
        """
        return list(self.iterdir())

    def shrinkuser(self, home='~'):
        """
        Shrinks your home dir by replacing it with a tilde.

        This is the inverse of :func:`os.path.expanduser`.

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

            onerror (Callable[[OSError], None]):
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
        Test if the fspath representation endswith a particular string

        Allows ubelt.Path to be a better drop-in replacement when working with
        string-based paths.

        Args:
            suffix (str | Tuple[str, ...]):
                One or more suffixes to test for

            *args:
                start (int): if specified begin testing at this position.
                end (int): if specified stop testing at this position.

        Returns:
            bool: True if any of the suffixes are matched.

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
        Test if the fspath representation startswith a particular string

        Allows ubelt.Path to be a better drop-in replacement when working with
        string-based paths.

        Args:
            prefix (str | Tuple[str, ...]):
                One or more prefixes to test for

            *args:
                start (int): if specified begin testing at this position.
                end (int): if specified stop testing at this position.

        Returns:
            bool: True if any of the prefixes are matched.

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

            +----------+------------------------+------------------------+------------+
            | dst      | dir                    | file                   | no-exist   |
            +----------+                        |                        |            |
            | src      |                        |                        |            |
            +==========+========================+========================+============+
            | dir      | error-or-overwrite-dst | error                  | dst        |
            +----------+------------------------+------------------------+------------+
            | file     | dst / src.name         | error-or-overwrite-dst | dst        |
            +----------+------------------------+------------------------+------------+
            | no-exist | error                  | error                  | error      |
            +----------+------------------------+------------------------+------------+

        In general, the contents of src will be the contents of dst, except for
        the one case where a file is copied into an existing directory. In this
        case the name is used to construct a fully qualified destination.

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
            print(piv.to_markdown(tablefmt="presto"))
            print(piv.to_markdown(tablefmt="pretty", index=True))
            print(piv.to_markdown(tablefmt="grid", index=True))

        Args:
            dst (str | PathLike):
                if `src` is a file and `dst` does not exist, copies this to `dst`
                if `src` is a file and `dst` is a directory, copies this to `dst / src.name`

                if `src` is a directory and `dst` does not exist, copies this to `dst`
                if `src` is a directory and `dst` is a directory, errors unless
                overwrite is True, in which case, copies this to `dst` and
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
            Path: where the path was actually copied to

        Note:
            This is implemented with a combination of :func:`shutil.copy`,
            :func:`shutil.copy2`, and :func:`shutil.copytree`, but the The
            defaults and behavior here are noticably different (and hopefully
            safer and more intuitive).

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
            import xdev
            xdev.tree_repr(dpath)
            xdev.tree_repr(clone0, max_files=10)
            xdev.tree_repr(clone1, max_files=10)
        """
        warnings.warn('The ub.Path.copy function is experimental and may change, '
                      'in corner cases. Primary cases seem stable.')
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
            raise Exception
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
            error if it would overwrite any data. If you want an overwriting
            variant of move we recommend you either either copy the data, and
            then delete the original (potentially inefficient), or use
            :func:`shutil.move` directly if you know how :func:`os.rename`
            works on your system.

        Returns:
            Path: where the path was actually moved to

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
            >>> # xdev.tree_repr(dpath, max_files=10)
            >>> paths['dpath0'].move(dpath / 'dpath1')
            >>> # xdev.tree_repr(dpath, max_files=10)

        Ignore:
            import xdev
            xdev.tree_repr(dpath)
        """
        warnings.warn('The ub.Path.move function is experimental and may change! '
                      'Do not rely on this behavior yet!')

        # Behave more like POSIX move to avoid potential confusing behavior
        if exists(dst):
            raise FileExistsError(
                'Moves are only allowed to locations that dont exist')
        # if os.path.isdir(dst):
        #     with os.scandir(dst) as itr:
        #         is_empty = next(itr, None) is None
        #     if not is_empty:
        #         raise IOError(f'Cannot move {self!r} to {dst!r}. '
        #                       'Directory not empty')

        import shutil
        copy_function = self._request_copy_function(
            follow_file_symlinks=follow_file_symlinks,
            follow_dir_symlinks=follow_dir_symlinks, meta=meta)
        real_dst = shutil.move(self, dst, copy_function=copy_function)
        return Path(real_dst)

if sys.version_info[0:2] < (3, 8):  # nocover

    # Vendor in a nearly modern copytree for Python 3.6 and 3.7
    def _compat_copytree(src, dst, symlinks=False, ignore=None,
                         copy_function=None, ignore_dangling_symlinks=False,
                         dirs_exist_ok=False):
        """
        A vendored shutil.copytree for older pythons based on the 3.10
        implementation
        """
        # import stat
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
