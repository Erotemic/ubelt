# -*- coding: utf-8 -*-
"""
The goal of this module is to provide an idomatic cross-platform pattern of
accessing platform dependant file systems.

Standard application directory structure: cache, config, and other XDG
standards [1].

Notes:
    Table mapping the type of directory to the system default environment variable.
    Inspired by [2,3,4].

           | Linux            | Win32          |   Darwin
    data   | $XDG_DATA_HOME   | %APPDATA%      | ~/Library/Application Support
    config | $XDG_CONFIG_HOME | %APPDATA%      | ~/Library/Application Support
    cache  | $XDG_CACHE_HOME  | %LOCALAPPDATA% | ~/Library/Caches


    If an environment variable is not specified the defaults are:
        APPDATA      = ~/AppData/Roaming
        LOCALAPPDATA = ~/AppData/Local

        XDG_DATA_HOME   = ~/.local/share
        XDG_CACHE_HOME  = ~/.cache
        XDG_CONFIG_HOME = ~/.config

References:
    ..[1] https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    ..[2] https://stackoverflow.com/questions/43853548/xdg-windows
    ..[3] https://stackoverflow.com/questions/11113974/cross-plat-path
    ..[4] https://github.com/harawata/appdirs#supported-directories

"""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import six
import itertools as it
from os.path import exists, join, isdir, expanduser, normpath


# References:
# https://stackoverflow.com/questions/446209/possible-values-from-sys-platform
WIN32  = sys.platform == 'win32'
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform == 'darwin'
POSIX = 'posix' in sys.builtin_module_names


def platform_data_dir():
    """
    Returns path for user-specific data files

    Returns:
        PathLike : path to the data dir used by the current operating system
    """
    if LINUX:  # nocover
        dpath_ = os.environ.get('XDG_DATA_HOME', '~/.local/share')
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Application Support'
    elif WIN32:  # nocover
        dpath_ = os.environ.get('APPDATA', '~/AppData/Roaming')
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def platform_config_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.

    Returns:
        PathLike : path to the cahce dir used by the current operating system
    """
    if LINUX:  # nocover
        dpath_ = os.environ.get('XDG_CONFIG_HOME', '~/.config')
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Application Support'
    elif WIN32:  # nocover
        dpath_ = os.environ.get('APPDATA', '~/AppData/Roaming')
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def platform_cache_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for temporary deletable data.

    Returns:
        PathLike : path to the cache dir used by the current operating system
    """
    if LINUX:  # nocover
        dpath_ = os.environ.get('XDG_CACHE_HOME', '~/.cache')
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Caches'
    elif WIN32:  # nocover
        dpath_ = os.environ.get('LOCALAPPDATA', '~/AppData/Local')
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath

# ---


def get_app_data_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        PathLike: dpath: writable data directory for this application

    SeeAlso:
        ensure_app_data_dir
    """
    dpath = join(platform_data_dir(), appname, *args)
    return dpath


def ensure_app_data_dir(appname, *args):
    """
    Calls `get_app_data_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    SeeAlso:
        get_app_data_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_data_dir('ubelt')
        >>> assert exists(dpath)
    """
    from ubelt import util_path
    dpath = get_app_data_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def get_app_config_dir(appname, *args):
    r"""
    Returns a writable directory for an application
    This should be used for persistent configuration files.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        PathLike: dpath: writable config directory for this application

    SeeAlso:
        ensure_app_config_dir
    """
    dpath = join(platform_config_dir(), appname, *args)
    return dpath


def ensure_app_config_dir(appname, *args):
    """
    Calls `get_app_config_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    SeeAlso:
        get_app_config_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_config_dir('ubelt')
        >>> assert exists(dpath)
    """
    from ubelt import util_path
    dpath = get_app_config_dir(appname, *args)
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
        PathLike: dpath: writable cache directory for this application

    SeeAlso:
        ensure_app_cache_dir
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Calls `get_app_cache_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    SeeAlso:
        get_app_cache_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    from ubelt import util_path
    dpath = get_app_cache_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def startfile(fpath, verbose=True):  # nocover
    """
    Uses default program defined by the system to open a file.
    This is done via `os.startfile` on windows, `open` on mac, and `xdg-open`
    on linux.

    Args:
        fpath (PathLike): a file to open using the program associated with the
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
    from ubelt import util_cmd
    if verbose:
        print('[ubelt] startfile("{}")'.format(fpath))
    fpath = normpath(fpath)
    if not exists(fpath):
        raise Exception('Cannot start nonexistant file: %r' % fpath)
    if not WIN32:
        import pipes
        fpath = pipes.quote(fpath)
    if LINUX:
        info = util_cmd.cmd(('xdg-open', fpath), detach=True, verbose=verbose)
    elif DARWIN:
        info = util_cmd.cmd(('open', fpath), detach=True, verbose=verbose)
    elif WIN32:
        os.startfile(fpath)
        info = None
    else:
        raise RuntimeError('Unknown Platform')
    if info is not None:
        if not info['proc']:
            raise Exception('startfile failed')


