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
