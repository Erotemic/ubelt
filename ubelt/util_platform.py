# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import normpath, expanduser, join, exists
import os
import sys

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')


def platform_resource_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.

    Returns:
        str : path to the resource dir used by the current operating system
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Roaming'
    elif LINUX:  # nocover
        dpath_ = '~/.config'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Application Support'
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
    if WIN32:  # nocover
        dpath_ = '~/AppData/Local'
    elif LINUX:  # nocover
        dpath_ = '~/.cache'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Caches'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def get_app_resource_dir(appname, *args):
    r"""
    Returns a writable directory for an application
    This should be used for persistent configuration files.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable resource directory for this application

    SeeAlso:
        ensure_app_resource_dir
    """
    dpath = join(platform_resource_dir(), appname, *args)
    return dpath


def ensure_app_resource_dir(appname, *args):
    """
    Calls `get_app_resource_dir` but ensures the directory exists.

    SeeAlso:
        get_app_resource_dir

    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_resource_dir(appname, *args)
    ensuredir(dpath)
    return dpath


def get_app_cache_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory for this application

    SeeAlso:
        ensure_app_cache_dir
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Calls `get_app_cache_dir` but ensures the directory exists.

    SeeAlso:
        get_app_cache_dir

    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_cache_dir(appname, *args)
    ensuredir(dpath)
    return dpath


def ensuredir(dpath, mode=0o1777, verbose=None):
    r"""
    Ensures that directory will exist. creates new dir with sticky bits by
    default

    Args:
        dpath (str): dir to ensure. Can also be a tuple to send to join
        mode (int): octal mode of directory (default 0o1777)
        verbose (int): verbosity (default 0)

    Returns:
        str: path - the ensured directory

    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> cache_dpath = ub.ensure_app_cache_dir('ubelt')
        >>> dpath = join(cache_dpath, 'ensuredir')
        >>> if exists(dpath):
        >>>     os.rmdir(dpath)
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
            print('[ubelt] mkdir(%r)' % dpath)
        try:
            os.makedirs(normpath(dpath), mode=mode)
        except OSError as ex:  # nocover
            print('Error in ensuredir')
            raise
    return dpath


def _run_process(proc):
    """ helper for cmd """
    while True:
        # returns None while subprocess is running
        retcode = proc.poll()
        line = proc.stdout.readline()
        yield line
        if retcode is not None:
            # The program has a return code, so its done executing.
            # Grab any remaining data in stdout
            for line in proc.stdout.readlines():
                yield line
            raise StopIteration('process finished')


