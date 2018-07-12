# -*- coding: utf-8 -*-
import ubelt as ub
from os.path import join


def test_cache_stamp():
    # stamp the computation of expensive-to-compute.txt
    dpath = ub.ensure_app_cache_dir('ubelt', 'test-cache-stamp')
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = join(dpath, 'expensive-to-compute.txt')
    self = ub.CacheStamp('test1', dpath=dpath, cfgstr='test1',
                         product=product, hasher=None)
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    # corrupting the output will not expire in non-robust mode
    ub.writeto(product, 'corrupted')
    assert not self.expired()
    self.hasher = 'sha1'
    # but it will expire if we are in robust mode
    assert self.expired()
    # deleting the product will cause expiration in any mode
    self.hasher = None
    ub.delete(product)
    assert self.expired()


def test_cache_stamp_corrupt_product_nohasher():
    dpath = ub.ensure_app_cache_dir('ubelt', 'test-cache-stamp')
    name = 'corrupt_product_nohasher'
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = join(dpath, name + '.txt')
    self = ub.CacheStamp(name, dpath=dpath, cfgstr=name, product=product,
                         hasher=None)
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    # corrupting the output will not expire in non-robust mode
    ub.writeto(product, 'corrupted')
    assert not self.expired()


def test_cache_stamp_corrupt_product_hasher():
    dpath = ub.ensure_app_cache_dir('ubelt', 'test-cache-stamp')
    name = 'corrupt_product_hasher'
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = join(dpath, name + '.txt')
    self = ub.CacheStamp(name, dpath=dpath, cfgstr=name, product=product,
                         hasher='sha1')
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    # corrupting the output will not expire in non-robust mode
    ub.writeto(product, 'corrupted')
    assert self.expired()


def test_cache_stamp_multiproduct():
    from os.path import join
    # stamp the computation of expensive-to-compute.txt
    dpath = ub.ensure_app_cache_dir('ubelt', 'test-cache-stamp')
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = [
        join(dpath, 'product1.txt'),
        join(dpath, 'product2.txt'),
        join(dpath, 'product3.txt'),
    ]
    self = ub.CacheStamp('somedata', dpath=dpath, cfgstr='someconfig',
                         product=product)
    if self.expired():
        for fpath in product:
            ub.writeto(fpath, 'very expensive')
        self.renew()
    assert not self.expired()
    ub.writeto(product[1], 'corrupted')
    assert self.expired()


def test_cache_stamp_noproduct():
    from os.path import join
    # stamp the computation of expensive-to-compute.txt
    dpath = ub.ensure_app_cache_dir('ubelt', 'test-cache-stamp')
    ub.delete(dpath)
    ub.ensuredir(dpath)
    name = 'noproduct'
    product = join(dpath, name + '.txt')
    self = ub.CacheStamp('somedata', dpath=dpath, cfgstr='someconfig', product=None)
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    ub.writeto(product, 'corrupted')
    assert not self.expired()
