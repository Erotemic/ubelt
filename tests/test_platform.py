import ubelt as ub
from os.path import expanduser, basename


def test_compressuser_without_home():
    username = basename(expanduser('~'))
    not_the_user = 'foobar_' + username
    ub.shrinkuser(not_the_user) == not_the_user


def test_find_path_no_path():
    candidates = list(ub.find_path('does-not-exist', path=[]))
    assert len(candidates) == 0


def _available_prog():
    # Try and find a program that exists on the machine
    import pytest
    common_progs = ['ls', 'ping', 'which']
    prog_name = None
    for cand_prog_name in common_progs:
        if ub.find_exe(cand_prog_name):
            prog_name = cand_prog_name
            break
    else:
        pytest.skip((
            'Common progs {} are not installed. '
            'Are we on a weird machine?').format(common_progs))
    return prog_name


def test_find_exe_idempotence():
    prog_name = _available_prog()
    prog_fpath = ub.find_exe(prog_name)
    assert prog_fpath == ub.find_exe(prog_fpath), (
        'find_exe with an existing path should work')


def test_find_exe_no_exist():
    assert ub.find_exe('!noexist', multi=False) is None, (
        'multi=False not found should return None')
    assert ub.find_exe('!noexist', multi=True) == [], (
        'multi=True not found should return an empty list')


if __name__ == '__main__':
    """
        pytest ubelt/tests/test_platform.py
    """

    import xdoctest
    xdoctest.doctest_module(__file__)
