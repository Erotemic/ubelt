# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import getpass
import platform
# import os
import sys
import pipes
import shlex
import subprocess
from threading import Thread
from six.moves import zip_longest
from six.moves import queue
from ubelt.util_platform import POSIX, WIN32

if POSIX:
    import select
else:  # nocover
    select = NotImplemented

__all__ = ['cmd']

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


def _proc_async_iter_stream(proc, stream, buffersize=1):
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

    Note:
        WARNING. current implementation might have bugs with other threads.
        This behavior was seen when using earlier versions of tqdm. I'm not
        sure if this was our bug or tqdm's. Newever versions of tqdm fix this,
        but I cannot gaurentee that there isn't an issue on our end.

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
        if stdout_live:  # pragma: nobranch
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


def _tee_output(make_proc, stdout=None, stderr=None, backend='auto'):
    """
    Simultaniously reports and captures stdout and stderr from a process

    subprocess must be created using (stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
    """
    logged_out = []
    logged_err = []
    if backend == 'auto':
        # backend = 'select' if POSIX else 'thread'
        backend = 'thread'

    if backend == 'select':
        if not POSIX:  # nocover
            raise NotImplementedError('select is only available on posix')
        # the select-based version is stable, but slow
        _proc_iteroutput = _proc_iteroutput_select
    elif backend == 'thread':
        # the thread version is fast, but might run into issues.
        _proc_iteroutput = _proc_iteroutput_thread
    else:
        raise ValueError('backend must be select, thread, or auto')

    proc = make_proc()
    for oline, eline in _proc_iteroutput(proc):
        if oline:
            if stdout:  # pragma: nobranch
                stdout.write(oline)
                stdout.flush()
            logged_out.append(oline)
        if eline:
            if stderr:  # pragma: nobranch
                stderr.write(eline)
                stderr.flush()
            logged_err.append(eline)
    return proc, logged_out, logged_err


def cmd(command, shell=False, detatch=False, verbose=0, verbout=None,
        tee='auto'):
    r"""
    Executes a command in a subprocess.

    The advantage of this wrapper around subprocess is that
    (1) you control if the subprocess prints to stdout,
    (2) the text written to stdout and stderr is returned for parsing,
    (3) cross platform behavior that lets you specify the command as a string
    or tuple regardless of whether or not shell=True.
    (4) ability to detatch, return the process object and allow the process to
    run in the background (eventually we may return a Future object instead).

    Args:
        command (str): bash-like command string or tuple of executable and args
        shell (bool): if True, process is run in shell
        detatch (bool): if True, process is detached and run in background.
        verbose (int): verbosity mode. Can be 0, 1, 2, or 3.
        verbout (int): if True, `command` writes to stdout in realtime.
            defaults to True iff verbose > 0. Note when detatch is True
            all stdout is lost.
        tee (str): backend for tee output. Can be either: auto, select (POSIX
            only), or thread.

    Returns:
        dict: info - information about command status.
            if detatch is False `info` contains captured standard out,
            standard error, and the return code
            if detatch is False `info` contains a reference to the process.

    Notes:
        Inputs can either be text or tuple based. On unix we ensure conversion
        to text if shell=True, and to tuple if shell=False. On windows, the
        input is always text based.  See [3] for a potential cross-platform
        shlex solution for windows.

    CommandLine:
        python -m ubelt.util_cmd cmd
        python -c "import ubelt as ub; ub.cmd('ping localhost -c 2', verbose=2)"

    References:
        [1] https://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
        [2] https://stackoverflow.com/questions/7729336/how-can-i-print-and-display-subprocess-stdout-and-stderr-output-without-distorti
        [3] https://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex

    Example:
        >>> info = cmd(('echo', 'simple cmdline interface'), verbose=1)
        simple cmdline interface
        >>> assert info['ret'] == 0
        >>> assert info['out'].strip() == 'simple cmdline interface'
        >>> assert info['err'].strip() == ''

    Doctest:
        >>> info = cmd('echo str noshell', verbose=0)
        >>> assert info['out'].strip() == 'str noshell'

    Doctest:
        >>> # windows echo will output extra single quotes
        >>> info = cmd(('echo', 'tuple noshell'), verbose=0)
        >>> assert info['out'].strip().strip("'") == 'tuple noshell'

    Doctest:
        >>> # Note this command is formatted to work on win32 and unix
        >>> info = cmd('echo str&&echo shell', verbose=0, shell=True)
        >>> assert info['out'].strip() == 'str\nshell'

    Doctest:
        >>> info = cmd(('echo', 'tuple shell'), verbose=0, shell=True)
        >>> assert info['out'].strip().strip("'") == 'tuple shell'

    Doctest:
        >>> import ubelt as ub
        >>> from os.path import join, exists
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
    # Determine if command is specified as text or a tuple
    if isinstance(command, (list, tuple)):
        command_tup = command
        command_text = ' '.join(list(map(pipes.quote, command_tup)))
    else:
        command_text = command
        command_tup = None

    if shell or WIN32:
        # When shell=True, args is sent to the shell (e.g. bin/sh) as text
        args = command_text
    else:
        # When shell=False, args is a list of executable and arguments
        if command_tup is None:
            # parse this out of the string
            # NOTE: perhaps use the solution from [3] here?
            command_tup = shlex.split(command_text)
            # command_tup = shlex.split(command_text, posix=not WIN32)
        args = command_tup

    if verbout is None:
        verbout = verbose >= 1
    if verbose >= 2:  # nocover
        from ubelt import util_path
        import os
        cwd = os.getcwd()
        if verbose >= 3:
            print('+=== START CMD ===')
            # print('CWD:' + os.getcwd())
            print('CWD:' + cwd)
        compname = platform.node()
        username = getpass.getuser()
        cwd = util_path.compressuser(cwd)
        ps1 = '[ubelt.cmd] {}@{}:{}$ '.format(username, compname, cwd)
        print(ps1 + command_text)
        if verbout >= 3 and not detatch:
            print('----')
            print('Stdout:')

    # Create a new process to execute the command
    def make_proc():
        # delay the creation of the process until we validate all args
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=shell,
                                universal_newlines=True)
        return proc

    if detatch:
        info = {'proc': make_proc(), 'command': command_text}
        if verbose >= 2:  # nocover
            print('...detatching')
    else:
        if verbout:
            # we need to tee output nad start threads if verbout is False?
            stdout, stderr = sys.stdout, sys.stderr
            proc, logged_out, logged_err = _tee_output(make_proc, stdout, stderr,
                                                       backend=tee)

            try:
                out = ''.join(logged_out)
            except UnicodeDecodeError:  # nocover
                out = '\n'.join(_.decode('utf-8') for _ in logged_out)
            try:
                err = ''.join(logged_err)
            except UnicodeDecodeError:  # nocover
                err = '\n'.join(_.decode('utf-8') for _ in logged_err)
            (out_, err_) = proc.communicate()
        else:
            proc = make_proc()
            (out, err) = proc.communicate()
        # calling wait means that the process will terminate and it is safe to
        # return a reference to the process object.
        ret = proc.wait()
        info = {
            'out': out,
            'err': err,
            'ret': ret,
            'proc': proc,
            'command': command_text
        }
        if verbose >= 3:  # nocover
            print('L___ END CMD ___')  # TODO: use nicer unicode chars
    return info


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_cmd
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
