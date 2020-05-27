# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os.path import exists
from os.path import join
from os.path import os


def test_touch():
    import ubelt as ub
    dpath = ub.ensure_app_cache_dir('ubelt')
    fpath = join(dpath, 'touch_file')
    assert not exists(fpath)
    ub.touch(fpath, verbose=True)
    assert exists(fpath)
    os.unlink(fpath)


def test_readwrite():
    import ubelt as ub
    dpath = ub.ensure_app_cache_dir('ubelt')
    fpath = dpath + '/' + 'testwrite.txt'
    if exists(fpath):
        os.remove(fpath)
    to_write = 'utf-8 symbols Δ, Й, ק, م, ๗, あ, 叶, 葉, and 말.'
    ub.writeto(fpath, to_write, verbose=True)
    read_ = ub.readfrom(fpath, verbose=True)
    assert read_ == to_write
