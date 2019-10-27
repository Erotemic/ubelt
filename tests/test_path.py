from os.path import exists
import ubelt as ub


def test_pathlib():
    try:
        import pathlib
        base = pathlib.Path(ub.ensure_app_cache_dir('ubelt'))
        dpath = base.joinpath('test_pathlib_mkdir')

        # ensuredir
        ub.delete(dpath)
        assert not dpath.exists()
        got = ub.ensuredir(dpath)
        assert got.exists()

        # compressuser
        assert ub.compressuser(base) == '~/.cache/ubelt'

        assert ub.augpath(base, prefix='foo') == '/home/joncrall/.cache/fooubelt'

        ub.expandpath(base)

    except Exception:
        import pytest
        pytest.skip('pathlib is not installed')


def test_tempdir():
    temp = ub.TempDir()
    assert temp.dpath is None
    temp.ensure()
    assert exists(temp.dpath)
    # Double ensure for coverage
    temp.ensure()
    assert exists(temp.dpath)

    dpath = temp.dpath
    temp.cleanup()
    assert not exists(dpath)
    assert temp.dpath is None


def test_augpath_identity():
    assert ub.augpath('foo') == 'foo'
    assert ub.augpath('foo/bar') == 'foo/bar'
    assert ub.augpath('') == ''


def test_augpath_dpath():
    assert ub.augpath('foo', dpath='bar') == 'bar/foo'
    assert ub.augpath('foo/bar', dpath='baz') == 'baz/bar'
    assert ub.augpath('', dpath='bar').startswith('bar')


def test_ensuredir_recreate():
    ub.ensuredir('foo', recreate=True)
    ub.ensuredir('foo/bar')
    assert exists('foo/bar')
    ub.ensuredir('foo', recreate=True)
    assert not exists('foo/bar')
