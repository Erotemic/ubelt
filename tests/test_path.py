# -*- coding: utf-8 -*-
from os.path import exists, join
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

        # shrinkuser
        assert ub.shrinkuser(base) == '~/.cache/ubelt'

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
    assert ub.augpath('foo/bar') == join('foo', 'bar')
    assert ub.augpath('') == ''


def test_augpath_dpath():
    assert ub.augpath('foo', dpath='bar') == join('bar', 'foo')
    assert ub.augpath('foo/bar', dpath='baz') == join('baz', 'bar')
    assert ub.augpath('', dpath='bar').startswith('bar')


def test_ensuredir_recreate():
    base = ub.ensure_app_cache_dir('ubelt/tests')
    folder = join(base, 'foo')
    member = join(folder, 'bar')
    ub.ensuredir(folder, recreate=True)
    ub.ensuredir(member)
    assert exists(member)
    ub.ensuredir(folder, recreate=True)
    assert not exists(member)


def test_ensuredir_verbosity():
    base = ub.ensure_app_cache_dir('ubelt/tests')

    with ub.CaptureStdout() as cap:
        ub.ensuredir(join(base, 'foo'), verbose=0)
    assert cap.text == ''
    # None defaults to verbose=0
    with ub.CaptureStdout() as cap:
        ub.ensuredir((base, 'foo'), verbose=None)
    assert cap.text == ''

    ub.delete(join(base, 'foo'))
    with ub.CaptureStdout() as cap:
        ub.ensuredir(join(base, 'foo'), verbose=1)
    assert 'creating' in cap.text
    with ub.CaptureStdout() as cap:
        ub.ensuredir(join(base, 'foo'), verbose=1)
    assert 'existing' in cap.text
