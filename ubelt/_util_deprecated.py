"""
This file contains functions to be deprecated, but are still accessible.
"""
import os
import sys
import warnings
from os.path import exists, abspath, expanduser, expandvars, normpath, realpath
from ubelt import util_const
from .util_platform import (
    get_app_cache_dir, platform_cache_dir, ensure_app_cache_dir, WIN32, LINUX,
    DARWIN)

__all__ = [
    'dict_take', 'editfile', 'compressuser', 'dict_take', 'editfile',
    'ensure_app_resource_dir', 'get_app_resource_dir', 'platform_resource_dir',
    'schedule_deprecation', 'startfile', 'truepath'
]


PY2 = sys.version_info[0] == 2

if PY2:
    import six
    string_types = six.string_types
else:
    string_types = (str,)


DEP_SCHEDULE_1 = dict(deprecate='0.9.6', remove='1.0.0')


def schedule_deprecation(deprecate=None, error=None, remove=None):  # nocover
    """
    Deprecation machinery to help provide users with a smoother transition
    """
    import ubelt as ub
    from distutils.version import LooseVersion
    current = LooseVersion(ub.__version__)
    deprecate = None if deprecate is None else LooseVersion(deprecate)
    remove = None if remove is None else LooseVersion(remove)
    error = None if error is None else LooseVersion(error)

    if deprecate is None or current >= deprecate:
        import inspect
        prev_frame = inspect.currentframe().f_back
        # the_class = prev_frame.f_locals["self"].__class__
        caller = prev_frame.f_code.co_name
        # the_method = prev_frame.f_code.co_name
        # stack = inspect.stack()
        # the_class = stack[1][0].f_locals["self"].__class__.__name__
        # the_method = stack[1][0].f_code.co_name
        # caller = str(str(inspect.currentframe())).split(' ')[-1][:-1]
        msg = ub.paragraph(
            '''
            The "{caller}" function was deprecated in {deprecate}, will cause
            an error in {error} and will be removed in {remove}. The current
            version is {current}.
            ''').format(**locals())
        if remove is not None and current >= remove:
            raise AssertionError('forgot to remove a deprecated function')
        if error is not None and current >= error:
            raise DeprecationWarning(msg)
        else:
            warnings.warn(msg, DeprecationWarning)


# DEPRICATED:


def truepath(path, real=False):
    """
    Normalizes a string representation of a path and does shell-like expansion.

    Args:
        path (str | PathLike): string representation of a path
        real (bool): if True, all symbolic links are followed. (default: False)

    Returns:
        str : normalized path

    Note:
        This function is similar to the composition of expanduser, expandvars,
        normpath, and (realpath if `real` else abspath). However, on windows
        backslashes are then replaced with forward slashes to offer a
        consistent unix-like experience across platforms.

        On windows expanduser will expand environment variables formatted as
        %name%, whereas on unix, this will not occur.

    Example:
        >>> from os.path import join
        >>> import ubelt as ub
        >>> assert ub.truepath('~/foo') == join(ub.userhome(), 'foo')
        >>> assert ub.truepath('~/foo') == ub.truepath('~/foo/bar/..')
        >>> assert ub.truepath('~/foo', real=True) == ub.truepath('~/foo')
    """
    schedule_deprecation(**DEP_SCHEDULE_1)
    path = expanduser(path)
    path = expandvars(path)
    if real:
        path = realpath(path)
    else:
        path = abspath(path)
    path = normpath(path)
    return path


def compressuser(path, home='~'):  # nocover
    """
    Inverse of :func:`os.path.expanduser`.

    Args:
        path (str | PathLike): path in system file structure
        home (str, default='~'): symbol used to replace the home path.
            Defaults to '~', but you might want to use '$HOME' or
            '%USERPROFILE%' instead.

    Returns:
        str: path: shortened path replacing the home directory with a tilde

    Example:
        >>> from os.path import join
        >>> path = expanduser('~')
        >>> assert path != '~'
        >>> assert compressuser(path) == '~'
        >>> assert compressuser(path + '1') == path + '1'
        >>> assert compressuser(path + '/1') == join('~', '1')
        >>> assert compressuser(path + '/1', '$HOME') == join('$HOME', '1')
    """
    from ubelt import userhome
    schedule_deprecation(**DEP_SCHEDULE_1)
    path = normpath(path)
    userhome_dpath = userhome()
    if path.startswith(userhome_dpath):
        if len(path) == len(userhome_dpath):
            path = home
        elif path[len(userhome_dpath)] == os.path.sep:
            path = home + path[len(userhome_dpath):]
    return path


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

    Example:
        >>> # xdoctest: +SKIP
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> ub.editfile(ub.util_platform.__file__)
        >>> ub.editfile(ub)
        >>> ub.editfile(ub.editfile)
    """
    from six import types
    import ubelt as ub
    import warnings
    schedule_deprecation(**DEP_SCHEDULE_1)
    warnings.warn('Please use xdev.editfile instead', DeprecationWarning)
    if not isinstance(fpath, string_types):
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
            # 'todo vscode',
            # 'todo atom',
            # 'todo sublime',
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
    schedule_deprecation(**DEP_SCHEDULE_1)
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
    schedule_deprecation(**DEP_SCHEDULE_1)
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
    schedule_deprecation(**DEP_SCHEDULE_1)
    return ensure_app_cache_dir(appname, *args)


def startfile(fpath, verbose=True):  # nocover
    """
    Uses default program defined by the system to open a file.
    This is done via `os.startfile` on windows, `open` on mac, and `xdg-open`
    on linux.

    Args:
        fpath (str | PathLike): a file to open using the program associated with the
            files extension type.
        verbose (int): verbosity

    References:
        http://stackoverflow.com/questions/2692873/quote-posix

    Example:
        >>> # xdoctest: +SKIP
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> base = ub.ensure_app_cache_dir('ubelt')
        >>> fpath1 = join(base, 'test_open.txt')
        >>> ub.touch(fpath1)
        >>> proc = ub.startfile(fpath1)
    """
    schedule_deprecation(**DEP_SCHEDULE_1)
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


def dict_take(dict_, keys, default=util_const.NoParam):
    r"""
    Generates values from a dictionary

    Args:
        dict_ (Mapping): a dictionary to take from
        keys (Iterable): the keys to take
        default (object, optional): if specified uses default if keys are missing

    Example:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> result = list(ub.dict_take(dict_, keys, None))
        >>> assert result == ['a', 'b', 'c', None, None]

    Example:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> try:
        >>>     print(list(ub.dict_take(dict_, keys)))
        >>>     raise AssertionError('did not get key error')
        >>> except KeyError:
        >>>     print('correctly got key error')
    """
    schedule_deprecation(**DEP_SCHEDULE_1)
    if default is util_const.NoParam:
        for key in keys:
            yield dict_[key]
    else:
        for key in keys:
            yield dict_.get(key, default)
