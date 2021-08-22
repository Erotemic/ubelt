# -*- coding: utf-8 -*-
"""
The goal of this module is to provide an idiomatic cross-platform pattern of
accessing platform dependent file systems.

Standard application directory structure: cache, config, and other XDG
standards [1]_. This is similar to the more focused :mod:`appdirs` module [5]_.
In the future ubelt may directly use :mod:`appdirs`.

Notes:
    Table mapping the type of directory to the system default environment
    variable.  Inspired by [2]_, [3]_, and [4]_.


.. code-block:: none

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
    .. [1] https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    .. [2] https://stackoverflow.com/questions/43853548/xdg-windows
    .. [3] https://stackoverflow.com/questions/11113974/cross-plat-path
    .. [4] https://github.com/harawata/appdirs#supported-directories
    .. [5] https://github.com/ActiveState/appdirs
    .. [6] https://stackoverflow.com/questions/43853548/xdg-windows
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import itertools as it
from os.path import exists, join, isdir, expanduser, normpath


__all__ = [
    'WIN32', 'LINUX', 'DARWIN', 'POSIX',
    'find_exe', 'find_path',
    'ensure_app_cache_dir', 'ensure_app_config_dir', 'ensure_app_data_dir',
    'get_app_cache_dir', 'get_app_config_dir', 'get_app_data_dir',
    'platform_cache_dir', 'platform_config_dir', 'platform_data_dir'
]

# References:
# https://stackoverflow.com/questions/446209/possible-values-from-sys-platform
WIN32  = sys.platform == 'win32'
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform == 'darwin'
POSIX = 'posix' in sys.builtin_module_names


PY2 = sys.version_info[0] == 2

if PY2:
    import six
    string_types = six.string_types
else:
    string_types = (str,)


def platform_data_dir():
    """
    Returns path for user-specific data files

    Returns:
        str : path to the data dir used by the current operating system
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
        str : path to the cahce dir used by the current operating system
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
        str : path to the cache dir used by the current operating system
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
        str : dpath - writable data directory for this application

    SeeAlso:
        :func:`ensure_app_data_dir`
    """
    dpath = join(platform_data_dir(), appname, *args)
    return dpath


def ensure_app_data_dir(appname, *args):
    """
    Calls :func:`get_app_data_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: the path to the ensured directory

    SeeAlso:
        :func:`get_app_data_dir`

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
        str : dpath - writable config directory for this application

    SeeAlso:
        :func:`ensure_app_config_dir`
    """
    dpath = join(platform_config_dir(), appname, *args)
    return dpath


def ensure_app_config_dir(appname, *args):
    """
    Calls :func:`get_app_config_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: the path to the ensured directory

    SeeAlso:
        :func:`get_app_config_dir`

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
        str: the path to the ensured directory

    Returns:
        str : dpath - writable cache directory for this application

    SeeAlso:
        :func:`ensure_app_cache_dir`
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Calls :func:`get_app_cache_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: the path to the ensured directory

    SeeAlso:
        :func:`get_app_cache_dir`

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    from ubelt import util_path
    dpath = get_app_cache_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def find_exe(name, multi=False, path=None):
    """
    Locate a command.

    Search your local filesystem for an executable and return the first
    matching file with executable permission.

    Args:
        name (str | PathLike): globstr of matching filename

        multi (bool, default=False):
            if True return all matches instead of just the first.

        path (str | PathLike | Iterable[str | PathLike], default=None):
            overrides the system PATH variable.

    Returns:
        str | List[str] | None: returns matching executable(s).

    SeeAlso:
        :func:`shutil.which` - which is available in Python 3.3+.

    Notes:
        This is essentially the ``which`` UNIX command

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
        >>> import ubelt as ub
        >>> assert not ub.find_exe('noexist', multi=False)
        >>> assert ub.find_exe('ping', multi=False) or ub.find_exe('ls', multi=False)
        >>> assert not ub.find_exe('noexist', multi=True)
        >>> assert ub.find_exe('ping', multi=True) or ub.find_exe('ls', multi=True)

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
        fname (str | PathLike): file name to match.
            If exact is False this may be a glob pattern

        path (str | Iterable[str | PathLike], default=None):
            list of directories to search either specified as an ``os.pathsep``
            separated string or a list of directories.  Defaults to environment
            PATH.

        exact (bool, default=False): if True, only returns exact matches.

    Yields:
        str: candidate - a path that matches ``name``

    Notes:
        Running with ``name=''`` (i.e. ``ub.find_path('')``) will simply yield all
        directories in your PATH.

    Notes:
        For recursive behavior set ``path=(d for d, _, _ in os.walk('.'))``,
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
    if isinstance(path, string_types):
        dpaths = path.split(os.pathsep)
    else:
        dpaths = path
    candidates = (join(dpath, name) for dpath in dpaths)
    if exact:
        if WIN32:  # nocover
            # on WIN32 allow ``name`` to omit the extension suffix by trying
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
