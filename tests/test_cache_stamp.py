import ubelt as ub
from os.path import join


def test_cache_stamp():
    # stamp the computation of expensive-to-compute.txt
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = join(dpath, 'expensive-to-compute.txt')
    self = ub.CacheStamp('test1', dpath=dpath, depends='test1',
                         product=product, hasher=None)
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    # corrupting the output WILL expire in non-robust mode if the size is
    # different.
    ub.writeto(product, 'corrupted')
    assert self.expired()
    self.hasher = 'sha1'
    # but it will expire if we are in robust mode, even if the size is not
    # different
    assert self.expired()
    # deleting the product will cause expiration in any mode
    self.hasher = None
    ub.delete(product)
    assert self.expired()


def test_cache_stamp_corrupt_product_nohasher():
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    name = 'corrupt_product_nohasher'
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = join(dpath, name + '.txt')
    self = ub.CacheStamp(name, dpath=dpath, depends=name, product=product,
                         hasher=None)
    # Disable the new (as of 1.1.0) size and mtime checks
    # note: as of version 1.1.0 we also have to disable the new size and
    # mtime checks to get a non-robust mode.
    self._expire_checks['size'] = False
    self._expire_checks['mtime'] = False
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    # corrupting the output will not expire in non-robust mode
    ub.writeto(product, 'corrupted')
    assert not self.expired()


def test_not_time_expired():
    # stamp the computation of expensive-to-compute.txt
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    ub.delete(dpath)
    ub.ensuredir(dpath)
    self = ub.CacheStamp('test1', dpath=dpath, depends='test1',
                         expires=10000, hasher=None)
    self.renew()
    assert not self.expired()


def test_time_expired():
    # stamp the computation of expensive-to-compute.txt
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    ub.delete(dpath)
    ub.ensuredir(dpath)
    self = ub.CacheStamp('test1', dpath=dpath, depends='test1',
                         expires=-10000, hasher=None)
    self.renew()
    assert self.expired() == 'expired_cert'


def test_cache_stamp_corrupt_product_hasher():
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    name = 'corrupt_product_hasher'
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = join(dpath, name + '.txt')
    self = ub.CacheStamp(name, dpath=dpath, depends=name, product=product,
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
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    ub.delete(dpath)
    ub.ensuredir(dpath)
    product = [
        join(dpath, 'product1.txt'),
        join(dpath, 'product2.txt'),
        join(dpath, 'product3.txt'),
    ]
    self = ub.CacheStamp('somedata', dpath=dpath, depends='someconfig',
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
    dpath = ub.Path.appdir('ubelt/tests', 'test-cache-stamp').ensuredir()
    ub.delete(dpath)
    ub.ensuredir(dpath)
    name = 'noproduct'
    product = join(dpath, name + '.txt')
    self = ub.CacheStamp('somedata', dpath=dpath, depends='someconfig', product=None)
    if self.expired():
        ub.writeto(product, 'very expensive')
        self.renew()
    assert not self.expired()
    ub.writeto(product, 'corrupted')
    assert not self.expired()
