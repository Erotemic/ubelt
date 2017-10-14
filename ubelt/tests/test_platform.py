import ubelt as ub
from os.path import expanduser


def test_compressuser():
    path = expanduser('~')
    assert path != '~'
    assert ub.compressuser(path) == '~'
    assert ub.compressuser(path + '1') == path + '1'
    assert ub.compressuser(path + '/1') == '~/1'


def test_compressuser_without_home():
    import pwd
    import os
    username = pwd.getpwuid(os.getuid()).pw_name
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
