import ubelt as ub
from os.path import expanduser, basename


def test_compressuser_without_home():
    username = basename(expanduser('~'))
    not_the_user = 'foobar_' + username
    ub.shrinkuser(not_the_user) == not_the_user


def test_find_path_no_path():
    candidates = list(ub.find_path('does-not-exist', path=[]))
    assert len(candidates) == 0


if __name__ == '__main__':
    """
        pytest ubelt/tests/test_platform.py
    """

    import xdoctest
    xdoctest.doctest_module(__file__)
