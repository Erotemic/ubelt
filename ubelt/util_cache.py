"""
This module exposes :class:`Cacher` and :class:`CacheStamp` classes, which
provide a simple API for on-disk caching.

The :class:`Cacher` class is the simplest and most direct method of caching. In
fact, it only requires four lines of boilerplate, which is the smallest
general and robust way that I (Jon Crall) have achieved, and I don't think its
possible to do better.  These four lines implement the following necessary and
sufficient steps for general robust on-disk caching.

    1. Defining the cache dependencies
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

While the above two are equivalent, the second version provides a simpler
traceback, explicit procedures, and makes it easier to use breakpoint debugging
(because there is no closure scope).

While :class:`Cacher` is used to store direct results of in-line code in a
pickle format, the :class:`CacheStamp` object is used to cache processes that
produces an on-disk side effects other than the main return value. For
instance, consider the following example:

Example:
    >>> import ubelt as ub
    >>> def compute_many_files(dpath):
    ...     for i in range(10):
    ...         fpath = '{}/file{}.txt'.format(dpath, i)
    ...         with open(fpath, 'w') as file:
    ...             file.write('foo' + str(i))
    >>> dpath = ub.Path.appdir('ubelt/demo/cache').delete().ensuredir()
    >>> # You must specify a directory, unlike in Cacher where it is optional
    >>> self = ub.CacheStamp('name', dpath=dpath, depends={'a': 1, 'b': 2})
    >>> if self.expired():
    >>>     compute_many_files(dpath)
    >>>     # Instead of caching the whole processes, we just write a file
    >>>     # that signals the process has been done.
    >>>     self.renew()
    >>> assert not self.expired()

The CacheStamp is lightweight in that it simply marks that a process has been
completed, but the job of saving / loading the actual data is left to the
developer. The ``expired`` method checks if the stamp exists, and ``renew``
writes the stamp to disk.

In ubelt version 1.1.0, several additional features were added to CacheStamp.
In addition to specifying parameters via ``depends``, it is also possible for
CacheStamp to determine if an associated file has been modified. To do this,
the paths of the files must be known a-priori and passed to CacheStamp via the
``product`` argument. This will allow the CacheStamp to detect if the files
have been modified since the ``renew`` method was called. It does this by
remembering the size, modified time, and checksum of each file.  If the hash of
the expected hash of the product is known in advance, it is also possible to
specify the expected ``hash_prefix`` of each product. In this case, ``renew``
will raise an Exception if this specified hash prefix does not match the files
on disk. Lastly, it is possible to specify an expiration time via ``expires``,
after which the CacheStamp will always be marked as invalid. This is now the
mechanism via which the cache in :func:`ubelt.util_download.grabdata` works.

Example:
    >>> import ubelt as ub
    >>> dpath = ub.Path.appdir('ubelt/demo/cache').delete().ensuredir()
    >>> params = {'a': 1, 'b': 2}
    >>> expected_fpaths = [dpath / 'file{}.txt'.format(i) for i in range(2)]
    >>> hash_prefix = ['a7a8a91659601590e17191301dc1',
    ...                '55ae75d991c770d8f3ef07cbfde1']
    >>> self = ub.CacheStamp('name', dpath=dpath, depends=params,
    >>>                      hash_prefix=hash_prefix, hasher='sha256',
    >>>                      product=expected_fpaths, expires='2101-01-01T000000Z')
    >>> if self.expired():
    >>>     for fpath in expected_fpaths:
    ...         fpath.write_text(fpath.name)
    >>>     self.renew()
    >>> # modifying or removing the file will cause the stamp to expire
    >>> expected_fpaths[0].write_text('corrupted')
    >>> assert self.expired()


RelatedWork:
    https://github.com/shaypal5/cachier
"""
import os
from os.path import join, normpath, basename, exists


