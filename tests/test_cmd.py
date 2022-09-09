import pytest
import sys
import ubelt as ub

# import shlex
# PYEXE = shlex.quote(sys.executable)
PYEXE = sys.executable


def test_cmd_stdout():
    """
    Debug:

        # Issues on windows
        python -c "import ubelt; ubelt.cmd('echo hello stdout')"

        python -c "import subprocess; subprocess.call(['echo', 'hi'])"

        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=shell,
                                universal_newlines=True, cwd=cwd, env=env)

    """
    with ub.CaptureStdout() as cap:
        result = ub.cmd('echo hello stdout', verbose=True)
    assert result['out'].strip() == 'hello stdout'
    assert cap.text.strip() == 'hello stdout'


def test_cmd_veryverbose():
    with ub.CaptureStdout() as cap:
        result = ub.cmd('echo hello stdout', verbose=3)
    assert result['out'].strip() == 'hello stdout'
    print(cap.text)
    # assert cap.text.strip() == 'hello stdout'


def test_tee_false():
    with ub.CaptureStdout() as cap:
        result = ub.cmd('echo hello stdout', verbose=3, tee=False)
    assert result['out'].strip() == 'hello stdout'
    assert 'hello world' not in cap.text
    print(cap.text)


def test_cmd_stdout_quiet():
    with ub.CaptureStdout() as cap:
        result = ub.cmd('echo hello stdout', verbose=False)
    assert result['out'].strip() == 'hello stdout', 'should still capture internally'
    assert cap.text.strip() == '', 'nothing should print to stdout'


def test_cmd_stderr():
    result = ub.cmd('echo hello stderr 1>&2', shell=True, verbose=True)
    assert result['err'].strip() == 'hello stderr'


def test_cmd_with_pathlib():
    if not ub.POSIX:
        pytest.skip('posix only')
    fpath = ub.Path(ub.__file__)
    result = ub.cmd(['ls', fpath])
    assert str(fpath) in result['out']


def test_cmd_tee_auto():
    """
    pytest ubelt/tests/test_cmd.py -k tee_backend
    pytest ubelt/tests/test_cmd.py
    """
    command = '{pyexe} -c "for i in range(100): print(str(i))"'.format(pyexe=PYEXE)
    result = ub.cmd(command, verbose=0, tee_backend='auto')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'


def test_cmd_tee_thread():
    """
    CommandLine:
        pytest ubelt/tests/test_cmd.py::test_cmd_tee_thread -s
        python ubelt/tests/test_cmd.py test_cmd_tee_thread
    """
    if 'tqdm' in sys.modules:
        if tuple(map(int, sys.modules['tqdm'].__version__.split('.'))) < (4, 19):
            pytest.skip('threads cause issues with early tqdms')

    import threading
    # check which threads currently exist (ideally 1)
    existing_threads = list(threading.enumerate())
    print('existing_threads = {!r}'.format(existing_threads))

    command = '{pyexe} -c "for i in range(10): print(str(i))"'.format(pyexe=PYEXE)
    result = ub.cmd(command, verbose=0, tee_backend='thread')
    assert result['out'] == '\n'.join(list(map(str, range(10)))) + '\n'

    after_threads = list(threading.enumerate())
    print('after_threads = {!r}'.format(after_threads))
    assert len(existing_threads) <= len(after_threads), (
        'we should be cleaning up our threads')


@pytest.mark.skipif(sys.platform == 'win32', reason='not available on win32')
def test_cmd_tee_select():
    command = '{pyexe} -c "for i in range(100): print(str(i))"'.format(pyexe=PYEXE)
    result = ub.cmd(command, verbose=1, tee_backend='select')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'

    command = '{pyexe} -c "for i in range(100): print(str(i))"'.format(pyexe=PYEXE)
    result = ub.cmd(command, verbose=0, tee_backend='select')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='not available on win32')
def test_cmd_tee_badmethod():
    """
    pytest tests/test_cmd.py::test_cmd_tee_badmethod
    """
    command = '{pyexe} -c "for i in range(100): print(str(i))"'.format(pyexe=PYEXE)
    with pytest.raises(ValueError):
        ub.cmd(command, verbose=2, tee_backend='bad tee backend')


def test_cmd_multiline_stdout():
    """
    python ubelt/tests/test_cmd.py test_cmd_multiline_stdout
    pytest ubelt/tests/test_cmd.py::test_cmd_multiline_stdout
    """
    command = '{pyexe} -c "for i in range(10): print(str(i))"'.format(pyexe=PYEXE)
    result = ub.cmd(command, verbose=0)
    assert result['out'] == '\n'.join(list(map(str, range(10)))) + '\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='does not run on win32')