def find_exe(name, multi=False, path=None):
    """
    Locate a command.

    Search your local filesystem for an executable and return the first
    matching file with executable permission.

    Args:
        name (str): globstr of matching filename

        multi (bool): if True return all matches instead of just the first.
            Defaults to False.

        path (str or Iterable[PathLike]): overrides the system PATH variable.

    Returns:
        PathLike or List[PathLike] or None: returns matching executable(s).

    SeeAlso:
        shutil.which - which is available in Python 3.3+.

    Notes:
        This is essentially the `which` UNIX command

    References:
        https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
        https://docs.python.org/dev/library/shutil.html#shutil.which

    Example:
        >>> find_exe('ls')
        >>> find_exe('ping')
        >>> assert find_exe('which') == find_exe(find_exe('which'))
        >>> find_exe('which', multi=True)
        >>> find_exe('ping', multi=True)
        >>> find_exe('cmake', multi=True)
        >>> find_exe('nvcc', multi=True)
        >>> find_exe('noexist', multi=True)

    Example:
        >>> assert not find_exe('noexist', multi=False)
        >>> assert find_exe('ping', multi=False)
        >>> assert not find_exe('noexist', multi=True)
        >>> assert find_exe('ping', multi=True)

    Benchmark:
        >>> # xdoctest: +IGNORE_WANT
        >>> import ubelt as ub
        >>> import shutil
        >>> for timer in ub.Timerit(100, bestof=10, label='ub.find_exe'):
        >>>     ub.find_exe('which')
        >>> for timer in ub.Timerit(100, bestof=10, label='shutil.which'):
        >>>     shutil.which('which')
        Timed best=58.71 µs, mean=59.64 ± 0.96 µs for ub.find_exe
        Timed best=72.75 µs, mean=73.07 ± 0.22 µs for shutil.which
    """
    candidates = find_path(name, path=path, exact=True)
    mode = os.X_OK | os.F_OK
    results = (fpath for fpath in candidates
               if os.access(fpath, mode) and not isdir(fpath))
    if not multi:
        for fpath in results:
            return fpath
    else:
        return list(results)


def find_path(name, path=None, exact=False):
    """
    Search for a file or directory on your local filesystem by name
    (file must be in a directory specified in a PATH environment variable)

    Args:
        fname (PathLike or str): file name to match.
            If exact is False this may be a glob pattern

        path (str or Iterable[PathLike]): list of directories to search either
            specified as an os.pathsep separated string or a list of
            directories.  Defaults to environment PATH.

        exact (bool, default=False): if True, only returns exact matches.

    Yields:
        PathLike: candidate: a path that matches `name`

    Notes:
        Running with `name=''` (i.e. `ub.find_path('')`) will simply yield all
        directories in your PATH.

    Notes:
        For recursive behavior set `path=(d for d, _, _ in os.walk('.'))`,
        where '.' might be replaced by the root directory of interest.

    Example:
        >>> list(find_path('ping', exact=True))
        >>> list(find_path('bin'))
        >>> list(find_path('bin'))
        >>> list(find_path('*cc*'))
        >>> list(find_path('cmake*'))

    Example:
        >>> import ubelt as ub
        >>> from os.path import dirname
        >>> path = dirname(dirname(ub.util_platform.__file__))
        >>> res = sorted(find_path('ubelt/util_*.py', path=path))
        >>> assert len(res) >= 10
        >>> res = sorted(find_path('ubelt/util_platform.py', path=path, exact=True))
        >>> print(res)
        >>> assert len(res) == 1
    """
    if path is None:
        path = os.environ.get('PATH', os.defpath)
    if isinstance(path, six.string_types):
        dpaths = path.split(os.pathsep)
    else:
        dpaths = path
    candidates = (join(dpath, name) for dpath in dpaths)
    if exact:
        if WIN32:  # nocover
            # on WIN32 allow `name` to omit the extension suffix by trying
            # to match with all possible "valid" suffixes specified by PATHEXT
            pathext = [''] + os.environ.get('PATHEXT', '').split(os.pathsep)
            candidates = (p + ext for p in candidates for ext in pathext)
        candidates = filter(exists, candidates)
    else:
        import glob
        candidates = it.chain.from_iterable(
            glob.glob(pattern) for pattern in candidates)

    for candidate in candidates:
        yield candidate


# DEPRICATED:


def editfile(fpath, verbose=True):  # nocover
    """
    DEPRICATED: This has been ported to xdev, please use that version.

    Opens a file or code corresponding to a live python object in your
    preferred visual editor. This function is mainly useful in an interactive
    IPython session.

    The visual editor is determined by the `VISUAL` environment variable.  If
    this is not specified it defaults to gvim.

    Args:
        fpath (PathLike): a file path or python module / function
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
    import warnings
    warnings.warn('Please use xdev.editfile instead', DeprecationWarning)
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
    if not ub.find_exe(editor):
        warnings.warn('Cannot find visual editor={}'.format(editor), UserWarning)
        # Try and fallback on commonly installed editor
        alt_candidates = [
            'gedit',
            'TextEdit'
            'Notepad',
        ]
        for cand in alt_candidates:
            if ub.find_exe(cand):
                editor = cand

    if not exists(fpath):
        raise IOError('Cannot start nonexistant file: %r' % fpath)
    ub.cmd([editor, fpath], fpath, detach=True)


def platform_resource_dir():  # nocover
    """
    Alias for platform_cache_dir

    DEPRICATED in favor of platform_config_dir / platform_data_dir

    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.

    Returns:
        PathLike : path to the resource dir used by the current operating system
    """
    return platform_cache_dir()


def get_app_resource_dir(appname, *args):  # nocover
    r"""
    Returns a writable directory for an application
    This should be used for persistent configuration files.

    DEPRICATED in favor of get_app_config_dir / get_app_data_dir

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        PathLike: dpath: writable resource directory for this application

    SeeAlso:
        ensure_app_resource_dir
    """
    return get_app_cache_dir(appname, *args)


def ensure_app_resource_dir(appname, *args):  # nocover
    """
    Calls `get_app_resource_dir` but ensures the directory exists.

    DEPRICATED in favor of ensure_app_config_dir / ensure_app_data_dir

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    SeeAlso:
        get_app_resource_dir
    """
    return ensure_app_cache_dir(appname, *args)