class Cacher(object):
    """
    Saves data to disk and reloads it based on specified dependencies.

    Cacher uses pickle to save/load data to/from disk. Dependencies of the
    cached process can be specified, which ensures the cached data is
    recomputed if the dependencies change. If the location of the cache is not
    specified, it will default to the system user's cache directory.

    Args:
        fname (str):
            A file name. This is the prefix that will be used by the cache. It
            will always be used as-is.

        depends (str | List[str] | None):
            Indicate dependencies of this cache.  If the dependencies change,
            then the cache is recomputed.  New in version 0.8.9, replaces
            ``cfgstr``.

        dpath (str | PathLike | None):
            Specifies where to save the cache. If unspecified, Cacher defaults
            to an application cache dir as given by appname. See
            :func:`ub.get_app_cache_dir` for more details.

        appname (str, default='ubelt'): Application name
            Specifies a folder in the application cache directory where to
            cache the data if ``dpath`` is not specified.

        ext (str, default='.pkl'):
            File extension for the cache format. Can be ``'.pkl'`` or
            ``'.json'``.

        meta (object | None):
            Metadata that is also saved with the ``cfgstr``.  This can be
            useful to indicate how the ``cfgstr`` was constructed.
            Note: this is a candidate for deprecation.

        verbose (int, default=1): Level of verbosity. Can be 1, 2 or 3.

        enabled (bool, default=True): If set to False, then the load and save
            methods will do nothing.

        log (Callable[[str], Any]):
            Overloads the print function. Useful for sending output to loggers
            (e.g. logging.info, tqdm.tqdm.write, ...)

        hasher (str, default='sha1'):
            Type of hashing algorithm to use if ``cfgstr`` needs to be
            condensed to less than 49 characters.

        protocol (int, default=-1): Protocol version used by pickle.
            Defaults to the -1 which is the latest protocol.

        backend (str):
            Set to either ``'pickle'`` or ``'json'`` to force backend. Defaults
            to auto which chooses one based on the extension.

        cfgstr (str | None):
            Deprecated in favor of ``depends``.

    Example:
        >>> import ubelt as ub
        >>> depends = 'repr-of-params-that-uniquely-determine-the-process'
        >>> # Create a cacher and try loading the data
        >>> cacher = ub.Cacher('demo_process', depends, verbose=4)
        >>> cacher.clear()
        >>> print(f'cacher.fpath={cacher.fpath}')
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
                 hasher='sha1', protocol=-1, cfgstr=None, backend='auto'):

        if depends is None:
            depends = cfgstr

        if cfgstr is not None:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Use depends instead', name='cfgstr',
                type='Cacher class arg', deprecate='1.1.0', error='1.3.0',
                remove='1.4.0',
            )
            depends = cfgstr

        if verbose is None:
            verbose = self.VERBOSE
        if dpath is None:  # pragma: no branch
            from ubelt import util_path
            dpath = os.fspath(util_path.Path.appdir(appname, type='cache'))

        if backend == 'auto':
            if ext == '.pkl':
                backend = 'pickle'
            elif ext == '.json':
                backend = 'json'
            else:
                backend = 'pickle'
        else:
            if backend not in {'json', 'pickel'}:
                raise ValueError(backend)

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
        self.backend = backend
        if len(self.ext) > 0 and self.ext[0] != '.':
            raise ValueError('Please be explicit and use a dot in ext')

    def _rectify_cfgstr(self, cfgstr=None):
        if cfgstr is not None:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration=(
                    'In general, you should not need to specify a custom '
                    'cfgstr after the Cacher has been created. '
                    'If you must, then you can modify the ``depends`` class '
                    'attribute instead, but in general it is recommend to '
                    'avoid this.'
                ), name='cfgstr', type='Cacher method arg', deprecate='1.1.0',
                error='1.3.0', remove='1.4.0',
            )

        cfgstr = self.cfgstr if cfgstr is None else cfgstr

        if cfgstr is None and self.depends is not None:
            from ubelt import util_hash
            # lazy hashing of depends data into cfgstr
            if isinstance(self.depends, str):
                self.cfgstr = self.depends
            else:
                self.cfgstr = util_hash.hash_data(self.depends)
            cfgstr = self.cfgstr

        if cfgstr is None and self.enabled:
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

    @property
    def fpath(self):
        import ubelt as ub
        return ub.Path(self.get_fpath())

    def get_fpath(self, cfgstr=None):
        """
        Reports the filepath that the cacher will use.

        It will attempt to use '{fname}_{cfgstr}{ext}' unless that is too long.
        Then cfgstr will be hashed.

        Args:
            cfgstr (str | None): overrides the instance-level cfgstr

        Returns:
            str | PathLike

        Example:
            >>> # xdoctest: +REQUIRES(module:pytest)
            >>> from ubelt.util_cache import Cacher
            >>> import pytest
            >>> #with pytest.warns(UserWarning):
            >>> if 1:  # we no longer warn here
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
            cfgstr (str | None): overrides the instance-level cfgstr

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
            >>> # Ensure that some data exists
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir(
            >>>     'ubelt/tests/util_cache',
            >>>     'test-existing-versions').delete().ensuredir()
            >>> cacher = ub.Cacher('versioned_data_v2', depends='1', dpath=dpath)
            >>> cacher.ensure(lambda: 'data1')
            >>> known_fpaths = set()
            >>> known_fpaths.add(cacher.get_fpath())
            >>> cacher = ub.Cacher('versioned_data_v2', depends='2', dpath=dpath)
            >>> cacher.ensure(lambda: 'data2')
            >>> known_fpaths.add(cacher.get_fpath())
            >>> # List previously computed configs for this type
            >>> from os.path import basename
            >>> cacher = ub.Cacher('versioned_data_v2', depends='2', dpath=dpath)
            >>> exist_fpaths = set(cacher.existing_versions())
            >>> exist_fnames = list(map(basename, exist_fpaths))
            >>> print('exist_fnames = {!r}'.format(exist_fnames))
            >>> print('exist_fpaths = {!r}'.format(exist_fpaths))
            >>> print('known_fpaths={!r}'.format(known_fpaths))
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
            cfgstr (str | None): overrides the instance-level cfgstr
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
            cfgstr (str | None): overrides the instance-level cfgstr

            on_error (str, default='raise'):
                How to handle non-io errors errors. Either 'raise', which
                re-raises the exception, or 'clear' which deletes the cache and
                returns None.

        Returns:
            None | object:
                the cached data if it exists, otherwise returns None
        """
        # cfgstr = self._rectify_cfgstr(cfgstr)
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
            cfgstr (str | None): overrides the instance-level cfgstr

        Returns:
            object: the cached data

        Raises:
            IOError - if the data is unable to be loaded. This could be due to
                a cache miss or because the cache is disabled.

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher = Cacher('test_disabled_load', '', enabled=True,
            >>>                 appname='ubelt/tests/util_cache')
            >>> cacher.save('data')
            >>> assert cacher.load() == 'data'
            >>> cacher.enabled = False
            >>> assert cacher.tryload() is None
        """
        cfgstr_ = self._rectify_cfgstr(cfgstr)

        dpath = self.dpath
        fname = self.fname
        verbose = self.verbose

        if not self.enabled:
            if verbose > 1:
                self.log('[cacher] ... cache disabled: fname={}'.format(
                    self.fname))
            raise IOError(3, 'Cache Loading Is Disabled')

        data_fpath = self.get_fpath(cfgstr=cfgstr)

        if not exists(data_fpath):
            if verbose > 2:
                self.log('[cacher] ... cache does not exist: '
                         'dpath={} fname={} cfgstr={}'.format(
                             basename(dpath), fname, cfgstr_))
            raise IOError(2, 'No such file or directory: {!r}'.format(data_fpath))
        else:
            if verbose > 3:
                sizestr = _byte_str(os.stat(data_fpath).st_size)
                self.log('[cacher] ... cache exists: '
                         'dpath={} fname={} cfgstr={}, size={}'.format(
                             basename(dpath), fname, cfgstr_, sizestr))
        try:
            data = self._backend_load(data_fpath)
        except Exception as ex:
            if verbose > 0:
                self.log('CORRUPTED? fpath = {!r}'.format(data_fpath))
            if verbose > 1:
                self.log('[cacher] ... CORRUPTED? dpath={} cfgstr={}'.format(
                    basename(dpath), cfgstr_))
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
        Writes data to path specified by ``self.fpath``.

        Metadata containing information about the cache will also be appended
        to an adjacent file with the `.meta` suffix.

        Args:
            data (object): arbitrary pickleable object to be cached
            cfgstr (str | None): overrides the instance-level cfgstr

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Normal functioning
            >>> depends = 'long-cfg' * 32
            >>> cacher = Cacher('test_enabled_save', depends=depends,
            >>>                 appname='ubelt/tests/util_cache')
            >>> cacher.save('data')
            >>> assert exists(cacher.get_fpath()), 'should be enabled'
            >>> assert exists(cacher.get_fpath() + '.meta'), 'missing metadata'
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher2 = Cacher('test_disabled_save', 'params', enabled=False,
            >>>                  appname='ubelt/tests/util_cache')
            >>> cacher2.save('data')
            >>> assert not exists(cacher2.get_fpath()), 'should be disabled'
        """
        from ubelt import util_path
        from ubelt import util_time
        if not self.enabled:
            return
        if self.verbose > 0:
            self.log('[cacher] ... {} cache save'.format(self.fname))

        cfgstr_ = self._rectify_cfgstr(cfgstr)
        condensed = self._condense_cfgstr(cfgstr)

        # Make sure the cache directory exists
        util_path.ensuredir(self.dpath)

        data_fpath = self.get_fpath(cfgstr=cfgstr)
        meta_fpath = data_fpath + '.meta'

        # Also save metadata file to reconstruct hashing
        # This may be deprecated in the future.
        with open(meta_fpath, 'a') as file_:
            # TODO: maybe append this in json or YML format?
            file_.write('\n\nsaving {}\n'.format(util_time.timestamp()))
            file_.write(self.fname + '\n')
            file_.write(condensed + '\n')
            file_.write(cfgstr_ + '\n')
            file_.write(str(self.meta) + '\n')

        self._backend_dump(data_fpath, data)

        if self.verbose > 3:
            sizestr = _byte_str(os.stat(data_fpath).st_size)
            self.log('[cacher] ... finish save, size={}'.format(sizestr))

    def _backend_load(self, data_fpath):
        """
        Example:
            >>> import ubelt as ub
            >>> cacher = ub.Cacher('test_other_backend', depends=['a'], ext='.json')
            >>> cacher.save(['data'])
            >>> cacher.tryload()

            >>> import ubelt as ub
            >>> cacher = ub.Cacher('test_other_backend2', depends=['a'], ext='.yaml', backend='json')
            >>> cacher.save({'data': [1, 2, 3]})
            >>> cacher.tryload()

            >>> import pytest
            >>> with pytest.raises(ValueError):
            >>>     ub.Cacher('test_other_backend2', depends=['a'], ext='.yaml', backend='does-not-exist')
            >>> cacher = ub.Cacher('test_other_backend2', depends=['a'], ext='.really-a-pickle', backend='auto')
            >>> assert cacher.backend == 'pickle', 'should be default'
        """
        if self.backend == 'pickle':
            import pickle
            with open(data_fpath, 'rb') as file_:
                data = pickle.load(file_)
        elif self.backend == 'json':
            import json
            with open(data_fpath, 'r') as file_:
                data = json.load(file_)
        else:
            raise NotImplementedError('self.backend = {}'.format(self.backend))
        return data

    def _backend_dump(self, data_fpath, data):
        if self.backend == 'pickle':
            import pickle
            with open(data_fpath, 'wb') as file_:
                pickle.dump(data, file_, protocol=self.protocol)
        elif self.backend == 'json':
            import json
            with open(data_fpath, 'w') as file_:
                json.dump(data, file_)
        else:
            raise NotImplementedError('self.backend = {}'.format(self.backend))
        return data

    def ensure(self, func, *args, **kwargs):
        """
        Wraps around a function. A cfgstr must be stored in the base cacher.

        Args:
            func (Callable): function that will compute data on cache miss
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
        # Can't return arguments because cfgstr won't take them into account
        def _wrapper():
            data = self.ensure(func)
            return data
        _wrapper.cacher = self
        return _wrapper


