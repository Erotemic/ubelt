from __future__ import unicode_literals
from os.path import os


def test_touch():
    import ubelt as ub
    dpath = ub.Path.appdir('ubelt', 'tests').ensuredir()
    fpath = dpath / 'touch_file'
    assert not fpath.exists()
    ub.touch(fpath, verbose=True)
    assert fpath.exists()
    os.unlink(fpath)


def test_readwrite():
    import pytest
    import ubelt as ub
    dpath = ub.Path.appdir('ubelt', 'tests').ensuredir()
    fpath = dpath / 'testwrite.txt'
    if fpath.exists():
        os.remove(fpath)
    to_write = 'utf-8 symbols Δ, Й, ק, م, ๗, あ, 叶, 葉, and 말.'
    with pytest.warns(DeprecationWarning):
        ub.writeto(fpath, to_write, verbose=True)
    with pytest.warns(DeprecationWarning):
        read_ = ub.readfrom(fpath, verbose=True)
    assert read_ == to_write
