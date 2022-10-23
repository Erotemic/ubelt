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

(3) Specificy if the process blocks or not by setting ``detach``. Note: when
``detach is True`` it is not possible to tee the output.

Example:
    >>> import ubelt as ub
    >>> # Running with verbose=1 will write to stdout in real time
    >>> info = ub.cmd('echo "write your command naturally"', verbose=1)
    write your command naturally
    >>> # Unless `detach=True`, `cmd` always returns an info dict.
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
import os


__pitch__ = """
The ubelt.cmd command is probably the easiest way to execute a command line program from Python. Unlike os.system, subprocess.check_output, and subprocess.call, The syntax for what you want to call is exactly the same no matter what type of configuration you are using.

Either pass the text you would execute on the command line directly or break it up into a list where each item should be considered its own argument. This works regardless of if shell=True or shell=False, so if your command doesn't work with the safer shell=False, you can turn on shell=True without modifying anything else. You can capture output, print it to the screen, or namely --- something few other packages support --- both (via tee=True or verbose>1).

You can also invoke the call via os.system instead of Popen by setting system=True (although this does come with all of the os.system benefits and restrictions).

I'm biased because I wrote it, but subprocess-tee is the only other package I know of that comes close to getting this right. Maybe invoke?
"""

# import logging
# logging.basicConfig(
#     format='[%(asctime)s %(threadName)s %(levelname)s] %(message)s',
#     level=logging.DEBUG,
#     force=True
# )
# logger = logging.getLogger(__name__)

__all__ = ['cmd']

POSIX = 'posix' in sys.builtin_module_names
WIN32 = sys.platform == 'win32'