class CacheStamp(object):
    """
    Quickly determine if a file-producing computation has been done.

    Check if the computation needs to be redone by calling ``expired``.  If the
    stamp is not expired, the user can expect that the results exist and could
    be loaded. If the stamp is expired, the computation should be redone.
    After the result is updated, the calls ``renew``, which writes a "stamp"
    file to disk that marks that the procedure has been done.

    There are several ways to control how a stamp expires. At a bare minimum,
    removing the stamp file will force expiration. However, in this
    circumstance CacheStamp only knows that something has been done, but it
    doesn't have any information about what was done, so in general this is not
    sufficient.

    To achieve more robust expiration behavior, the user should specify the
    ``product`` argument, which is a list of file paths that are expected to
    exist whenever the stamp is renewed. When this is specified the CacheStamp
    will expire if any of these products are deleted, their size changes, their
    modified timestamp changes, or their hash (i.e. checksum) changes. Note
    that by setting ``hasher=None``, running and verifying checksums can be
    disabled.

    If the user knows what the hash of the file should be this can be specified
    to prevent renewal of the stamp unless these match the files on disk. This
    can be useful for security purposes.

    The stamp can also be set to expire at a specified time or after a
    specified duration using the ``expires`` argument.

    Args:
        fname (str):
            Name of the stamp file

        dpath (str | PathLike | None):
            Where to store the cached stamp file

        product (str | PathLike | Sequence[str | PathLike] | None):
            Path or paths that we expect the computation to produce. If
            specified the hash of the paths are stored.

        hasher (str, default='sha1'):
            The type of hasher used to compute the file hash of product.
            If None, then we assume the file has not been corrupted or changed
            if the mtime and size are the same. Defaults to sha1.

        verbose (bool, default=None):
            Passed to internal :class:`ubelt.Cacher` object

        enabled (bool, default=True):
            if False, expired always returns True

        depends (str | List[str] | None):
            Indicate dependencies of this cache.  If the dependencies change,
            then the cache is recomputed.  New to CacheStamp in version 0.9.2.

        meta (object | None):
            Metadata that is also saved as a sidecar file.
            New to CacheStamp in version 0.9.2.  Note: this is a candidate for
            deprecation.

        expires (str | int | datetime.datetime | datetime.timedelta | None):
            If specified, sets an expiration date for the certificate. This can
            be an absolute datetime or a timedelta offset. If specified as an
            int, this is interpreted as a time delta in seconds.  If specified
            as a str, this is interpreted as an absolute timestamp. Time delta
            offsets are coerced to absolute times at "renew" time.

        hash_prefix (None | str | List[str]):
            If specified, we verify that these match the hash(s) of the
            product(s) in the stamp certificate.

        ext (str, default='.pkl'):
            File extension for the cache format. Can be ``'.pkl'`` or
            ``'.json'``.

        cfgstr (str | None): DEPRECATED.

    Notes:
        The size, mtime, and hash mechanism is similar to how Makefile and redo
        caches work.

    Example:
        >>> import ubelt as ub
        >>> # Stamp the computation of expensive-to-compute.txt
        >>> dpath = ub.Path.appdir('ubelt/tests/cache-stamp')
        >>> dpath.delete().ensuredir()
        >>> product = dpath / 'expensive-to-compute.txt'
        >>> self = ub.CacheStamp('somedata', depends='someconfig', dpath=dpath,
        >>>                      product=product, hasher='sha256')
        >>> self.clear()
        >>> print(f'self.fpath={self.fpath}')
        >>> if self.expired():
        >>>     product.write_text('very expensive')
        >>>     self.renew()
        >>> assert not self.expired()
        >>> # corrupting the output will cause the stamp to expire
        >>> product.write_text('very corrupted')
        >>> assert self.expired()
    """
    def __init__(self, fname, dpath, cfgstr=None, product=None, hasher='sha1',
                 verbose=None, enabled=True, depends=None, meta=None,
                 hash_prefix=None, expires=None, ext='.pkl'):
        self.cacher = Cacher(fname, cfgstr=cfgstr, dpath=dpath,
                             verbose=verbose, enabled=enabled, depends=depends,
                             meta=meta, ext=ext)
        self.product = product
        self.hasher = hasher
        self.expires = expires
        self.hash_prefix = hash_prefix

        # The user can modify these if they want to disable size or mtime
        # checks for expiration. Not sure if I want to expose it at the
        # top level API yet or not.
        self._expire_checks = {
            'size': True,
            'mtime': True,
            'hash': True,
        }

    @property
    def fpath(self):
        return self.cacher.fpath

    def clear(self):
        """
        Delete the stamp (the products are untouched)
        """
        return self.cacher.clear()

    def _get_certificate(self, cfgstr=None):
        """
        Returns the stamp certificate if it exists
        """
        certificate = self.cacher.tryload(cfgstr=cfgstr, on_error='clear')
        return certificate

    def _rectify_products(self, product=None):
        """ puts products in a normalized format """
        from ubelt import util_path
        products = self.product if product is None else product
        if products is None:
            return None
        if not isinstance(products, (list, tuple)):
            products = [products]
        products = list(map(util_path.Path, products))
        return products

    def _rectify_hash_prefixes(self):
        """ puts products in a normalized format """
        hash_prefixes = self.hash_prefix
        if hash_prefixes is None:
            return None
        if not isinstance(hash_prefixes, (list, tuple)):
            hash_prefixes = [hash_prefixes]
        return hash_prefixes

    def _product_info(self, product=None):
        """
        Compute summary info about each product on disk.
        """
        products = self._rectify_products(product)
        product_info = {}
        product_info.update(self._product_file_stats())
        if self.hasher is None:
            hasher_name = None
        else:
            if not isinstance(self.hasher, str):  # nocover
                from ubelt import schedule_deprecation
                schedule_deprecation(
                    modname='ubelt',
                    migration='Pass hasher as a string',
                    name='hasher', type='CacheStamp arg',
                    deprecate='1.1.0', error='1.3.0', remove='1.4.0')
                hasher_name = self.hasher.name
            else:
                hasher_name = self.hasher
        product_info['hasher'] = hasher_name
        product_info['hash'] = self._product_file_hash(products)
        return product_info

    def _product_file_stats(self, product=None):
        products = self._rectify_products(product)
        product_stats = [p.stat() for p in products]
        product_file_stats = {
            'mtime': [stat.st_mtime for stat in product_stats],
            'size': [stat.st_size for stat in product_stats]
        }
        return product_file_stats

    def _product_file_hash(self, product=None):
        if self.hasher is None:
            product_file_hash = None
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
        Check to see if a previously existing stamp is still valid, if the
        expected result of that computation still exists, and if all other
        expiration criteria are met.

        Args:
            cfgstr (Any): DEPRECATED

            product (Any): DEPRECATED

        Returns:
            bool | str:
                True(-thy) if the stamp is invalid, expired, or does not exist.
                When the stamp is expired, the reason for expiration is
                returned as a string. If the stamp is still valid, False is
                returned.

        Example:
            >>> import ubelt as ub
            >>> import time
            >>> import os
            >>> # Stamp the computation of expensive-to-compute.txt
            >>> dpath = ub.Path.appdir('ubelt/tests/cache-stamp-expired')
            >>> dpath.delete().ensuredir()
            >>> products = [
            >>>     dpath / 'product1.txt',
            >>>     dpath / 'product2.txt',
            >>> ]
            >>> self = ub.CacheStamp('myname', depends='myconfig', dpath=dpath,
            >>>                      product=products, hasher='sha256',
            >>>                      expires=0)
            >>> if self.expired():
            >>>     for fpath in products:
            >>>         fpath.write_text(fpath.name)
            >>>     self.renew()
            >>> fpath = products[0]
            >>> # Because we set the expiration delta to 0, we should already be expired
            >>> assert self.expired() == 'expired_cert'
            >>> # Disable the expiration date, renew and we should be ok
            >>> self.expires = None
            >>> self.renew()
            >>> assert not self.expired()
            >>> # Modify the mtime to cause expiration
            >>> orig_atime = fpath.stat().st_atime
            >>> orig_mtime = fpath.stat().st_mtime
            >>> os.utime(fpath, (orig_atime, orig_mtime + 200))
            >>> assert self.expired() == 'mtime_diff'
            >>> self.renew()
            >>> assert not self.expired()
            >>> # rewriting the file will cause the size constraint to fail
            >>> # even if we hack the mtime to be the same
            >>> orig_atime = fpath.stat().st_atime
            >>> orig_mtime = fpath.stat().st_mtime
            >>> fpath.write_text('corrupted')
            >>> os.utime(fpath, (orig_atime, orig_mtime))
            >>> assert self.expired() == 'size_diff'
            >>> self.renew()
            >>> assert not self.expired()
            >>> # Force a situation where the hash is the only thing
            >>> # that saves us, write a different file with the same
            >>> # size and mtime.
            >>> orig_atime = fpath.stat().st_atime
            >>> orig_mtime = fpath.stat().st_mtime
            >>> fpath.write_text('corrApted')
            >>> os.utime(fpath, (orig_atime, orig_mtime))
            >>> assert self.expired() == 'hash_diff'
            >>> # Test what a wrong hash prefix causes expiration
            >>> certificate = self.renew()
            >>> self.hash_prefix = certificate['hash']
            >>> self.expired()
            >>> self.hash_prefix = ['bad', 'hashes']
            >>> self.expired()
            >>> # A bad hash will not allow us to renew
            >>> import pytest
            >>> with pytest.raises(RuntimeError):
            ...     self.renew()
        """
        if cfgstr is not None:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Do not pass cfgstr to expired. Use the class depends arg',
                name='cfgstr', type='CacheStamp.expires arg',
                deprecate='1.1.0', error='1.3.0', remove='1.4.0',
            )
        if product is not None:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Do not pass product to expired. Use the class product arg',
                name='product', type='CacheStamp.expires arg',
                deprecate='1.1.0', error='1.3.0', remove='1.4.0',
            )

        if not self.cacher.enabled:
            return 'disabled'

        certificate = self._get_certificate(cfgstr=cfgstr)
        if certificate is None:
            # We don't have a certificate, so we are expired
            err = 'no_cert'
            if self.cacher.verbose > 0:  # pragma: nobranch
                print('[cacher] stamp expired {}'.format(err))
            return err

        expires = certificate.get('expires', None)
        if expires is not None:
            from ubelt import util_time
            # Need to add in the local timezone to compare against the cert.
            now = _localnow()
            expires_abs = util_time.timeparse(expires)
            if  now >= expires_abs:
                # We are expired
                err = 'expired_cert'
                if self.cacher.verbose > 0:  # pragma: nobranch
                    print('[cacher] stamp expired {}'.format(err))
                return err

        products = self._rectify_products(product)
        if products is None:
            # We don't have a product to check, so assume not expired
            return False
        elif not all(map(exists, products)):
            # We are expired if the expected product does not exist
            err = 'missing_products'
            if self.cacher.verbose > 0:  # pragma: nobranch
                print('[cacher] stamp expired {}'.format(err))
            return err
        else:
            # First test to see if the size or mtime of the files has changed
            # as a potentially quicker check. If sizes or mtimes do not exist
            # in the certificate (old ubelt version), then ignore them.
            product_file_stats = self._product_file_stats()
            sizes = certificate.get('size', None)
            if sizes is not None and self._expire_checks['size']:
                if sizes != product_file_stats['size']:
                    # The sizes are differnt, we are expired
                    err =  'size_diff'
                    if self.cacher.verbose > 0:  # pragma: nobranch
                        print('[cacher] stamp expired {}'.format(err))
                    return err
            mtimes = certificate.get('mtime', None)
            if mtimes is not None and self._expire_checks['mtime']:
                if mtimes != product_file_stats['mtime']:
                    # The sizes are differnt, we are expired
                    err = 'mtime_diff'
                    if self.cacher.verbose > 0:  # pragma: nobranch
                        print('[cacher] stamp expired {}'.format(err))
                    return err

            err = self._check_certificate_hashes(certificate)
            if err:
                return err

            # We are expired if the hash of the existing product data
            # does not match the expected hash in the certificate
            if self._expire_checks['hash']:
                certificate_hash = certificate.get('hash', None)
                product_file_hash = self._product_file_hash(products)
                if product_file_hash != certificate_hash:
                    if self.cacher.verbose > 0:
                        print('invalid hash value (expected "{}", got "{}")'.format(
                            product_file_hash, certificate_hash))
                    # The hash is different, we are expired
                    err = 'hash_diff'
                    if self.cacher.verbose > 0:
                        print('[cacher] stamp expired {}'.format(err))
                    return err

        # All tests passed, we are not expired
        return False

    def _check_certificate_hashes(self, certificate):
        certificate_hash = certificate.get('hash', None)
        hash_prefixes = self._rectify_hash_prefixes()
        if hash_prefixes is not None:
            for pref_hash, cert_hash in zip(hash_prefixes, certificate_hash):
                if not cert_hash.startswith(pref_hash):
                    if self.cacher.verbose > 0:
                        print('invalid hash prefix value (expected "{}", got "{}")'.format(
                            pref_hash, cert_hash))
                    err = 'hash_prefix_mismatch'
                    return err

    def _expires(self, now=None):
        """
        Returns:
            datetime.datetime: the absolute local time when the stamp expires

        Example:
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('ubelt/tests/cache-stamp-expires')
            >>> self = ub.CacheStamp('myname', depends='myconfig', dpath=dpath)
            >>> # Test str input
            >>> self.expires = '2020-01-01T000000Z'
            >>> assert self._expires().replace(tzinfo=None).isoformat() == '2020-01-01T00:00:00'
            >>> # Test datetime input
            >>> dt = ub.timeparse(ub.timestamp())
            >>> self.expires = dt
            >>> assert self._expires() == dt
            >>> # Test None input
            >>> self.expires = None
            >>> assert self._expires() is None
            >>> # Test int input
            >>> self.expires = 0
            >>> assert self._expires(dt) == dt
            >>> self.expires = 10
            >>> assert self._expires(dt) > dt
            >>> self.expires = -10
            >>> assert self._expires(dt) < dt
            >>> # Test timedelta input
            >>> import datetime as datetime_mod
            >>> self.expires = datetime_mod.timedelta(seconds=-10)
            >>> assert self._expires(dt) == dt + self.expires
        """
        # Rectify into a datetime
        from ubelt import util_time
        import datetime as datetime_mod
        import numbers
        if now is None:
            now = datetime_mod.datetime.now()
        expires = self.expires
        if expires is None:
            expires_abs = None
        elif isinstance(expires, numbers.Number):
            expires_abs = now + datetime_mod.timedelta(seconds=expires)
        elif isinstance(expires, datetime_mod.timedelta):
            expires_abs = now + expires
        elif isinstance(expires, str):
            expires_abs = util_time.timeparse(expires)
        elif isinstance(expires, datetime_mod.datetime):
            expires_abs = expires
        else:
            raise TypeError(
                'expires must be a coercable to datetime or timedelta')
        return expires_abs

    def _new_certificate(self, cfgstr=None, product=None):
        """
        Returns:
            dict: certificate information

        Example:
            >>> import ubelt as ub
            >>> # Stamp the computation of expensive-to-compute.txt
            >>> dpath = ub.Path.appdir('ubelt/tests/cache-stamp-cert').ensuredir()
            >>> product = dpath / 'product1.txt'
            >>> product.write_text('hi')
            >>> self = ub.CacheStamp('myname', depends='myconfig', dpath=dpath,
            >>>                      product=product)
            >>> cert = self._new_certificate()
            >>> assert cert['expires'] is None
            >>> self.expires = '2020-01-01T000000'
            >>> self.renew()
            >>> cert = self._new_certificate()
            >>> assert cert['expires'] is not None
        """
        from ubelt import util_time
        products = self._rectify_products(product)
        now = _localnow()
        expires = self._expires(now)
        certificate = {
            'timestamp': util_time.timestamp(now, precision=4),
            'expires': None if expires is None else util_time.timestamp(expires, precision=4),
            'product': None if products is None else [os.fspath(p) for p in products],
        }
        if products is not None:
            if not all(map(exists, products)):
                raise IOError(
                    'The stamped product must exist: {}'.format(products))
            product_info = self._product_info(products)
            certificate.update(product_info)
        return certificate

    def renew(self, cfgstr=None, product=None):
        """
        Recertify that the product has been recomputed by writing a new
        certificate to disk.

        Returns:
            None | dict: certificate information if enabled otherwise None.

        Example:
            >>> # Test that renew does nothing when the cacher is disabled
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('ubelt/tests/cache-stamp-renew').ensuredir()
            >>> self = ub.CacheStamp('foo', dpath=dpath, enabled=False)
            >>> assert self.renew() is None
        """
        if not self.cacher.enabled:
            return None
        if cfgstr is not None:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Do not pass cfgstr to renew. Use the class depends arg',
                name='cfgstr', type='CacheStamp.renew arg',
                deprecate='1.1.0', error='1.3.0', remove='1.4.0',
            )
        if product is not None:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Do not pass product to renew. Use the class product arg',
                name='product', type='CacheStamp.renew arg',
                deprecate='1.1.0', error='1.3.0', remove='1.4.0',
            )
        certificate = self._new_certificate(cfgstr, product)
        err = self._check_certificate_hashes(certificate)
        if err:
            raise RuntimeError(err)
        self.cacher.save(certificate, cfgstr=cfgstr)
        return certificate


def _localnow():
    # Might be nice to have a util_time function add in tzinfo
    import datetime as datetime_mod
    import time
    local_tzinfo = datetime_mod.timezone(datetime_mod.timedelta(seconds=-time.timezone))
    now = datetime_mod.datetime.now().replace(tzinfo=local_tzinfo)
    return now


def _byte_str(num, unit='auto', precision=2):
    """
    Automatically chooses relevant unit (KB, MB, or GB) for displaying some
    number of bytes.

    Args:
        num (int): number of bytes
        unit (str): which unit to use, can be auto, B, KB, MB, GB, or TB

    References:
        .. [WikiOrdersOfMag] https://en.wikipedia.org/wiki/Orders_of_magnitude_(data)

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
