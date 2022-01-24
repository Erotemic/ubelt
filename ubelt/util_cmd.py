r"""
This module exposes the :func:`ubelt.cmd` command, which provides a simple
means for interacting with the commandline.  This uses
:class:`subprocess.Popen` under the hood, but improves upon existing
:mod:`subprocess` functionality by:

(1) Adding the option to "tee" the output, i.e. simultaniously capture and
write to stdout and stderr.

(2) Always specify the command as a string. The :mod:`subprocess` module
expects the command as either a  ``List[str]`` if ``shell=False`` and ``str``
if ``shell=True``. If necessary, :func:`ubelt.util_cmd.cmd` will automatically
convert from one format to the other, so passing in either case will work.

(3) Specificy if the process blocks or not by setting ``detatch``. Note: when
``detatch is True`` it is not possible to tee the output.

Example:
    >>> import ubelt as ub
    >>> # Running with verbose=1 will write to stdout in real time
    >>> info = ub.cmd('echo "write your command naturally"', verbose=1)
    write your command naturally
    >>> # Unless `detatch=True`, `cmd` always returns an info dict.
    >>> print('info = ' + ub.repr2(info))
    info = {
        'command': 'echo "write your command naturally"',
        'cwd': None,
        'err': '',
        'out': 'write your command naturally\n',
        'proc': <...Popen...>,
        'ret': 0,
    }
"""
import sys
import warnings

__all__ = ['cmd']

POSIX = 'posix' in sys.builtin_module_names

if POSIX:
    import select
else:  # nocover
    select = NotImplemented


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
    from six.moves import queue
    from threading import Thread
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
        WARNING. Current implementation might have bugs with other threads.
        This behavior was seen when using earlier versions of tqdm. I'm not
        sure if this was our bug or tqdm's. Newer versions of tqdm fix this,
        but I cannot guarantee that there isn't an issue on our end.

    Yields:
        Tuple[str, str]: oline, eline: stdout and stderr line

    References:
        .. [SO_375427] https://stackoverflow.com/questions/375427/non-blocking-read-subproc
    """
    from six.moves import queue

    # Create threads that read stdout / stderr and queue up the output
    stdout_queue = _proc_async_iter_stream(proc, proc.stdout)
    stderr_queue = _proc_async_iter_stream(proc, proc.stderr)

    stdout_live = True
    stderr_live = True

    # read from the output asynchronously until
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


def _proc_iteroutput_select(proc):
    """
    Iterates over output from a process line by line

    UNIX only. Use :func:`_proc_iteroutput_thread` instead for a cross platform
    solution based on threads.

    Yields:
        Tuple[str, str]: oline, eline: stdout and stderr line
    """
    from six.moves import zip_longest
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


def _tee_output(proc, stdout=None, stderr=None, backend='thread'):
    """
    Simultaneously reports and captures stdout and stderr from a process

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
    else:  # nocover
        # The value of "backend" should be checked before we create the
        # processes, otherwise we will have a dangling process
        raise AssertionError('Validate "backend" before creating the proc')

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


