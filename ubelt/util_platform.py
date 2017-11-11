# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import normpath, expanduser, join, exists
import os
import sys
import getpass
import pipes
import platform
import shlex
import six
import subprocess
# import itertools as it
from six.moves import zip_longest
from threading  import Thread
if six.PY2:
    import Queue as queue
else:
    import queue

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')
POSIX = 'posix' in sys.builtin_module_names


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
            print('[ubelt] mkdir(%r)' % dpath)
        try:
            os.makedirs(normpath(dpath), mode=mode)
        except OSError:  # nocover
            raise
    return dpath


# def _run_process(proc):
#     """ helper for cmd """
#     while True:
#         # returns None while subprocess is running
#         retcode = proc.poll()
#         line = proc.stdout.readline()
#         yield line
#         if retcode is not None:
#             # The program has a return code, so its done executing.
#             # Grab any remaining data in stdout
#             for line in proc.stdout.readlines():
#                 yield line
#             raise StopIteration('process finished')


def _textio_iterlines(stream):
    """
    Iterates over lines in a TextIO stream until an EOF is encountered.
    This is the iterator version of stream.readlines()
    """
    line = stream.readline()
    while line != '':
        yield line
        line = stream.readline()


def _proc_async_iter_stream(proc, stream, buffersize=10):
    """
    Reads output from a process in a separate thread
    """
    def enqueue_output(proc, stream, stream_queue):
        while proc.poll() is None:
            line = stream.readline()
            # print('ENQUEUE LIVE {!r} {!r}'.format(stream, line))
            stream_queue.put(line)

        for line in _textio_iterlines(stream):
            # print('ENQUEUE FINAL {!r} {!r}'.format(stream, line))
            stream_queue.put(line)

        # print("STREAM IS DONE {!r}".format(stream))
        stream_queue.put(None)  # signal that the stream is finished
        # stream.close()
    stream_queue = queue.Queue(maxsize=buffersize)
    _thread = Thread(target=enqueue_output, args=(proc, stream, stream_queue))
    _thread.daemon = True  # thread dies with the program
    _thread.start()
    return stream_queue


def _proc_iteroutput_thread(proc):
    """
    Iterates over output from a process line by line

    Yields:
        tuple[(str, str)]: oline, eline: stdout and stderr line

    References:
        https://stackoverflow.com/questions/375427/non-blocking-read-subproc
    """

    # Create threads that read stdout / stderr and queue up the output
    stdout_queue = _proc_async_iter_stream(proc, proc.stdout)
    stderr_queue = _proc_async_iter_stream(proc, proc.stderr)

    stdout_live = True
    stderr_live = True

    # read from the output asychronously until
    while stdout_live or stderr_live:
        if stdout_live:
            try:
                oline = stdout_queue.get_nowait()
                stdout_live = oline is not None
            except queue.Empty:
                oline = None
        if stderr_live:
            try:
                eline = stderr_queue.get_nowait()
                stderr_live = eline is not None
            except queue.Empty:
                eline = None
        if oline is not None or eline is not None:
            yield oline, eline


def _proc_iteroutput_select(proc):  # nocover
    """
    Iterates over output from a process line by line

    UNIX only. Use `_proc_iteroutput_thread` instead for a cross platform
    solution based on threads.

    Yields:
        tuple[(str, str)]: oline, eline: stdout and stderr line
    """
    # Read output while the external program is running
    import select
    while proc.poll() is None:
        reads = [proc.stdout.fileno(), proc.stderr.fileno()]
        ret = select.select(reads, [], [])
        oline = eline = None
        for fd in ret[0]:
            if fd == proc.stdout.fileno():
                oline = proc.stdout.readline()
            if fd == proc.stderr.fileno():
                eline = proc.stderr.readline()
        yield oline, eline

    # Grab any remaining data in stdout and stderr after the process finishes
    oline_iter = _textio_iterlines(proc.stdout)
    eline_iter = _textio_iterlines(proc.stderr)
    for oline, eline in zip_longest(oline_iter, eline_iter):
        yield oline, eline


