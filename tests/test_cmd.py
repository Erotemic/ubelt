# -*- coding: utf-8 -*-
import pytest
import sys
import ubelt as ub


def test_cmd_stdout():
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


def test_cmd_tee_auto():
    """
    pytest ubelt/tests/test_cmd.py -k tee_backend
    pytest ubelt/tests/test_cmd.py
    """
    command = 'python -c "for i in range(100): print(str(i))"'
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
            pytest.skip(reason='threads cause issues with early tqdms')

    import threading
    # check which threads currently exist (ideally 1)
    existing_threads = list(threading.enumerate())
    print('existing_threads = {!r}'.format(existing_threads))

    command = 'python -c "for i in range(10): print(str(i))"'
    result = ub.cmd(command, verbose=0, tee_backend='thread')
    assert result['out'] == '\n'.join(list(map(str, range(10)))) + '\n'

    after_threads = list(threading.enumerate())
    print('after_threads = {!r}'.format(after_threads))
    assert len(existing_threads) <= len(after_threads), (
        'we should be cleaning up our threads')


@pytest.mark.skipif(sys.platform == 'win32', reason='not available on win32')
def test_cmd_tee_select():
    command = 'python -c "for i in range(100): print(str(i))"'
    result = ub.cmd(command, verbose=1, tee_backend='select')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'

    command = 'python -c "for i in range(100): print(str(i))"'
    result = ub.cmd(command, verbose=0, tee_backend='select')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='not available on win32')
def test_cmd_tee_badmethod():
    """
    pytest ubelt/tests/test_cmd.py::test_cmd_tee_badmethod
    """
    command = 'python -c "for i in range(100): print(str(i))"'
    with pytest.raises(ValueError):
        ub.cmd(command, verbose=2, tee_backend='bad tee backend')


def test_cmd_multiline_stdout():
    """
    python ubelt/tests/test_cmd.py test_cmd_multiline_stdout
    pytest ubelt/tests/test_cmd.py::test_cmd_multiline_stdout
    """
    command = 'python -c "for i in range(10): print(str(i))"'
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
            ''').lstrip()
        result = ub.cmd(py_script, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'
    else:
        # faster mode
        py_script = ub.codeblock(
            r'''
            python -c "
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
        dpath = ub.ensure_app_resource_dir('ubelt')
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


if __name__ == '__main__':
    """
        pytest ubelt/tests/test_cmd.py -s

        python ~/code/ubelt/ubelt/tests/test_cmd.py test_cmd_veryverbose
    """

    import xdoctest
    xdoctest.doctest_module(__file__)
