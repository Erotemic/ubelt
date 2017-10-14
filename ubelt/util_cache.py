# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import hashlib
from os.path import join, normpath, basename, exists
from six.moves import cPickle as pickle


class Cacher(object):
    """
    Cacher that can be quickly integrated into existing scripts.

    Args:
        fname (str): A file name. This is the prefix that will be used by the
            cache. It will alwasys be used as-is.

        cfgstr (str): indicates the state. Either this string or a hash of this
            string will be used to identify the cache. A cfgstr should always
            be reasonably readable, thus it is good practice to hash extremely
            detailed cfgstrs to a reasonable readable level. Use meta to store
            make original details persist.

        dpath (str): Specifies where to save the cache. If unspecified,
            Cacher defaults to an application resource dir as given by appname.

        appname (str): application name (default = 'ubelt')
            Specifies a folder in the application resource directory where to
            cache the data if dpath is not specified.

        ext (str): extension (default = '.cPkl')

        meta (str): cfgstr metadata that is also saved with the cfgstr.
            This data is not used in the hash, but if useful to send in if the
            cfgstr itself contains hashes.

        verbose (int): level of verbosity (default=1)

        enabled (bool): if set to False, then the load and save methods will
            do nothing.  (default = True)

    CommandLine:
        python -m ubelt.util_cache Cacher

    Example:
        >>> import ubelt as ub
        >>> cfgstr = 'repr-of-params-that-uniquely-determine-the-process'
        >>> # Create a cacher and try loading the data
        >>> cacher = ub.Cacher('test_process', cfgstr)
        >>> cacher.clear()
        >>> data = cacher.tryload()
        >>> if data is None:
        >>>     # Put expensive functions in if block when cacher misses
        >>>     myvar1 = 'result of expensive process'
        >>>     myvar2 = 'another result'
        >>>     # Tell the cacher to write at the end of the if block
        >>>     # It is idomatic to put results in a tuple named data
        >>>     data = myvar1, myvar2
        >>>     cacher.save(data)
        >>> # Last part of the Cacher pattern is to unpack the data tuple
        >>> myvar1, myvar2 = data

    Example:
        >>> # The previous example can be shorted if only a single value
        >>> from ubelt.util_cache import Cacher
        >>> cfgstr = 'repr-of-params-that-uniquely-determine-the-process'
        >>> # Create a cacher and try loading the data
        >>> cacher = Cacher('test_process', cfgstr)
        >>> myvar = cacher.tryload()
        >>> if myvar is None:
        >>>     myvar = ('result of expensive process', 'another result')
        >>>     cacher.save(myvar)
        >>> assert cacher.exists(), 'should now exist'
    """
    def __init__(self, fname, cfgstr=None, dpath=None, appname='ubelt',
                 ext='.cPkl', meta=None, verbose=None, enabled=True):
        import ubelt as ub
        if verbose is None:
            verbose = 1
        if dpath is None:  # pragma: no branch
            dpath = ub.ensure_app_cache_dir(appname)
        ub.ensuredir(dpath)
        self.dpath = dpath
        self.fname = fname
        self.cfgstr = cfgstr
        self.verbose = verbose
        self.ext = ext
        self.meta = meta
        self.enabled = enabled

        if len(self.ext) > 0 and self.ext[0] != '.':
            raise ValueError('Please be explicit and use a dot in ext')

    def _rectify_cfgstr(self, cfgstr=None):
        cfgstr = self.cfgstr if cfgstr is None else cfgstr
        if cfgstr is None:
            import warnings
            warnings.warn('No cfgstr given in Cacher constructor or call')
            cfgstr = ''
        assert self.fname is not None, 'no fname specified in Cacher'
        assert self.dpath is not None, 'no dpath specified in Cacher'
        return cfgstr

    def _condense_cfgstr(self, cfgstr=None):
        cfgstr = self._rectify_cfgstr(cfgstr)
        max_len = 32
        hashlen = 32
        if len(cfgstr) > max_len:
            hasher = hashlib.sha256()
            hasher.update(cfgstr.encode('utf8'))
            hashed_cfgstr = hasher.hexdigest()[:hashlen]
            condensed = hashed_cfgstr
        else:
            condensed = cfgstr
        return condensed

    def get_fpath(self, cfgstr=None):
        """
        Reports the filepath that the cacher will use.
        It will attempt to use '{fname}_{cfgstr}{ext}' unless that is too long.
        Then cfgstr will be hashed.

        Example:
            >>> from ubelt.util_cache import Cacher
            >>> cacher = Cacher('test_cacher1')
            >>> cacher.get_fpath()
            >>> self = Cacher('test_cacher2', cfgstr='cfg1')
            >>> self.get_fpath()
            >>> self = Cacher('test_cacher3', cfgstr='cfg1' * 32)
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
        """
        return exists(self.get_fpath())

    def existing_versions(self):
        """
        Returns data with different cfgstr values that were previously computed
        with this cacher.

        Example:
            >>> from ubelt.util_cache import Cacher
            >>> # Ensure that some data exists
            >>> known_fnames = set()
            >>> cacher = Cacher('versioned_data', cfgstr='1')
            >>> cacher.ensure(lambda: 'data1')
            >>> known_fnames.add(cacher.get_fpath())
            >>> cacher = Cacher('versioned_data', cfgstr='2')
            >>> cacher.ensure(lambda: 'data2')
            >>> known_fnames.add(cacher.get_fpath())
            >>> # List previously computed configs for this type
            >>> from os.path import basename
            >>> cacher = Cacher('versioned_data', cfgstr='2')
            >>> exist_fpaths = set(cacher.existing_versions())
            >>> exist_fnames = list(map(basename, exist_fpaths))
            >>> print(exist_fnames)
            >>> assert exist_fpaths == known_fnames

            ['versioned_data_1.cPkl', 'versioned_data_2.cPkl']
        """
        import glob
        pattern = join(self.dpath, self.fname + '_*' + self.ext)
        for fname in glob.iglob(pattern):
            fpath = join(self.dpath, fname)
            yield fpath

    def clear(self, cfgstr=None):
        """
        Removes the cache from disk
        """
        fpath = self.get_fpath(cfgstr)
        if self.verbose > 0:
            print('[cacher] clear cache')
        if exists(fpath):
            print('[cacher] removing %s' % (fpath,))
            os.remove(fpath)
        else:
            print('[cacher] ... nothing to clear')

    def tryload(self, cfgstr=None):
        """
        Like load, but returns None if the load fails
        """
        cfgstr = self._rectify_cfgstr(cfgstr)
        if self.enabled:
            try:
                if self.verbose > 1:
                    print('[cacher] tryload fname={}'.format(self.fname))
                return self.load(cfgstr)
            except IOError:
                if self.verbose > 0:
                    print('[cacher] ... {} cache miss'.format(self.fname))
        else:
            if self.verbose > 1:
                print('[cacher] ... cache disabled: fname={}'.format(self.fname))
        return None

    def load(self, cfgstr=None):
        """
        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher = Cacher('test_disabled_load', '', enabled=True)
            >>> cacher.save('data')
            >>> assert cacher.load() == 'data'
            >>> cacher.enabled = False
            >>> assert cacher.tryload() is None
        """
        cfgstr = self._rectify_cfgstr(cfgstr)

        dpath = self.dpath
        fname = self.fname
        verbose = self.verbose

        if not self.enabled:
            if verbose > 1:
                print('[cacher] ... cache disabled: fname={}'.format(self.fname))
            raise IOError(3, 'Cache Loading Is Disabled')

        fpath = self.get_fpath(cfgstr=cfgstr)

        if not exists(fpath):
            if verbose > 2:
                print('[cacher] ... cache does not exist: '
                      'dpath={} fname={} cfgstr={}'.format(
                          basename(dpath), fname, cfgstr))
            raise IOError(2, 'No such file or directory: %r' % (fpath,))
        else:
            if verbose > 3:
                print('[cacher] ... cache exists: '
                      'dpath={} fname={} cfgstr={}'.format(
                          basename(dpath), fname, cfgstr))
        try:
            with open(fpath, 'rb') as file_:
                data = pickle.load(file_)
        except (EOFError, IOError, ImportError) as ex:  # nocover
            if verbose > 0:
                print('CORRUPTED? fpath = %s' % (fpath,))
            if verbose > 1:
                print('[cacher] ... CORRUPTED? dpath={} cfgstr={}'.format(
                    basename(dpath), cfgstr))
            raise IOError(str(ex))
        except Exception:  # nocover
            if verbose > 0:
                print('CORRUPTED? fpath = {}'.format(fpath))
            raise
        else:
            if self.verbose > 2:
                print('[cacher] ... {} cache hit'.format(self.fname))
            elif verbose > 1:
                print('[cacher] ... cache hit')
        return data

    def save(self, data, cfgstr=None):
        """
        Writes data to path specified by `self.fpath(cfgstr)`.

        Metadata containing information about the cache will also be appended
        to an adjacent file with the `.meta` suffix.

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Normal functioning
            >>> cfgstr = 'long-cfg' * 32
            >>> cacher = Cacher('test_enabled_save', cfgstr)
            >>> cacher.save('data')
            >>> assert exists(cacher.get_fpath()), 'should be enabeled'
            >>> assert exists(cacher.get_fpath() + '.meta'), 'missing metadata'
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher2 = Cacher('test_disabled_save', 'params', enabled=False)
            >>> cacher2.save('data')
            >>> assert not exists(cacher2.get_fpath()), 'should be disabled'
        """
        import ubelt as ub
        if not self.enabled:
            return
        if self.verbose > 0:
            print('[cacher] ... {} cache save'.format(self.fname))

        cfgstr = self._rectify_cfgstr(cfgstr)
        condensed = self._condense_cfgstr(cfgstr)

        # Make sure the cache directory exists
        ub.ensuredir(self.dpath)

        data_fpath = self.get_fpath(cfgstr=cfgstr)
        meta_fpath = data_fpath + '.meta'

        # Also save metadata file to reconstruct hashing
        with open(meta_fpath, 'a') as file_:
            # TODO: maybe append this in json format?
            file_.write('\n\nsaving {}\n'.format(ub.timestamp()))
            file_.write(self.fname + '\n')
            file_.write(condensed + '\n')
            file_.write(cfgstr + '\n')
            file_.write(str(self.meta) + '\n')

        with open(data_fpath, 'wb') as file_:
            # Use protocol 2 to support python2 and 3
            pickle.dump(data, file_, protocol=2)

    def ensure(self, func, *args, **kwargs):
        r"""
        Wraps around a function. A cfgstr must be stored in base cacher

        Args:
            func (callable): function that will compute data on cache miss
            *args: passed to func
            **kwargs: passed to func

        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> def func():
            >>>     return 'expensive result'
            >>> fname = 'test_cacher_ensure'
            >>> cfgstr = 'func params'
            >>> cacher = Cacher(fname, cfgstr)
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


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_cache
        python -m ubelt.util_cache all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