def _proc_tee_output(proc, stdout=None, stderr=None):
    """
    Simultaniously reports and captures stdout and stderr from a process

    subprocess must be created using (stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
    """
    logged_out = []
    logged_err = []
    _proc_iteroutput = _proc_iteroutput_thread
    for oline, eline in _proc_iteroutput(proc):
        if oline:
            if stdout:
                stdout.write(oline)
                stdout.flush()
            logged_out.append(oline)
        if eline:
            if stderr:
                stderr.write(eline)
                stderr.flush()
            logged_err.append(eline)
    return logged_out, logged_err


def cmd(command, shell=False, detatch=False, verbose=0, verbout=None):
    r"""
    Trying to clean up cmd

    Args:
        command (str): bash-like command string or tuple of executable and args
        shell (bool): if True, process is run in shell
        detatch (bool): if True, process is detached and run in background.
        verbose (int): verbosity mode. Can be 0, 1, 2, or 3.
        verbout (int): if True, `command` writes to stdout in realtime.
            defaults to True iff verbose > 0. Note when detatch is True
            all stdout is lost.

    Returns:
        dict: info - information about command status.
            if detatch is False `info` contains captured standard out,
            standard error, and the return code
            if detatch is False `info` contains a reference to the process.

    CommandLine:
        python -m ubelt.util_platform cmd
        python -c "import ubelt as ub; ub.cmd('ping localhost -c 2', verbose=2)"

    References:
        https://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
        https://stackoverflow.com/questions/7729336/how-can-i-print-and-display-subprocess-stdout-and-stderr-output-without-distorti

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
        >>> info1 = ub.cmd(('touch', fpath1), detatch=True)
        >>> info2 = ub.cmd('echo writing2 > ' + fpath2, shell=True, detatch=True)
        >>> while not exists(fpath1):
        ...     pass
        >>> while not exists(fpath2):
        ...     pass
        >>> assert ub.readfrom(fpath1) == ''
        >>> assert ub.readfrom(fpath2).strip() == 'writing2'
        >>> info1['proc'].wait()
        >>> info2['proc'].wait()
    """
    if verbout is None:
        verbout = verbose >= 1
    if verbose >= 2:  # nocover
        if verbose >= 3:
            print('+=== START CMD ===')
            print('CWD:' + os.getcwd())
            print('Command:')
            print(command)
        else:
            from ubelt import util_path
            compname = platform.node()
            username = getpass.getuser()
            cwd = util_path.compressuser(os.getcwd())
            ps1 = '[ubelt.cmd] {}@{}:{}$ '.format(username, compname, cwd)
            print(ps1 + command)
        if verbout >= 3 and not detatch:
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
                            stderr=subprocess.PIPE, shell=shell,
                            universal_newlines=True)
    if detatch:
        info = {'proc': proc}
        if verbose >= 2:  # nocover
            print('...detatching')
    else:
        if verbout:
            stdout, stderr = sys.stdout, sys.stderr
        else:
            stdout, stderr = None, None
        logged_out, logged_err = _proc_tee_output(proc, stdout, stderr)

        try:
            out = ''.join(logged_out)
        except UnicodeDecodeError:  # nocover
            out = '\n'.join(_.decode('utf-8') for _ in logged_out)
        try:
            err = ''.join(logged_err)
        except UnicodeDecodeError:  # nocover
            err = '\n'.join(_.decode('utf-8') for _ in logged_err)
        (out_, err_) = proc.communicate()
        ret = proc.wait()
        info = {
            'out': out,
            'err': err,
            'ret': ret,
        }
        if verbose >= 3:  # nocover
            print('L___ END CMD ___')  # TODO: use nicer unicode chars
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
        >>> ub.editfile(ub.util_platform.__file__)
        >>> ub.editfile(ub)
        >>> ub.editfile(ub.editfile)
    """
    from six import types
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

    if not exists(fpath):
        raise IOError('Cannot start nonexistant file: %r' % fpath)
    cmd([editor, fpath], fpath, detatch=True)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