def cmd(command, shell=False, detach=False, verbose=0, tee=None, cwd=None,
        env=None, tee_backend='auto', check=False, **kwargs):
    """
    Executes a command in a subprocess.

    The advantage of this wrapper around subprocess is that
    (1) you control if the subprocess prints to stdout,
    (2) the text written to stdout and stderr is returned for parsing,
    (3) cross platform behavior that lets you specify the command as a string
    or tuple regardless of whether or not shell=True.
    (4) ability to detach, return the process object and allow the process to
    run in the background (eventually we may return a Future object instead).

    Args:
        command (str | List[str]): bash-like command string or tuple of
            executable and args

        shell (bool, default=False): if True, process is run in shell.

        detach (bool, default=False):
            if True, process is detached and run in background.

        verbose (int, default=0): verbosity mode. Can be 0, 1, 2, or 3.

        tee (bool | None): if True, simultaneously writes to stdout while
            capturing output from the command. If not specified, defaults to
            True if verbose > 0.  If detach is True, then this argument is
            ignored.

        cwd (str | PathLike | None):
            Path to run command. Defaults to current working directory if
            unspecified.

        env (Dict[str, str] | None): environment passed to Popen

        tee_backend (str, default='auto'): backend for tee output.
            Valid choices are: "auto", "select" (POSIX only), and "thread".

        check (bool, default=False): if True, check that the return code was
            zero before returning, otherwise raise a CalledProcessError.
            Does nothing if detach is True.

        **kwargs: only used to support deprecated arguments

    Returns:
        dict:
            info - information about command status.
            if detach is False ``info`` contains captured standard out,
            standard error, and the return code
            if detach is False ``info`` contains a reference to the process.

    Note:
        Inputs can either be text or tuple based. On UNIX we ensure conversion
        to text if shell=True, and to tuple if shell=False. On windows, the
        input is always text based.  See [SO_33560364]_ for a potential
        cross-platform shlex solution for windows.

    CommandLine:
        xdoctest -m ubelt.util_cmd cmd:6
        python -c "import ubelt as ub; ub.cmd('ping localhost -c 2', verbose=2)"
        pytest "$(python -c 'import ubelt; print(ubelt.util_cmd.__file__)')" -sv --xdoctest-verbose 2

    References:
        .. [SO_11495783] https://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
        .. [SO_7729336] https://stackoverflow.com/questions/7729336/how-can-i-print-and-display-subprocess-stdout-and-stderr-output-without-distorti
        .. [SO_33560364] https://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex

    Example:
        >>> import ubelt as ub
        >>> info = ub.cmd(('echo', 'simple cmdline interface'), verbose=1)
        simple cmdline interface
        >>> assert info['ret'] == 0
        >>> assert info['out'].strip() == 'simple cmdline interface'
        >>> assert info['err'].strip() == ''

    Example:
        >>> import ubelt as ub
        >>> info = ub.cmd('echo str noshell', verbose=0)
        >>> assert info['out'].strip() == 'str noshell'

    Example:
        >>> # windows echo will output extra single quotes
        >>> import ubelt as ub
        >>> info = ub.cmd(('echo', 'tuple noshell'), verbose=0)
        >>> assert info['out'].strip().strip("'") == 'tuple noshell'

    Example:
        >>> # Note this command is formatted to work on win32 and unix
        >>> import ubelt as ub
        >>> info = ub.cmd('echo str&&echo shell', verbose=0, shell=True)
        >>> assert info['out'].strip() == 'str' + chr(10) + 'shell'

    Example:
        >>> import ubelt as ub
        >>> info = ub.cmd(('echo', 'tuple shell'), verbose=0, shell=True)
        >>> assert info['out'].strip().strip("'") == 'tuple shell'

    Example:
        >>> import pytest
        >>> import ubelt as ub
        >>> info = ub.cmd('echo hi', check=True)
        >>> import subprocess
        >>> with pytest.raises(subprocess.CalledProcessError):
        >>>     ub.cmd('exit 1', check=True, shell=True)

    Example:
        >>> import ubelt as ub
        >>> from os.path import join, exists
        >>> fpath1 = join(ub.get_app_cache_dir('ubelt'), 'cmdout1.txt')
        >>> fpath2 = join(ub.get_app_cache_dir('ubelt'), 'cmdout2.txt')
        >>> ub.delete(fpath1)
        >>> ub.delete(fpath2)
        >>> # Start up two processes that run simultaneously in the background
        >>> info1 = ub.cmd(('touch', fpath1), detach=True)
        >>> info2 = ub.cmd('echo writing2 > ' + fpath2, shell=True, detach=True)
        >>> # Detached processes are running in the background
        >>> # We can run other code while we wait for them.
        >>> while not exists(fpath1):
        ...     pass
        >>> while not exists(fpath2):
        ...     pass
        >>> # communicate with the process before you finish
        >>> # (otherwise you may leak a text wrapper)
        >>> info1['proc'].communicate()
        >>> info2['proc'].communicate()
        >>> # Check that the process actually did finish
        >>> assert (info1['proc'].wait()) == 0
        >>> assert (info2['proc'].wait()) == 0
        >>> # Check that the process did what we expect
        >>> assert ub.readfrom(fpath1) == ''
        >>> assert ub.readfrom(fpath2).strip() == 'writing2'
    """
    import subprocess
    # TODO: stdout, stderr - experimental - custom file to pipe stdout/stderr to
    if kwargs:  # nocover
        if 'verbout' in kwargs:
            warnings.warn(
                '`verbout` is deprecated and will be removed. '
                'Use `tee` instead', DeprecationWarning)
            tee = kwargs.pop('verbout')

        if 'detatch' in kwargs:
            warnings.warn(
                '`detatch` is deprecated (misspelled) and will be removed. '
                'Use `detach` instead', DeprecationWarning)
            detach = kwargs.pop('detatch')

        if kwargs:
            raise ValueError('Unknown kwargs: {}'.format(list(kwargs.keys())))

    # Determine if command is specified as text or a tuple
    if isinstance(command, str):
        command_text = command
        command_tup = None
    else:
        import pipes
        command_tup = command
        command_text = ' '.join(list(map(pipes.quote, command_tup)))

    if shell or sys.platform.startswith('win32'):
        # When shell=True, args is sent to the shell (e.g. bin/sh) as text
        args = command_text
    else:
        # When shell=False, args is a list of executable and arguments
        if command_tup is None:
            # parse this out of the string
            # NOTE: perhaps use the solution from [3] here?
            import shlex
            command_tup = shlex.split(command_text)
            # command_tup = shlex.split(command_text, posix=not WIN32)
        args = command_tup

    if tee is None:
        tee = verbose > 0

    if tee and tee_backend not in {'auto', 'thread', 'select'}:
        raise ValueError('tee_backend must be select, thread, or auto')

    if verbose > 1:
        import os
        import platform
        import getpass
        from ubelt import shrinkuser
        if verbose > 2:
            try:
                print('┌─── START CMD ───')
            except Exception:  # nocover
                print('+=== START CMD ===')
        cwd_ = os.getcwd() if cwd is None else cwd
        compname = platform.node()
        username = getpass.getuser()
        cwd_ = shrinkuser(cwd_)
        ps1 = '[ubelt.cmd] {}@{}:{}$ '.format(username, compname, cwd_)
        print(ps1 + command_text)

    # Create a new process to execute the command
    def make_proc():
        # delay the creation of the process until we validate all args
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=shell,
                                universal_newlines=True, cwd=cwd, env=env)
        return proc

    if detach:
        info = {'proc': make_proc(), 'command': command_text}
        if verbose > 0:  # nocover
            print('...detaching')
    else:
        if tee:
            # We logging stdout and stderr, while simulaniously piping it to
            # another stream.
            stdout = sys.stdout
            stderr = sys.stderr
            proc = make_proc()
            proc, logged_out, logged_err = _tee_output(proc, stdout, stderr,
                                                       backend=tee_backend)

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
            'cwd': cwd,
            'command': command_text
        }
        if verbose > 2:
            # https://en.wikipedia.org/wiki/Box-drawing_character
            try:
                print('└─── END CMD ───')
            except Exception:  # nocover
                print('L___ END CMD ___')

        if check:
            if info['ret'] != 0:
                raise subprocess.CalledProcessError(
                    info['ret'], info['command'], info['out'], info['err'])
    return info
