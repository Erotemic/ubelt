# -*- coding: utf-8 -*-
"""
This module exposes :class:`Cacher` and :class:`CacheStamp` classes, which
provide a simple API for on-disk caching.

The :class:`Cacher` class is the simplest and most direct method of caching. In
fact, it only requires four lines of boilderplate, which is the smallest
general and robust way that I (Jon Crall) have achieved, and I don't think its
possible to do better.  These four lines implement the following necessary and
sufficient steps for general robust on-disk caching.

    1. Defining the cache dependenies
    2. Checking if the cache missed
    3. Loading the cache on a hit
    4. Executing the process and saving the result on a miss.

The following example illustrates these four points.

Example:
    >>> import ubelt as ub
    >>> # Define a cache name and dependencies (which is fed to `ub.hash_data`)
    >>> cacher = ub.Cacher('name', depends='set-of-deps')  # boilerplate:1
    >>> # Calling tryload will return your data on a hit and None on a miss
    >>> data = cacher.tryload(on_error='clear')            # boilerplate:2
    >>> # Check if you need to recompute your data
    >>> if data is None:                                   # boilerplate:3
    >>>     # Your code to recompute data goes here (this is not boilerplate).
    >>>     data = 'mydata'
    >>>     # Cache the computation result (via pickle)
    >>>     cacher.save(data)                              # boilerplate:4

Surprisingly this uses just as many boilerplate lines as a decorator style
cacher, but it is much more extensible. It is possible to use :class:`Cacher`
in more sophisticated ways (e.g. metadata), but the simple in-line use is often
easier and cleaner. The following example illustrates this:

Example:
    >>> import ubelt as ub

    >>> @ub.Cacher('name', depends={'dep1': 1, 'dep2': 2})  # boilerplate:1
    >>> def func():                                         # boilerplate:2
    >>>     data = 'mydata'
    >>>     return data                                     # boilerplate:3
    >>> data = func()                                       # boilerplate:4

    >>> cacher = ub.Cacher('name', depends=['dependencies'])  # boilerplate:1
    >>> data = cacher.tryload(on_error='clear')               # boilerplate:2
    >>> if data is None:                                      # boilerplate:3
    >>>     data = 'mydata'
    >>>     cacher.save(data)                                 # boilerplate:4

While the above two are equivalent, the second version provides simpler
tracebacks, explicit procedures, and makes it easier to use breakpoint
debugging (because there is no closure scope).


While :class:`Cacher` is used to store direct results of in-line code in a
pickle format, the :class:`CacheStamp` object is used to cache processes that
produces an on-disk side effects other than the main return value. For
instance, consider the following example:

Example:
    >>> def compute_many_files(dpath):
    ...     for i in range(0):
    ...         fpath = '{}/file{}.txt'.format(dpath, i)
    ...         open(fpath).write('foo' + str(i))
    >>> #
    >>> import ubelt as ub
    >>> dpath = ub.ensure_app_cache_dir('ubelt/demo/cache')
    >>> ub.delete(dpath)  # start fresh
    >>> # You must specify a directory, unlike in Cacher where it is optional
    >>> self = ub.CacheStamp('name', dpath=dpath, depends={'a': 1, 'b': 2})
    >>> if self.expired():
    >>>     compute_many_files(dpath)
    >>>     # Instead of caching the whole processes, we just write a file
    >>>     # that signals the process has been done.
    >>>     self.renew()
    >>> assert not self.expired()


TODO:
    - [ ] Remove the cfgstr-overrides?
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
from os.path import join, normpath, basename, exists
import warnings


class Cacher(object):
    """
    Cacher designed to be quickly integrated into existing scripts.

    A dependency string can be specified, which will invalidate the cache if it
    changes to an unseen value. The location

    Args:
        fname (str): A file name. This is the prefix that will be used by the
            cache. It will always be used as-is.

        depends (str | List[str]): Indicate dependencies of this cache.
            If the dependencies change, then the cache is recomputed.
            New in version 0.8.9, replaces `cfgstr`.

        dpath (PathLike): Specifies where to save the cache. If unspecified,
            Cacher defaults to an application resource dir as given by appname.

        appname (str, default='ubelt'): Application name
            Specifies a folder in the application resource directory where to
            cache the data if ``dpath`` is not specified.

        ext (str, default='.pkl'): File extension for the cache format

        meta (object): Metadata that is also saved with the ``cfgstr``.
            This can be useful to indicate how the ``cfgstr`` was constructed.

        verbose (int, default=1): Level of verbosity. Can be 1, 2 or 3.

        enabled (bool, default=True): If set to False, then the load and save
            methods will do nothing.

        log (func): Overloads the print function. Useful for sending output to
            loggers (e.g. logging.info, tqdm.tqdm.write, ...)

        hasher (str): Type of hashing algorithm to use if ``cfgstr`` needs to
            be condensed to less than 49 characters.

        protocol (int, default=-1): Protocol version used by pickle.
            Defaults to the -1 which is the latest protocol.
            If python 2 compatibility is not required, set to 2.

        cfgstr (str): Deprecated in favor of depends. Indicates the state.
            Either this string or a hash of this string will be used to
            identify the cache. A cfgstr should always be reasonably readable,
            thus it is good practice to hash extremely detailed cfgstrs to a
            reasonable readable level. Use meta to store make original details
            persist.

    Example:
        >>> import ubelt as ub
        >>> depends = 'repr-of-params-that-uniquely-determine-the-process'
        >>> # Create a cacher and try loading the data
        >>> cacher = ub.Cacher('demo_process', depends, verbose=4)
        >>> cacher.clear()
        >>> data = cacher.tryload()
        >>> if data is None:
        >>>     # Put expensive functions in if block when cacher misses
        >>>     myvar1 = 'result of expensive process'
        >>>     myvar2 = 'another result'
        >>>     # Tell the cacher to write at the end of the if block
        >>>     # It is idomatic to put results in an object named data
        >>>     data = myvar1, myvar2
        >>>     cacher.save(data)
        >>> # Last part of the Cacher pattern is to unpack the data object
        >>> myvar1, myvar2 = data
        >>> #
        >>> # If we know the data exists, we can also simply call load
        >>> data = cacher.tryload()

    Example:
        >>> # The previous example can be shorted if only a single value
        >>> from ubelt.util_cache import Cacher
        >>> depends = 'repr-of-params-that-uniquely-determine-the-process'
        >>> # Create a cacher and try loading the data
        >>> cacher = Cacher('demo_process', depends)
        >>> myvar = cacher.tryload()
        >>> if myvar is None:
        >>>     myvar = ('result of expensive process', 'another result')
        >>>     cacher.save(myvar)
        >>> assert cacher.exists(), 'should now exist'
    """
    VERBOSE = 1  # default verbosity
    FORCE_DISABLE = False  # global scope override

    def __init__(self, fname, depends=None, dpath=None, appname='ubelt',
                 ext='.pkl', meta=None, verbose=None, enabled=True, log=None,
                 hasher='sha1', protocol=-1, cfgstr=None):

        if depends is None:
            depends = cfgstr

        if cfgstr is not None:
            # We will start warning after the next version releases and a
            # stable version with depends exists on pypi.
            # import warnings
            # warnings.warn('cfgstr is deprecated, use depends instead')
            depends = cfgstr

        if verbose is None:
            verbose = self.VERBOSE
        if dpath is None:  # pragma: no branch
            from ubelt import util_platform
            dpath = util_platform.get_app_cache_dir(appname)

        self.dpath = dpath
        self.fname = fname
        self.depends = depends
        self.cfgstr = cfgstr
        self.verbose = verbose
        self.ext = ext
        self.meta = meta
        self.enabled = enabled and not self.FORCE_DISABLE
        self.protocol = protocol
        self.hasher = hasher
        self.log = print if log is None else log

        if len(self.ext) > 0 and self.ext[0] != '.':
            raise ValueError('Please be explicit and use a dot in ext')

    def _rectify_cfgstr(self, cfgstr=None):
        cfgstr = self.cfgstr if cfgstr is None else cfgstr

        if cfgstr is None and self.depends is not None:
            from ubelt import util_hash
            import six
            # lazy hashing of depends data into cfgstr
            if isinstance(self.depends, six.string_types):
                self.cfgstr = self.depends
            else:
                self.cfgstr = util_hash.hash_data(self.depends)
            cfgstr = self.cfgstr

        if cfgstr is None and self.enabled:
            warnings.warn(
                'No cfgstr given in Cacher constructor or call for {}'.format(
                    self.fname), UserWarning)
            cfgstr = ''
        if self.fname is None:
            raise AssertionError('no fname specified in Cacher')
        if self.dpath is None:
            raise AssertionError('no dpath specified in Cacher')
        return cfgstr

    def _condense_cfgstr(self, cfgstr=None):
        cfgstr = self._rectify_cfgstr(cfgstr)
        # The 49 char maxlen is just long enough for an 8 char name, an 1 char
        # underscore, and a 40 char sha1 hash.
        max_len = 49
        if len(cfgstr) > max_len:
            from ubelt import util_hash
            condensed = util_hash.hash_data(cfgstr, hasher=self.hasher,
                                            base='hex')
            condensed = condensed[0:max_len]
        else:
            condensed = cfgstr
        return condensed

    def get_fpath(self, cfgstr=None):
        """
        Reports the filepath that the cacher will use.

        It will attempt to use '{fname}_{cfgstr}{ext}' unless that is too long.
        Then cfgstr will be hashed.

        Args:
            cfgstr (str, optional): overrides the instance-level cfgstr

        Returns:
            PathLike

        Example:
            >>> # xdoctest: +REQUIRES(module:pytest)
            >>> from ubelt.util_cache import Cacher
            >>> import pytest
            >>> with pytest.warns(UserWarning):
            >>>     cacher = Cacher('test_cacher1')
            >>>     cacher.get_fpath()
            >>> self = Cacher('test_cacher2', depends='cfg1')
            >>> self.get_fpath()
            >>> self = Cacher('test_cacher3', depends='cfg1' * 32)
            >>> self.get_fpath()
        """
        condensed = self._condense_cfgstr(cfgstr)
        fname_cfgstr = '{}_{}{}'.format(self.fname, condensed, self.ext)
        fpath = join(self.dpath, fname_cfgstr)
        fpath = normpath(fpath)
        return fpath

    def exists(self, cfgstr=None):
        """
        Check to see if the cache exists

        Args:
            cfgstr (str, optional): overrides the instance-level cfgstr

        Returns:
            bool
        """
        return exists(self.get_fpath(cfgstr=cfgstr))

    def existing_versions(self):
        """
        Returns data with different cfgstr values that were previously computed
        with this cacher.

        Yields:
            str: paths to cached files corresponding to this cacher

        Example:
            >>> from ubelt.util_cache import Cacher
            >>> # Ensure that some data exists
            >>> known_fpaths = set()
            >>> import ubelt as ub
            >>> dpath = ub.ensure_app_cache_dir('ubelt',
            >>>                                 'test-existing-versions')
            >>> ub.delete(dpath)  # start fresh
            >>> cacher = Cacher('versioned_data_v2', depends='1', dpath=dpath)
            >>> cacher.ensure(lambda: 'data1')
            >>> known_fpaths.add(cacher.get_fpath())
            >>> cacher = Cacher('versioned_data_v2', depends='2', dpath=dpath)
            >>> cacher.ensure(lambda: 'data2')
            >>> known_fpaths.add(cacher.get_fpath())
            >>> # List previously computed configs for this type
            >>> from os.path import basename
            >>> cacher = Cacher('versioned_data_v2', depends='2', dpath=dpath)
            >>> exist_fpaths = set(cacher.existing_versions())
            >>> exist_fnames = list(map(basename, exist_fpaths))
            >>> print('exist_fnames = {!r}'.format(exist_fnames))
            >>> assert exist_fpaths.issubset(known_fpaths)
        """
        import glob
        pattern = join(self.dpath, self.fname + '_*' + self.ext)
        for fname in glob.iglob(pattern):
            data_fpath = join(self.dpath, fname)
            yield data_fpath

    def clear(self, cfgstr=None):
        """
        Removes the saved cache and metadata from disk

        Args:
            cfgstr (str, optional): overrides the instance-level cfgstr
        """
        data_fpath = self.get_fpath(cfgstr)
        if self.verbose > 0:
            self.log('[cacher] clear cache')
        if exists(data_fpath):
            if self.verbose > 0:
                self.log('[cacher] removing {}'.format(data_fpath))
            os.remove(data_fpath)

            # Remove the metadata if it exists
            meta_fpath = data_fpath + '.meta'
            if exists(meta_fpath):
                os.remove(meta_fpath)
        else:
            if self.verbose > 0:
                self.log('[cacher] ... nothing to clear')

    def tryload(self, cfgstr=None, on_error='raise'):
        """
        Like load, but returns None if the load fails due to a cache miss.

        Args:
            cfgstr (str, optional): overrides the instance-level cfgstr

            on_error (str, default='raise'):
                How to handle non-io errors errors. Either 'raise', which
                re-raises the exception, or 'clear' which deletes the cache and
                returns None.

        Returns:
            None | object:
                the cached data if it exists, otherwise returns None
        """
        cfgstr = self._rectify_cfgstr(cfgstr)
        if self.enabled:
            try:
                if self.verbose > 1:
                    self.log('[cacher] tryload fname={}'.format(self.fname))
                return self.load(cfgstr)
            except IOError:
                if self.verbose > 0:
                    self.log('[cacher] ... {} cache miss'.format(self.fname))
            except Exception:
                if self.verbose > 0:
                    self.log('[cacher] ... failed to load')
                if on_error == 'raise':
                    raise
                elif on_error == 'clear':
                    self.clear(cfgstr)
                    return None
                else:
                    raise KeyError('Unknown method on_error={}'.format(
                        on_error))
        else:
            if self.verbose > 1:
                self.log('[cacher] ... cache disabled: fname={}'.format(
                    self.fname))
        return None

    def load(self, cfgstr=None):
        """
        Load the data cached and raise an error if something goes wrong.

        Args:
            cfgstr (str, optional): overrides the instance-level cfgstr

        Returns:
            object: the cached data

        Raises:
            IOError - if the data is unable to be loaded. This could be due to
                a cache miss or because the cache is disabled.

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher = Cacher('test_disabled_load', '', enabled=True)
            >>> cacher.save('data')
            >>> assert cacher.load() == 'data'
            >>> cacher.enabled = False
            >>> assert cacher.tryload() is None
        """
        from six.moves import cPickle as pickle
        cfgstr = self._rectify_cfgstr(cfgstr)

        dpath = self.dpath
        fname = self.fname
        verbose = self.verbose

        if not self.enabled:
            if verbose > 1:
                self.log('[cacher] ... cache disabled: fname={}'.format(
                    self.fname))
            raise IOError(3, 'Cache Loading Is Disabled')

        fpath = self.get_fpath(cfgstr=cfgstr)

        if not exists(fpath):
            if verbose > 2:
                self.log('[cacher] ... cache does not exist: '
                         'dpath={} fname={} cfgstr={}'.format(
                             basename(dpath), fname, cfgstr))
            raise IOError(2, 'No such file or directory: %r' % (fpath,))
        else:
            if verbose > 3:
                sizestr = _byte_str(os.stat(fpath).st_size)
                self.log('[cacher] ... cache exists: '
                         'dpath={} fname={} cfgstr={}, size={}'.format(
                             basename(dpath), fname, cfgstr, sizestr))
        try:
            with open(fpath, 'rb') as file_:
                data = pickle.load(file_)
        except Exception as ex:
            if verbose > 0:
                self.log('CORRUPTED? fpath = %s' % (fpath,))
            if verbose > 1:
                self.log('[cacher] ... CORRUPTED? dpath={} cfgstr={}'.format(
                    basename(dpath), cfgstr))
            if isinstance(ex, (EOFError, IOError, ImportError)):
                raise IOError(str(ex))
            else:
                if verbose > 1:
                    self.log('[cacher] ... unknown reason for exception')
                raise
        else:
            if self.verbose > 2:
                self.log('[cacher] ... {} cache hit'.format(self.fname))
            elif verbose > 1:
                self.log('[cacher] ... cache hit')
        return data

    def save(self, data, cfgstr=None):
        """
        Writes data to path specified by `self.fpath(cfgstr)`.

        Metadata containing information about the cache will also be appended
        to an adjacent file with the `.meta` suffix.

        Args:
            data (object): arbitrary pickleable object to be cached
            cfgstr (str, optional): overrides the instance-level cfgstr

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Normal functioning
            >>> depends = 'long-cfg' * 32
            >>> cacher = Cacher('test_enabled_save', depends=depends)
            >>> cacher.save('data')
            >>> assert exists(cacher.get_fpath()), 'should be enabeled'
            >>> assert exists(cacher.get_fpath() + '.meta'), 'missing metadata'
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher2 = Cacher('test_disabled_save', 'params', enabled=False)
            >>> cacher2.save('data')
            >>> assert not exists(cacher2.get_fpath()), 'should be disabled'
        """
        from six.moves import cPickle as pickle
        from ubelt import util_path
        from ubelt import util_time
        if not self.enabled:
            return
        if self.verbose > 0:
            self.log('[cacher] ... {} cache save'.format(self.fname))

        cfgstr = self._rectify_cfgstr(cfgstr)
        condensed = self._condense_cfgstr(cfgstr)

        # Make sure the cache directory exists
        util_path.ensuredir(self.dpath)

        data_fpath = self.get_fpath(cfgstr=cfgstr)
        meta_fpath = data_fpath + '.meta'

        # Also save metadata file to reconstruct hashing
        with open(meta_fpath, 'a') as file_:
            # TODO: maybe append this in json or YML format?
            file_.write('\n\nsaving {}\n'.format(util_time.timestamp()))
            file_.write(self.fname + '\n')
            file_.write(condensed + '\n')
            file_.write(cfgstr + '\n')
            file_.write(str(self.meta) + '\n')

        with open(data_fpath, 'wb') as file_:
            # Use protocol 2 to support python2 and 3
            pickle.dump(data, file_, protocol=self.protocol)

        if self.verbose > 3:
            sizestr = _byte_str(os.stat(data_fpath).st_size)
            self.log('[cacher] ... finish save, size={}'.format(sizestr))

    def ensure(self, func, *args, **kwargs):
        """
        Wraps around a function. A cfgstr must be stored in the base cacher.

        Args:
            func (callable): function that will compute data on cache miss
            *args: passed to func
            **kwargs: passed to func

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> def func():
            >>>     return 'expensive result'
            >>> fname = 'test_cacher_ensure'
            >>> depends = 'func params'
            >>> cacher = Cacher(fname, depends=depends)
            >>> cacher.clear()
            >>> data1 = cacher.ensure(func)
            >>> data2 = cacher.ensure(func)
            >>> assert data1 == 'expensive result'
            >>> assert data1 == data2
            >>> cacher.clear()
        """
        data = self.tryload()
        if data is None:
            data = func(*args, **kwargs)
            self.save(data)
        return data

    def __call__(self, func):
        """
        Allows Cacher to be used as a decorator for functions with no
        arguments. This mode of usage has much less control than others, so it
        is only recommended for the simplest of cases.

        Args:
            func (Callable): function to decorate. Must have no arguments.

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> @Cacher('demo_cacher_call', depends='foobar')
            >>> def func():
            >>>     return 'expensive result'
            >>> func.cacher.clear()
            >>> assert not func.cacher.exists()
            >>> data = func()
            >>> assert func.cacher.exists()
            >>> func.cacher.clear()
        """
        # Cant return arguments because cfgstr wont take them into account
        def _wrapper():
            data = self.ensure(func)
            return data
        _wrapper.cacher = self
        return _wrapper


class CacheStamp(object):
    """
    Quickly determine if a file-producing computation has been done.

    Writes a file that marks that a procedure has been done by writing a
    "stamp" file to disk. Removing the stamp file will force recomputation.
    However, removing or changing the result of the computation may not trigger
    recomputation unless specific handling is done or the expected "product"
    of the computation is a file and registered with the stamper.  If
    hasher is None, we only check if the product exists, and we ignore
    its hash, otherwise it checks that the hash of the product is the same.

    Args:
        fname (str):
            Name of the stamp file

        cfgstr (str):
            Configuration associated with the stamped computation.  A common
            pattern is to call :func:`ubelt.hash_data` on a dependency list.

            Deprecated in favor of depends. Indicates the state.
            Either this string or a hash of this string will be used to
            identify the cache. A cfgstr should always be reasonably readable,
            thus it is good practice to hash extremely detailed cfgstrs to a
            reasonable readable level. Use meta to store make original details
            persist.

        dpath (PathLike):
            Where to store the cached stamp file

        product (PathLike or Sequence[PathLike], optional):
            Path or paths that we expect the computation to produce. If
            specified the hash of the paths are stored.

        hasher (str, default='sha1'):
            The type of hasher used to compute the file hash of product.
            If None, then we assume the file has not been corrupted or changed.
            Defaults to sha1.

        verbose (bool, default=None):
            Passed to internal ub.Cacher object

        enabled (bool, default=True):
            if False, expired always returns True

        depends (str | List[str]): Indicate dependencies of this cache.
            If the dependencies change, then the cache is recomputed.
            New to CacheStamp in version 0.9.2, replaces `cfgstr`.

        meta (object): Metadata that is also saved with the ``cfgstr``.
            This can be useful to indicate how the ``cfgstr`` was constructed.
            New to CacheStamp in version 0.9.2.

    TODO:
        - [ ] expiration time delta or date time (also remember when renewed)

    Example:
        >>> import ubelt as ub
        >>> from os.path import join
        >>> # Stamp the computation of expensive-to-compute.txt
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'test-cache-stamp')
        >>> ub.delete(dpath)
        >>> ub.ensuredir(dpath)
        >>> product = join(dpath, 'expensive-to-compute.txt')
        >>> self = CacheStamp('somedata', depends='someconfig', dpath=dpath,
        >>>                   product=product, hasher=None)
        >>> self.hasher = None
        >>> if self.expired():
        >>>     ub.writeto(product, 'very expensive')
        >>>     self.renew()
        >>> assert not self.expired()
        >>> # corrupting the output will not expire in non-robust mode
        >>> ub.writeto(product, 'corrupted')
        >>> assert not self.expired()
        >>> self.hasher = 'sha1'
        >>> # but it will expire if we are in robust mode
        >>> assert self.expired()
        >>> # deleting the product will cause expiration in any mode
        >>> self.hasher = None
        >>> ub.delete(product)
        >>> assert self.expired()
    """
    def __init__(self, fname, dpath, cfgstr=None, product=None, hasher='sha1',
                 verbose=None, enabled=True, depends=None, meta=None):
        self.cacher = Cacher(fname, cfgstr=cfgstr, dpath=dpath,
                             verbose=verbose, enabled=enabled, depends=depends,
                             meta=meta)
        self.product = product
        self.hasher = hasher

    def _get_certificate(self, cfgstr=None):
        """
        Returns the stamp certificate if it exists
        """
        certificate = self.cacher.tryload(cfgstr=cfgstr)
        return certificate

    def _rectify_products(self, product=None):
        """ puts products in a normalized format """
        products = self.product if product is None else product
        if products is None:
            return None
        if not isinstance(products, (list, tuple)):
            products = [products]
        return products

    def _product_file_hash(self, product=None):
        """
        Get the hash of the each product file
        """
        if self.hasher is None:
            return None
        else:
            from ubelt import util_hash
            products = self._rectify_products(product)
            product_file_hash = [
                util_hash.hash_file(p, hasher=self.hasher, base='hex')
                for p in products
            ]
            return product_file_hash

    def expired(self, cfgstr=None, product=None):
        """
        Check to see if a previously existing stamp is still valid and if the
        expected result of that computation still exists.

        Args:
            cfgstr (str, optional): overrides the instance-level cfgstr

            product (PathLike or Sequence[PathLike], optional): override the
                default product if specified

        Returns:
            bool: True if the stamp is invalid or does not exist.
        """
        if not self.cacher.enabled:
            return True
        products = self._rectify_products(product)
        certificate = self._get_certificate(cfgstr=cfgstr)
        if certificate is None:
            # We dont have a certificate, so we are expired
            is_expired = True
        elif products is None:
            # We dont have a product to check, so assume not expired
            is_expired = False
        elif not all(map(exists, products)):
            # We are expired if the expected product does not exist
            is_expired = True
        else:
            # We are expired if the hash of the existing product data
            # does not match the expected hash in the certificate
            product_file_hash = self._product_file_hash(products)
            certificate_hash = certificate.get('product_file_hash', None)
            is_expired = product_file_hash != certificate_hash
        return is_expired

    def renew(self, cfgstr=None, product=None):
        """
        Recertify that the product has been recomputed by writing a new
        certificate to disk.

        Returns:
            dict: certificate information
        """
        from ubelt import util_time
        products = self._rectify_products(product)
        certificate = {
            'timestamp': util_time.timestamp(),
            'product': products,
        }
        if products is not None:
            if not all(map(exists, products)):
                raise IOError(
                    'The stamped product must exist: {}'.format(products))
            product_hash = self._product_file_hash(products)
            certificate['product_file_hash'] = product_hash
        self.cacher.save(certificate, cfgstr=cfgstr)
        return certificate


def _byte_str(num, unit='auto', precision=2):
    """
    Automatically chooses relevant unit (KB, MB, or GB) for displaying some
    number of bytes.

    Args:
        num (int): number of bytes
        unit (str): which unit to use, can be auto, B, KB, MB, GB, or TB

    References:
        https://en.wikipedia.org/wiki/Orders_of_magnitude_(data)

    Returns:
        str: string representing the number of bytes with appropriate units

    Example:
        >>> import ubelt as ub
        >>> num_list = [1, 100, 1024,  1048576, 1073741824, 1099511627776]
        >>> result = ub.repr2(list(map(_byte_str, num_list)), nl=0)
        >>> print(result)
        ['0.00KB', '0.10KB', '1.00KB', '1.00MB', '1.00GB', '1.00TB']
        >>> _byte_str(10, unit='B')
        10.00B
    """
    abs_num = abs(num)
    if unit == 'auto':
        if abs_num < 2.0 ** 10:
            unit = 'KB'
        elif abs_num < 2.0 ** 20:
            unit = 'KB'
        elif abs_num < 2.0 ** 30:
            unit = 'MB'
        elif abs_num < 2.0 ** 40:
            unit = 'GB'
        else:
            unit = 'TB'
    if unit.lower().startswith('b'):
        num_unit = num
    elif unit.lower().startswith('k'):
        num_unit =  num / (2.0 ** 10)
    elif unit.lower().startswith('m'):
        num_unit =  num / (2.0 ** 20)
    elif unit.lower().startswith('g'):
        num_unit = num / (2.0 ** 30)
    elif unit.lower().startswith('t'):
        num_unit = num / (2.0 ** 40)
    else:
        raise ValueError('unknown num={!r} unit={!r}'.format(num, unit))
    fmtstr = ('{:.' + str(precision) + 'f}{}')
    res = fmtstr.format(num_unit, unit)
    return res


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/ubelt/util_cache.py Cacher
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
