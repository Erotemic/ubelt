# -*- coding: utf-8 -*-
from os.path import exists
import ubelt as ub
import pytest


def test_noexist_meta_clear():
    """
    What no errors happen when an external processes removes meta
    """
    def func():
        return 'expensive result'
    cacher = ub.Cacher('name', 'params', verbose=10)
    cacher.clear()

    cacher.ensure(func)

    data_fpath = cacher.get_fpath()
    meta_fpath = data_fpath + '.meta'
    assert exists(data_fpath)
    assert exists(meta_fpath)

    ub.delete(meta_fpath)
    assert not exists(meta_fpath)
    cacher.clear()

    assert not exists(meta_fpath)
    assert not exists(data_fpath)


def test_clear_quiet():
    """
    What no errors happen when an external processes removes meta
    """
    def func():
        return 'expensive result'
    cacher = ub.Cacher('name', 'params', verbose=0)
    cacher.clear()
    cacher.clear()
    cacher.ensure(func)
    cacher.clear()


def test_corrupt():
    """
    What no errors happen when an external processes removes meta

    python ubelt/tests/test_cache.py test_corrupt
    """
    def func():
        return ['expensive result']
    cacher = ub.Cacher('name', 'params', verbose=10)
    cacher.clear()

    data = cacher.ensure(func)

    data2 = cacher.tryload()

    assert data2 == data

    # Overwrite the data with junk
    with open(cacher.get_fpath(), 'wb') as file:
        file.write(''.encode('utf8'))

    assert cacher.tryload() is None
    with pytest.raises(IOError):
        cacher.load()

    assert cacher.tryload() is None
    with open(cacher.get_fpath(), 'wb') as file:
        file.write(':junkdata:'.encode('utf8'))
    with pytest.raises(Exception):
        cacher.load()


def _setup_corrupt_cacher(verbose=0):
    def func():
        return ['expensive result']
    cacher = ub.Cacher('name', 'params', verbose=verbose)
    cacher.clear()
    cacher.ensure(func)
    # Write junk data that will cause a non-io error
    with open(cacher.get_fpath(), 'wb') as file:
        file.write(':junkdata:'.encode('utf8'))
    with pytest.raises(Exception):
        assert cacher.tryload(on_error='raise')
    assert exists(cacher.get_fpath())
    return cacher


def test_onerror_clear():
    cacher = _setup_corrupt_cacher()
    assert cacher.tryload(on_error='clear') is None
    assert not exists(cacher.get_fpath())
    cacher.clear()


def test_onerror_raise():
    cacher = _setup_corrupt_cacher(verbose=1)
    with pytest.raises(Exception):
        assert cacher.tryload(on_error='raise')
    assert exists(cacher.get_fpath())
    cacher.clear()


def test_onerror_bad_method():
    cacher = _setup_corrupt_cacher()
    assert exists(cacher.get_fpath())
    with pytest.raises(KeyError):
        assert cacher.tryload(on_error='doesnt exist')
    assert exists(cacher.get_fpath())
    cacher.clear()


def test_cache_hit():
    cacher = ub.Cacher('name', 'params', verbose=2)
    cacher.clear()
    assert not cacher.exists()
    cacher.save(['some', 'data'])
    assert cacher.exists()
    data = cacher.load()
    assert data == ['some', 'data']


def test_disable():
    """
    What no errors happen when an external processes removes meta
    """
    nonlocal_var = [0]

    def func():
        nonlocal_var[0] += 1
        return ['expensive result']
    cacher = ub.Cacher('name', 'params', verbose=10, enabled=False)

    assert nonlocal_var[0] == 0
    cacher.ensure(func)
    assert nonlocal_var[0] == 1
    cacher.ensure(func)
    assert nonlocal_var[0] == 2
    cacher.ensure(func)

    with pytest.raises(IOError):
        cacher.load()

    assert cacher.tryload(func) is None


def test_disabled_cache_stamp():
    stamp = ub.CacheStamp('foo', 'bar', enabled=False)
    assert stamp.expired() is True, 'disabled cache stamps are always expired'


def test_cache_depends():
    """
    What no errors happen when an external processes removes meta
    """
    cacher = ub.Cacher('name', depends=['a', 'b', 'c'],
                        verbose=10, enabled=False)
    cfgstr = cacher._rectify_cfgstr()
    assert cfgstr.startswith('8a82eef87cb905220841f95')

if __name__ == '__main__':
    r"""
    CommandLine:
        pytest ubelt/tests/test_cache.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