def test_cmd_interleaved_streams_sh():
    """
    A test that ``Crosses the Streams'' of stdout and stderr

    pytest ubelt/tests/test_cmd.py::test_cmd_interleaved_streams_sh
    """
    if False:
        sh_script = ub.codeblock(
            r'''
            for i in `seq 0 29`;
            do
                sleep .001
                >&1 echo "O$i"
                if [ "$(($i % 5))" = "0" ]; then
                    >&2 echo "!E$i"
                fi
            done
            ''').lstrip()
        result = ub.cmd(sh_script, shell=True, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'
    else:
        sh_script = ub.codeblock(
            r'''
            for i in `seq 0 15`;
            do
                sleep .000001
                >&1 echo "O$i"
                if [ "$(($i % 5))" = "0" ]; then
                    >&2 echo "!E$i"
                fi
            done
            ''').lstrip()
        result = ub.cmd(sh_script, shell=True, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='does not run on win32')
def test_cmd_interleaved_streams_py():
    # apparently multiline quotes dont work on win32
    if False:
        # slow mode
        py_script = ub.codeblock(
            r'''
            python -c "
            import sys
            import time
            for i in range(30):
                time.sleep(.001)
                sys.stdout.write('O{}\n'.format(i))
                sys.stdout.flush()
                if i % 5 == 0:
                    sys.stderr.write('!E{}\n'.format(i))
                    sys.stderr.flush()
            "
            ''').lstrip().format(pyexe=PYEXE)
        result = ub.cmd(py_script, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'
    else:
        # faster mode
        py_script = PYEXE + ' ' + ub.codeblock(
            r'''
            -c "
            import sys
            import time
            for i in range(15):
                time.sleep(.000001)
                sys.stdout.write('O{}\n'.format(i))
                sys.stdout.flush()
                if i % 5 == 0:
                    sys.stderr.write('!E{}\n'.format(i))
                    sys.stderr.flush()
            "
            ''').lstrip()
        result = ub.cmd(py_script, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\n'
        assert result['err'] == '!E0\n!E5\n!E10\n'


def test_cwd():
    """
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_cmd.py test_cwd
    """
    import sys
    import os
    import ubelt as ub
    if not sys.platform.startswith('win32'):
        dpath = ub.Path.appdir('ubelt/tests').ensuredir()
        dpath = os.path.realpath(dpath)
        info = ub.cmd('pwd', cwd=dpath, shell=True)
        print('info = {}'.format(ub.repr2(info, nl=1)))
        print('dpath = {!r}'.format(dpath))
        assert info['out'].strip() == dpath


def test_env():
    import sys
    import ubelt as ub
    import os
    if not sys.platform.startswith('win32'):
        env = os.environ.copy()
        env.update({'UBELT_TEST_ENV': '42'})
        info = ub.cmd('echo $UBELT_TEST_ENV', env=env, shell=True)
        print(info['out'])
        assert info['out'].strip() == env['UBELT_TEST_ENV']


# @pytest.mark.skipif(sys.platform == 'win32', reason='does not run on win32')
def test_timeout():
    import subprocess
    import pytest
    # Infinite script
    py_script = ub.codeblock(
        r'''
        {pyexe} -c "
        while True:
            pass
        "
        ''').lstrip().format(pyexe=PYEXE)
    # info = ub.cmd(py_script, detach=1)

    initial_grid = list(ub.named_product({
        'tee': [0, 1],
        'timeout': [0, 0.001, 0.01],
    }))
    expanded_grid = []
    for kw in initial_grid:
        if kw['tee']:
            if not ub.WIN32:
                expanded_grid.append(ub.dict_union(kw, {'tee_backend': 'select'}))
            expanded_grid.append(ub.dict_union(kw, {'tee_backend': 'thread'}))
        else:
            expanded_grid.append(kw)

    for kw in expanded_grid:
        print('kw = {}'.format(ub.repr2(kw, nl=0)))
        with pytest.raises(subprocess.TimeoutExpired):
            ub.cmd(py_script, **kw)
            return


def _dev_debug_timeouts():
    """
    Notes used when implementating timeout

    Ignore:
        # For debugging and development
        import sys
        from ubelt.util_cmd import (
            _textio_iterlines, _proc_async_iter_stream,
            _proc_iteroutput_thread, _proc_iteroutput_select, _tee_output, logger)

        import logging
        logging.basicConfig(
            format='[%(asctime)s %(threadName)s %(levelname)s] %(message)s',
            level=logging.DEBUG,
            force=True
        )
        logging.info('hi')
        logging.debug('hi')

        import subprocess
        args = ['ping', 'localhost', '-c', '1000']
        args = ['python', '-c', "{}".format(chr(10) + ub.codeblock(
            '''
            import sys
            import time
            import random
            import ubelt as ub
            wait_times = [0.5, 1.0, 2.0]
            def pseudo_sleep(sec):
                timer = ub.Timer().tic()
                while timer.toc() < sec:
                    ...
            print('Starting a process')
            while True:
                sec = random.choice(wait_times)
                print('Sleep for {} seconds'.format(sec))
                #pseudo_sleep(sec)
                #time.sleep(sec)
                time.sleep(0.05)
                print('Slept for {} seconds'.format(sec))
            ''') + chr(10))]
        args = ['python', '-c', "{}".format(chr(10) + ub.codeblock(
            '''
            import sys
            import ubelt as ub
            import time
            print('Starting a process')
            for i in range(4):
                print('Step {} {}'.format(i, ub.timestamp(precision=4)))
                time.sleep(1.0)
            ''') + chr(10))]
        lines = []
        log = lines.append
        info = ub.cmd(args, verbose=3, shell=True, tee_backend='thread', timeout=10)

        try:
            ub.cmd(args, verbose=0, shell=True, tee_backend='thread', timeout=2)
        except subprocess.TimeoutExpired as e:
            std_ex = e

        try:
            ub.cmd(args, verbose=3, shell=True, tee_backend='thread', timeout=2)
        except subprocess.TimeoutExpired as e:
            verb_ex = e

        print('verb_ex.__dict__ = {}'.format(ub.repr2(verb_ex.__dict__, nl=1)))
        print('std_ex.__dict__ = {}'.format(ub.repr2(std_ex.__dict__, nl=1)))
    """


if __name__ == '__main__':
    """
        pytest ubelt/tests/test_cmd.py -s

        python ~/code/ubelt/ubelt/tests/test_cmd.py test_cmd_veryverbose
    """

    import xdoctest
    xdoctest.doctest_module(__file__)
