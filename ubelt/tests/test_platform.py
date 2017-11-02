import ubelt as ub
import pytest
import sys
from os.path import expanduser, basename


def test_compressuser_without_home():
    username = basename(expanduser('~'))
    not_the_user = 'foobar_' + username
    ub.compressuser(not_the_user) == not_the_user


def test_cmd_stdout():
    with ub.CaptureStdout() as cap:
        result = ub.cmd('echo hello stdout', verbose=True)
    assert result['out'].strip() == 'hello stdout'
    assert cap.text.strip() == 'hello stdout'


def test_cmd_stdout_quiet():
    with ub.CaptureStdout() as cap:
        result = ub.cmd('echo hello stdout', verbose=False)
    assert result['out'].strip() == 'hello stdout', 'should still capture internally'
    assert cap.text.strip() == '', 'nothing should print to stdout'


def test_cmd_stderr():
    result = ub.cmd('echo hello stderr 1>&2', shell=True, verbose=True)
    assert result['err'].strip() == 'hello stderr'


def test_cmd_multiline_stdout():
    import threading
    # check which threads currently exist (ideally 1)
    existing_threads = list(threading.enumerate())
    print('existing_threads = {!r}'.format(existing_threads))

    command = 'python -c "for i in range(100): print(str(i))"'
    result = ub.cmd(command, verbose=2)
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'

    after_threads = list(threading.enumerate())
    print('after_threads = {!r}'.format(after_threads))
    assert len(existing_threads) <= len(after_threads), (
        'we should be cleaning up our threads')


@pytest.mark.skipif(sys.platform == 'win32',
                    reason="does not run on windows")
def test_cmd_interleaved_streams_sh():
    """
    A test that ``Crosses the Streams''
    """
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
    result = ub.cmd(sh_script, shell=True, verbose=2)

    assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
    assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'


@pytest.mark.skipif(sys.platform == 'win32',
                    reason="does not run on windows")
def test_cmd_interleaved_streams_py():
    # apparently multiline quotes dont work on win32
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
    result = ub.cmd(py_script, verbose=2)

    assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
    assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'