def cmd(command, shell=False, detatch=False, verbose=False, verbout=None):
    r"""
    Trying to clean up cmd

    Args:
        command (str): bash-like command string or tuple of executable and args
        shell (bool): if True, process is run in shell
        detatch (bool): if True, process is detached and run in background.
        verbose (int): verbosity mode
        verbout (bool): if True, `command` writes to stdout in realtime.
            defaults to True iff verbose > 0. Note when detatch is True
            all stdout is lost.

    Returns:
        dict: info - information about command status.
            if detatch is False `info` contains captured standard out,
            standard error, and the return code
            if detatch is False `info` contains a reference to the process.

    CommandLine:
        python -m ubelt.util_platform cmd

    Doctest:
        >>> import ubelt as ub
        >>> from os.path import join, exists
        >>> verbose = 0
        >>> # ----
        >>> info = ub.cmd('echo str noshell', verbose=verbose)
        >>> assert info['out'].strip() == 'str noshell'
        >>> # ----
        >>> info = ub.cmd(('echo', 'tuple noshell'), verbose=verbose)
        >>> assert info['out'].strip() == 'tuple noshell'
        >>> # ----
        >>> info = ub.cmd('echo "str\n\nshell"', verbose=verbose, shell=True)
        >>> assert info['out'].strip() == 'str\n\nshell'
        >>> # ----
        >>> info = ub.cmd(('echo', 'tuple shell'), verbose=verbose, shell=True)
        >>> assert info['out'].strip() == 'tuple shell'
        >>> # ----
        >>> fpath1 = join(ub.get_app_cache_dir('ubelt'), 'cmdout1.txt')
        >>> fpath2 = join(ub.get_app_cache_dir('ubelt'), 'cmdout2.txt')
        >>> ub.delete(fpath1)
        >>> ub.delete(fpath2)
        >>> info = ub.cmd(('touch', fpath1), detatch=True)
        >>> info = ub.cmd('echo writing2 > ' + fpath2, shell=True, detatch=True)
        >>> while not exists(fpath1):
        >>>     pass
        >>> while not exists(fpath2):
        >>>     pass
        >>> assert ub.readfrom(fpath1) == ''
        >>> assert ub.readfrom(fpath2).strip() == 'writing2'

    # Doctest:
    #     >>> import ubelt as ub
    #     >>> info = ub.cmd('ping localhost -c 2', verbose=1)

    """
    import shlex
    import subprocess
    import pipes
    if verbout is None:
        verbout = verbose >= 1
    if verbose >= 2:  # nocover
        print('+=== START CMD ===')
        print('Command:')
        print(command)
        if verbout and not detatch:
            print('----')
            print('Stdout:')

    # When shell=True, args is a string sent to the shell (e.g. bin/sh)
    # When shell=False, args is a list of executable and arguments
    if shell:
        if isinstance(command, (list, tuple)):
            args = ' '.join(list(map(pipes.quote, command)))
        else:
            args = command
    else:
        if isinstance(command, (list, tuple)):
            args = command
        else:
            args = shlex.split(command, posix=not WIN32)
    # Create a new process to execute the command
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, shell=shell,
                            universal_newlines=True)
    if detatch:
        info = {'proc': proc}
        if verbose >= 2:  # nocover
            print('...detatching')
    else:
        write_fn = sys.stdout.write
        flush_fn = sys.stdout.flush
        logged_out = []
        for line in _run_process(proc):
            #line_ = line if six.PY2 else line.decode('utf-8')
            line_ = line if PY2 else line
            if len(line_) > 0:
                if verbout:  # nocover
                    write_fn(line_)
                    flush_fn()
                logged_out.append(line)
        try:
            out = ''.join(logged_out)
        except UnicodeDecodeError:  # nocover
            out = '\n'.join(_.decode('utf-8') for _ in logged_out)
        (out_, err) = proc.communicate()
        ret = proc.wait()
        info = {
            'out': out,
            'err': err,
            'ret': ret,
        }
        if verbose >= 2:  # nocover
            print('L___ END CMD ___')
    return info


def startfile(fpath, verbose=True):  # nocover
    """
    Uses default program defined by the system to open a file.

    Args:
        fpath (str): a file to open using the program associated with the
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
    import pipes
    if verbose:
        print('[ubelt] startfile("{}")'.format(fpath))
    fpath = normpath(fpath)
    if not exists(fpath):
        raise Exception('Cannot start nonexistant file: %r' % fpath)
    if not WIN32:
        fpath = pipes.quote(fpath)
    if LINUX:
        info = cmd(('xdg-open', fpath), detatch=True, verbose=verbose)
    elif DARWIN:
        info = cmd(('open', fpath), detatch=True, verbose=verbose)
    elif WIN32:
        os.startfile(fpath)
        info = None
    else:
        raise RuntimeError('Unknown Platform')
    if info is not None:
        if not info['proc']:
            raise Exception('startfile failed')


def editfile(fpath, verbose=True):  # nocover
    """
    Opens a file or python module in your preferred visual editor.

    Your preferred visual editor is gvim... unless you specify one using the
    VISUAL environment variable. This function is extremely useful in an
    IPython development environment.

    Args:
        fpath (str): a file path or python module / function
        verbose (int): verbosity

    DisableExample:
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> ub.editfile(ub.util_test.__file__)
        >>> ub.editfile(ub)
        >>> ub.editfile(ub.editfile)
    """
    import six
    if not isinstance(fpath, six.string_types):
        from six import types
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

    if not exists(fpath):
        raise IOError('Cannot start nonexistant file: %r' % fpath)
    cmd([editor, fpath], fpath, detatch=True)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