def cmd(command, shell=False, detach=False, verbose=0, tee=None, cwd=None,
        env=None, tee_backend='auto', check=False, system=False, timeout=None):
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
        command (str | List[str]):
            command string, tuple of executable and args, or shell command.

        shell (bool, default=False):
            if True, process is run in shell.

        detach (bool, default=False):
            if True, process is detached and run in background.

        verbose (int, default=0):
            verbosity mode. Can be 0, 1, 2, or 3.

        tee (bool | None):
            if True, simultaneously writes to stdout while capturing output
            from the command. If not specified, defaults to True if verbose >
            0.  If detach is True, then this argument is ignored.

        cwd (str | PathLike | None):
            Path to run command. Defaults to current working directory if
            unspecified.

        env (Dict[str, str] | None):
            environment passed to Popen

        tee_backend (str, default='auto'): backend for tee output.
            Valid choices are: "auto", "select" (POSIX only), and "thread".

        check (bool, default=False):
            if True, check that the return code was zero before returning,
            otherwise raise a :class:`subprocess.CalledProcessError`.
            Does nothing if detach is True.

        system (bool, default=False):
            if True, most other considerations are dropped, and
            :func:`os.system` is used to execute the command in a platform
            dependant way. Other arguments such as env, tee, timeout, and shell
            are all ignored.  (new in version 1.1.0)

        timeout (float):
            If the process does not complete in `timeout` seconds, raises a
            :class:`subprocess.TimeoutExpired`. (new in version 1.1.0)
            Currently unhandled when tee is True.

        log (Callable | None):
            If specified, verbose output is written using this function,
            otherwise the builtin print function is used.

    Returns:
        dict:
            info - information about command status.
            if detach is False ``info`` contains captured standard out,
            standard error, and the return code
            if detach is True ``info`` contains a reference to the process.

    Raises:
        ValueError - on an invalid configuration
        subprocess.TimeoutExpired - if the timeout limit is exceeded
        subprocess.CalledProcessError - if check and the return value is non zero

    Note:
        Inputs can either be text or tuple based. On UNIX we ensure conversion
        to text if shell=True, and to tuple if shell=False. On windows, the
        input is always text based.  See [SO_33560364]_ for a potential
        cross-platform shlex solution for windows.

        When using the tee output, the stdout and stderr may be shuffled from
        what they would be on the command line.

    Related Work:
        https://github.com/pycontribs/subprocess-tee
        https://github.com/mortoray/shelljob
        https://github.com/netinvent/command_runner
        https://www.pyinvoke.org/prior-art.html

    References:
        .. [SO_11495783] https://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
        .. [SO_7729336] https://stackoverflow.com/questions/7729336/how-can-i-print-and-display-subprocess-stdout-and-stderr-output-without-distorti
        .. [SO_33560364] https://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex

    CommandLine:
        xdoctest -m ubelt.util_cmd cmd:6
        python -c "import ubelt as ub; ub.cmd('ping localhost -c 2', verbose=2)"
        pytest "$(python -c 'import ubelt; print(ubelt.util_cmd.__file__)')" -sv --xdoctest-verbose 2

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
        >>> dpath = ub.Path.appdir('ubelt', 'test').ensuredir()
        >>> fpath1 = (dpath / 'cmdout1.txt').delete()
        >>> fpath2 = (dpath / 'cmdout2.txt').delete()
        >>> # Start up two processes that run simultaneously in the background
        >>> info1 = ub.cmd(('touch', str(fpath1)), detach=True)
        >>> info2 = ub.cmd('echo writing2 > ' + str(fpath2), shell=True, detach=True)
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
        >>> assert fpath1.read_text() == ''
        >>> assert fpath2.read_text().strip() == 'writing2'

    Example:
        >>> # Can also use ub.cmd to call os.system
        >>> import pytest
        >>> import ubelt as ub
        >>> import subprocess
        >>> info = ub.cmd('echo hi', check=True, system=True)
        >>> with pytest.raises(subprocess.CalledProcessError):
        >>>     ub.cmd('exit 1', check=True, shell=True)
    """
    # In the future we might allow the user to pass a custom log function
    # But this has weird interactions with how the tee process works
    # becasue of the assumption stdout.write does not emit a newline
    log = print

    import subprocess
    # TODO: stdout, stderr - experimental - custom file to pipe stdout/stderr to
    # Determine if command is specified as text or a tuple
    if isinstance(command, str):
        command_text = command
        command_tup = None
    else:
        import pipes
        command_parts = []
        # Allow the user to specify paths as part of the command
        for part in command:
            if isinstance(part, os.PathLike):
                part = os.fspath(part)
            command_parts.append(part)
        command_tup = tuple(command_parts)
        command_text = ' '.join(list(map(pipes.quote, command_tup)))

    if shell or sys.platform.startswith('win32'):
        # When shell=True, args is sent to the shell (e.g. bin/sh) as text
        args = command_text
    else:
        # When shell=False, args is a list of executable and arguments
        if command_tup is None:
            # parse this out of the string
            # NOTE: perhaps use the solution from [SO_33560364] here?
            import shlex
            command_tup = shlex.split(command_text)
            # command_tup = shlex.split(command_text, posix=not WIN32)
        args = command_tup

    if tee is None:
        tee = verbose > 0

    if tee and tee_backend not in {'auto', 'thread', 'select'}:
        raise ValueError('tee_backend must be select, thread, or auto')

    if verbose > 1:
        import platform
        import getpass
        from ubelt import shrinkuser
        if verbose > 2:
            try:
                log('┌─── START CMD ───')
            except Exception:  # nocover
                log('+=== START CMD ===')
        cwd_ = os.getcwd() if cwd is None else cwd
        compname = platform.node()
        username = getpass.getuser()
        cwd_ = shrinkuser(cwd_)
        ps1 = '[ubelt.cmd] {}@{}:{}$ '.format(username, compname, cwd_)
        log(ps1 + command_text)

    # Create a new process to execute the command
    def make_proc():
        # delay the creation of the process until we validate all args
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=shell,
                                universal_newlines=True, cwd=cwd, env=env)
        return proc

    if system:
        info = {
            'command': command_text,
            'out': None,
            'err': None,
        }
        ret = os.system(command_text)
        info['ret'] = ret
    elif detach:
        info = {'proc': make_proc(), 'command': command_text}
        if verbose > 0:  # nocover
            log('...detaching')
    else:
        if tee:
            # We logging stdout and stderr, while simulaniously piping it to
            # another stream.
            stdout = sys.stdout
            stderr = sys.stderr
            proc = make_proc()
            with proc:
                out, err = _tee_output(
                    proc=proc, stdout=stdout, stderr=stderr,
                    backend=tee_backend, timeout=timeout,
                    command_text=command_text)
                (out_, err_) = proc.communicate(timeout=timeout)
        else:
            proc = make_proc()
            with proc:
                try:
                    (out, err) = proc.communicate(timeout=timeout)
                except subprocess.TimeoutExpired as exc:
                    # Follow the error handling in the stdlib implementaton of
                    # subprocess.run
                    proc.kill()
                    if WIN32:  # nocover
                        # Win32 needs a communicate after the kill to get the
                        # output. See stdlib for details.
                        exc.stdout, exc.stderr = proc.communicate()
                    else:
                        # Posix implementations already handle the populate.
                        proc.wait()
                    raise
        # We used the popen context manager, which means that wait was called,
        # the process has existed, so it is safe to return a reference to the
        # process object.
        ret = proc.poll()
        info = {
            'out': out,
            'err': err,
            'ret': ret,
            'proc': proc,
            'cwd': cwd,
            'command': command_text
        }

    if not detach:
        if verbose > 2:
            # https://en.wikipedia.org/wiki/Box-drawing_character
            try:
                log('└─── END CMD ───')
            except Exception:  # nocover
                log('L___ END CMD ___')

        if check:
            if info['ret'] != 0:
                raise subprocess.CalledProcessError(
                    info['ret'], info['command'], info['out'], info['err'])
    return info


def _textio_iterlines(stream):
    """
    Iterates over lines in a TextIO stream until an EOF is encountered.
    This is the iterator version of stream.readlines()

    Args:
        stream (io.TextIOWrapper): The stream to finish reading.

    Yields:
        str: a line read from the stream.
    """
    try:
        # These if statements help mitigate race conditions but does not solve
        # them if the stream closes in the middle of a readline.
        if stream.closed:  # nocover
            return
        line = stream.readline()
        while line != '':
            yield line
            if stream.closed:  # nocover
                return
            line = stream.readline()
    except ValueError:  # nocover
        # Ignore I/O operation on closed files, the process was likely
        # killed.
        raise
        ...


def _proc_async_iter_stream(proc, stream, buffersize=1, timeout=None):
    """
    Reads output from a process in a separate thread

    Args:
        proc (subprocess.Popen): The process being run

        stream (io.TextIOWrapper): A stream belonging to the process
            e.g. ``proc.stdout`` or ``proc.stderr``.

        buffersize (int): Size of the returned queue.

    Returns:
        queue.Queue:
            The queue that the output lines will be asynchronously written to
            as they are read from the stream.
    """
    import queue
    import threading
    # logger.debug(f"Create and start thread for {id(stream)}")
    out_queue = queue.Queue(maxsize=buffersize)
    control_queue = queue.Queue(maxsize=1)
    io_thread = threading.Thread(
        target=_enqueue_output_thread_worker, args=(
            proc, stream, out_queue, control_queue, timeout))
    io_thread.daemon = True  # thread dies with the program
    io_thread.start()
    return io_thread, out_queue, control_queue


def _enqueue_output_thread_worker(proc, stream, out_queue, control_queue, timeout=None):
    """
    Thread worker function

    This follows a similar strategy employed in
    http://eyalarubas.com/python-subproc-nonblock.html and
    https://stackoverflow.com/questions/375427/a-non-blocking-read-on-a-subprocess-pipe-in-python/4896288#4896288

    Args:
        proc (subprocess.Popen): The process being run

        stream (io.TextIOWrapper): A stream belonging to the process
            e.g. ``proc.stdout`` or ``proc.stderr``.

        out_queue (queue.Queue): The queue to write to.

        control_queue (queue.Queue): For sending a signal to stop the thread

        timeout (None | float): amount of time to allow before stopping
    """
    import queue
    # logger.debug(f"Start worker for {id(stream)=} with {timeout=}")

    def _check_if_stopped():  # nocover
        try:
            # Check if we were told to stop
            control_queue.get_nowait()
        except queue.Empty:
            ...
        else:
            # logger.debug(f"Thread acknowledges stop request for {id(stream)}")
            return True

    def enqueue(item):  # nocover
        # Alternate between checking if we were stopped and putting the item in
        # the queue. This helps with the issue of an open process stream on
        # exit but it doesn't fully solve the issue because we still might
        # block on the stream.readline, therefore we can't guarentee this
        # thread will exit before the process does.
        if timeout is None:
            # If timeout is None, we can optimize this and just use the
            # blocking call.
            out_queue.put(item)
            return True

        # logger.debug('Waiting to put in item')
        while True:
            if _check_if_stopped():
                return False
            try:
                out_queue.put(item, block=False)
                # logger.debug('Thread put in item')
            except queue.Full:
                pass
            else:
                return True

    while proc.poll() is None:

        # Note: if the underlying process has buffered output, we may get this
        # line well after it is initially emitted and thus be stuck waiting
        # here for some time.
        # logger.debug(f"ENQUEUE Waiting for line {id(stream)}")
        line = stream.readline()

        # logger.debug(f"ENQUEUE LIVE {id(stream)} {line!r}")
        if not enqueue(line):  # nocover
            return

    if _check_if_stopped():  # nocover
        return

    # Coverage note: on Python 3.10 it seems like the tests dont always cover
    # these lines. We don't have much control over if this happens or not, so
    # we will exclude them from coverage checks.
    for line in _textio_iterlines(stream):  # nocover
        # logger.debug(f"ENQUEUE FINAL {id(stream)} {line!r}")
        if not enqueue(line):  # nocover
            return

    # logger.debug(f"STREAM IS DONE {id(stream)}")
    # signal that the stream is finished
    if not enqueue(None):  # nocover
        return


def _proc_iteroutput_thread(proc, timeout=None):
    """
    Iterates over output from a process line by line.

    Follows the answers from [SO_375427]_.

    Note:
        WARNING. Current implementation might have bugs with other threads.
        This behavior was seen when using earlier versions of tqdm. I'm not
        sure if this was our bug or tqdm's. Newer versions of tqdm fix this,
        but I cannot guarantee that there isn't an issue on our end.

    Yields:
        Tuple[str, str]: oline, eline - stdout and stderr line

    References:
        .. [SO_375427] https://stackoverflow.com/questions/375427/non-blocking-read-subproc
    """
    import queue

    # logger.debug("Create stdout/stderr streams")
    # Create threads that read stdout / stderr and queue up the output
    stdout_thread, stdout_queue, stdout_ctrl = _proc_async_iter_stream(proc, proc.stdout, timeout=timeout)
    stderr_thread, stderr_queue, stderr_ctrl = _proc_async_iter_stream(proc, proc.stderr, timeout=timeout)

    stdout_live = True
    stderr_live = True

    if timeout is not None:
        from time import monotonic as _time
        import subprocess
        start_time = _time()

    # read from the output asynchronously until
    while stdout_live or stderr_live:
        # Note: This function loop happens very quickly.
        # # logger.debug("Fast loop: check stdout / stderr threads")

        if timeout is not None:
            # Check for timeouts
            elapsed = _time() - start_time
            if elapsed >= timeout:
                stdout_ctrl.put('STOP')
                stderr_ctrl.put('STOP')
                # Unfortunately we can't guarentee that the threads will stop
                # because they might get stuck in a readline
                # stdout_thread.join()
                # stderr_thread.join()
                yield subprocess.TimeoutExpired, subprocess.TimeoutExpired

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


def _proc_iteroutput_select(proc, timeout=None):
    """
    Iterates over output from a process line by line

    UNIX only. Use :func:`_proc_iteroutput_thread` instead for a cross platform
    solution based on threads.

    Args:
        proc (subprocess.Popen): the process being run

        timeout (None | float): amount of time to allow before stopping

    Yields:
        Tuple[str, str]: oline, eline - stdout and stderr line
    """
    from itertools import zip_longest
    import select

    if timeout is not None:
        from time import monotonic as _time
        import subprocess
        start_time = _time()

    # Read output while the external program is running
    while proc.poll() is None:
        if timeout is not None:
            elapsed = _time() - start_time
            if elapsed >= timeout:
                yield subprocess.TimeoutExpired, subprocess.TimeoutExpired
                return  # nocover

        reads = [proc.stdout.fileno(), proc.stderr.fileno()]
        ret = select.select(reads, [], [], timeout)
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


def _tee_output(proc, stdout=None, stderr=None, backend='thread',
                timeout=None, command_text=None):
    """
    Simultaneously reports and captures stdout and stderr from a process

    subprocess must be created using (stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)

    Args:
        proc (subprocess.Popen): the process being run

        stdout (io.TextIOWrapper): typically sys.stdout

        stderr (io.TextIOWrapper): typically sys.stderr

        backend (str): thread, select or auto

        timeout (None | float): time before raising a timeout error

        command_text (str): used only to construct a TimeoutExpired error.

    Returns:
        Tuple[str, str]: recorded stdout and stderr
    """
    import subprocess
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
        raise AssertionError(
            'Invalid backend, but the check should have already a happened')

    # TODO: handle timeout
    output_gen = _proc_iteroutput(proc, timeout=timeout)
    # logger.debug("Start waiting for buffered output")
    for oline, eline in output_gen:
        if timeout is not None:
            if oline is subprocess.TimeoutExpired or eline is subprocess.TimeoutExpired:
                # logger.error("Timeout error triggered!")
                try:
                    out = ''.join(logged_out)
                except UnicodeDecodeError:  # nocover
                    out = '\n'.join(_.decode('utf-8') for _ in logged_out)
                try:
                    err = ''.join(logged_err)
                except UnicodeDecodeError:  # nocover
                    err = '\n'.join(_.decode('utf-8') for _ in logged_err)
                # Following the standard library implementation of
                # :func:`subprocess.run`, we kill (not terminate) the process
                # when the timeout expires. We shouldn't need the extra
                # communicate fix for windows because we report the tee-ed
                # output that already exists. But lets see what the CI says.
                proc.kill()
                proc.wait()
                raise subprocess.TimeoutExpired(command_text, timeout, out, err)
        if oline:
            # logger.debug("Write oline to stdout.write and logged_out")
            if stdout:  # pragma: nobranch
                stdout.write(oline)
                stdout.flush()
            logged_out.append(oline)
        if eline:
            # logger.debug("Write eline to stderr.write and logged_err")
            if stderr:  # pragma: nobranch
                stderr.write(eline)
                stderr.flush()
            logged_err.append(eline)
        # logger.debug("Continue waiting for buffered output")

    # The motivation for this logic is unclear.
    # In what cases is the logged output returned as bytes or text?
    # Using a bytes join probably makes more sense in most cases.
    try:
        out = ''.join(logged_out)
    except UnicodeDecodeError:  # nocover
        out = '\n'.join(_.decode('utf-8') for _ in logged_out)
    try:
        err = ''.join(logged_err)
    except UnicodeDecodeError:  # nocover
        err = '\n'.join(_.decode('utf-8') for _ in logged_err)

    return out, err


# Stub for possible object oriented interface
# class Command:
#     """
#     TODO
#     """
#     ...
