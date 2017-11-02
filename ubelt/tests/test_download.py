import ubelt as ub
import pytest
from os.path import basename, join, exists


def test_download_no_fpath():
    url = 'http://i.imgur.com/rqwaDag.png'

    dpath = ub.ensure_app_cache_dir('ubelt')
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(url)

    assert got_fpath == fpath
    assert exists(fpath)


def test_download_with_fpath():
    url = ' http://i.imgur.com/rqwaDag.png '

    dpath = ub.ensure_app_cache_dir('ubelt', 'tests')
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(url, fpath=fpath)
    assert got_fpath == fpath
    assert exists(fpath)


def test_grabdata_cache():
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    url = 'http://i.imgur.com/rqwaDag.png'

    dpath = ub.ensure_app_cache_dir('ubelt')
    fname = basename(url)
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url)
    assert got_fpath == fpath
    assert exists(fpath)

    ub.delete(fpath)
    assert not exists(fpath)

    ub.grabdata(url)
    assert exists(fpath)


def test_grabdata_url_only():
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    url = 'http://i.imgur.com/rqwaDag.png'

    dpath = ub.ensure_app_cache_dir('ubelt')
    fname = basename(url)
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url)
    assert got_fpath == fpath
    assert exists(fpath)


def test_grabdata_fname_only():
    url = 'http://i.imgur.com/rqwaDag.png'

    dpath = ub.ensure_app_cache_dir('ubelt')
    fname = 'mario.png'
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url, fname=fname)
    assert got_fpath == fpath
    assert exists(fpath)


def test_grabdata_dpath_only():
    url = 'http://i.imgur.com/rqwaDag.png'

    dpath = ub.ensure_app_cache_dir('ubelt', 'test')
    fname = basename(url)
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url, dpath=dpath)
    assert got_fpath == fpath
    assert exists(fpath)


def test_grabdata_fpath_and_dpath():
    url = 'http://i.imgur.com/rqwaDag.png'
    with pytest.raises(ValueError):
        ub.grabdata(url, fpath='foo', dpath='bar')
