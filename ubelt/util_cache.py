# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
from os.path import join, normpath, basename, exists
from six.moves import cPickle as pickle


class Cacher(object):
    """
    Cacher that can be quickly integrated into existing scripts.

    Args:
        fname (str):  file name
        cfgstr (str): indicates the state
        cache_dir (None): where to save the cache (default to app resource dir)
        appname (str): application name (default = 'ubelt')
        ext (str): extension (default = '.cPkl')
        verbose (bool): verbosity flag (default = None)
        enabled (bool): (default = True)

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
    def __init__(self, fname, cfgstr=None, cache_dir=None, appname='ubelt',
                 ext='.cPkl', verbose=None, enabled=True):
        import ubelt as ub
        if verbose is None:
            verbose = 1
        if cache_dir is None:  # pragma: no branch
            cache_dir = ub.get_app_resource_dir(appname)
        ub.ensuredir(cache_dir)
        self.dpath = cache_dir
        self.fname = fname
        self.cfgstr = cfgstr
        self.verbose = verbose
        self.ext = ext
        self.enabled = enabled

    def _rectify_cfgstr(self, cfgstr=None):
        cfgstr = self.cfgstr if cfgstr is None else cfgstr
        if cfgstr is None:
            import warnings
            warnings.warn('No cfgstr given in Cacher constructor or call')
            cfgstr = ''
        assert self.fname is not None, 'no fname specified in Cacher'
        assert self.dpath is not None, 'no dpath specified in Cacher'
        return cfgstr

    def get_fpath(self, cfgstr=None):
        """
        Reports the filepath that the cacher will use

        Example:
            >>> from ubelt.util_cache import Cacher
            >>> cacher = Cacher('test_cacher1')
            >>> cacher.get_fpath()
            >>> self = Cacher('test_cacher2', cfgstr='cfg1')
            >>> self.get_fpath()
        """
        cfgstr = self._rectify_cfgstr(cfgstr)
        fpath = _args2_fpath(self.dpath, self.fname, cfgstr, self.ext)
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
        """
        import glob
        pattern = self.fname + '_*' + self.ext
        for fname in glob.glob1(self.dpath, pattern):
            fpath = join(self.dpath, fname)
            yield fpath

    def clear(self, cfgstr=None):
        """
        Removes the cache from disk
        """
        fpath = self.get_fpath(cfgstr)
        if self.verbose > 0:
            print('[cache] Clear cache')
        if exists(fpath):
            print('[cache] Removing %s' % (fpath,))
            os.remove(fpath)
        else:
            print('[cache] ... nothing to clear')

    def tryload(self, cfgstr=None):
        """
        Like load, but returns None if the load fails
        """
        cfgstr = self._rectify_cfgstr(cfgstr)
        try:
            if self.verbose > 1:
                print('[cache] tryload fname=%s' % (self.fname,))
                # if self.verbose > 2:
                #     print('[cache] cfgstr=%r' % (cfgstr,))
            return self.load(cfgstr)
        except IOError:
            if self.verbose > 0:
                print('[cache] ... %s Cacher miss' % (self.fname))

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
        # TODO: use the computed fpath from this object instead

        dpath = self.dpath
        fname = self.fname
        verbose = self.verbose

        if not self.enabled:
            if verbose > 1:
                print('[cache] ... cache disabled: dpath=%s cfgstr=%r'
                        (basename(dpath), cfgstr,))
            raise IOError(3, 'Cache Loading Is Disabled')
        fpath = _args2_fpath(dpath, fname, cfgstr, self.ext)
        if not exists(fpath):
            if verbose > 0:
                print('[cache] ... cache does not exist: dpath=%r fname=%r cfgstr=%r' % (
                    basename(dpath), fname, cfgstr,))
            raise IOError(2, 'No such file or directory: %r' % (fpath,))
        else:
            if verbose > 2:
                print('[cache] ... cache exists: dpath=%r fname=%r cfgstr=%r' % (
                    basename(dpath), fname, cfgstr,))
            # import utool as ut
            # nbytes = ut.get_file_nBytes(fpath)
            # big_verbose = (nbytes > 1E6 and verbose > 2) or verbose > 2
            # if big_verbose:
            #     print('[cache] About to read file of size %s' % (ut.byte_str2(nbytes),))
        try:
            with open(fpath, 'rb') as file_:
                data = pickle.load(file_)
            # data = util_io.load_data(fpath, verbose=verbose > 2)
        except (EOFError, IOError, ImportError) as ex:  # nocover
            print('CORRUPTED? fpath = %s' % (fpath,))
            if verbose > 1:
                print('[cache] ... cache miss dpath=%s cfgstr=%r' % (
                    basename(dpath), cfgstr,))
            raise IOError(str(ex))
        except Exception:  # nocover
            print('CORRUPTED? fpath = %s' % (fpath,))
            raise
        else:
            if verbose > 2:
                print('[cache] ... cache hit')

        if self.verbose > 1:
            print('[cache] ... ' + self.fname + ' Cacher hit')
        return data

    def save(self, data, cfgstr=None):
        """
        Example:
            >>> from ubelt.util_cache import *  # NOQA
            >>> # Setting the cacher as enabled=False turns it off
            >>> cacher = Cacher('test_disabled_save', 'params', enabled=False)
            >>> cacher.save('data')
            >>> assert not exists(cacher.get_fpath()), 'should be disabled'
        """
        if not self.enabled:
            return
        cfgstr = self._rectify_cfgstr(cfgstr)
        if self.verbose > 0:
            print('[cache] ... ' + self.fname + ' Cacher save')

        fpath = _args2_fpath(self.dpath, self.fname, cfgstr, self.ext)
        with open(fpath, 'wb') as file_:
            # Use protocol 2 to support python2 and 3
            pickle.dump(data, file_, protocol=2)
        # util_io.save_data(fpath, data, verbose=verbose)

    def ensure(self, func, *args, **kwargs):
        r"""
        Wraps around a function

        Args:
            self (?):
            func (function):  live python function
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


def consensed_cfgstr(prefix, cfgstr, max_len=128, cfgstr_hashlen=32):
    if len(prefix) + len(cfgstr) > max_len:
        import hashlib
        hasher = hashlib.sha256()
        hasher.update(cfgstr.encode('utf8'))
        hashed_cfgstr = hasher.hexdigest()[:cfgstr_hashlen]
        condensed = hashed_cfgstr
    else:
        condensed = cfgstr
    # Hack for prettier names
    # if prefix.endswith('_') or condensed.startswith('_'):  # nocover
    #     fname_cfgstr = prefix + condensed
    # else:
    fname_cfgstr = prefix + '_' + condensed
    return fname_cfgstr


def _args2_fpath(dpath, fname, cfgstr, ext):
    r"""
    Ensures that the filename is not too long

    Internal util_cache helper function
    Windows MAX_PATH=260 characters
    Absolute length is limited to 32,000 characters
    Each filename component is limited to 255 characters

    Args:
        dpath (str):
        fname (str):
        cfgstr (str):
        ext (str):

    Returns:
        str: fpath

    CommandLine:
        python -m utool.util_cache --test-_args2_fpath

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ubelt.util_cache import *  # NOQA
        >>> from ubelt.util_cache import _args2_fpath
        >>> import ubelt as ut
        >>> dpath = 'F:\\.cache\\tmp'
        >>> fname = 'vsm'
        >>> cfgstr = '_'.join([
        >>>     'PZ_MTEST_DSUUIDS((9)67fdifdsalfsjdsfl)',
        >>>     'QSUUIDS((9)67fdsafdasfdsal)',
        >>>     'zebra_plains_vsone_NN(single,K1+1,last,cks1024)',
        >>>     'FILT(ratio<0.625;1.0,fg;1.0)',
        >>>     'SV(0.01;2;1.57minIn=4,nRR=50,nsum,)', 'AGG(nsum)',
        >>>     'FLANN(4_kdtrees)', 'FEATWEIGHT(ON,uselabel,rf)',
        >>>     'FEAT(hesaff+sift_)', 'CHIP(sz450)',
        >>> ])
        >>> assert len(cfgstr) > 260
        >>> ext = '.cPkl'
        >>> fpath = _args2_fpath(dpath, fname, cfgstr, ext)
        >>> result = str(fpath.replace('\\', '/'))
        >>> print('result = %s' % (result,))
        >>> target = 'F:/.cache/tmp/vsm_96f53cd002c5415ff9e90302b872abb7.cPkl'
        >>> print('target = %s' % (target,))
        >>> assert result == target

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ubelt.util_cache import *  # NOQA
        >>> from ubelt.util_cache import _args2_fpath
        >>> import ubelt as ut
        >>> dpath = 'F:\\.cache\\tmp'
        >>> fname = 'vsm'
        >>> cfgstr = '_'.join([
        >>>     'PZ_DUUIDS((9),iksidjaidurfd)',
        >>> ])
        >>> ext = '.cPkl'
        >>> fpath = _args2_fpath(dpath, fname, cfgstr, ext)
        >>> result = str(fpath.replace('\\', '/'))
        >>> print('result = %s' % (result,))
        >>> target = 'F:/.cache/tmp/vsm_PZ_DUUIDS((9),iksidjaidurfd).cPkl'
        >>> print('target = %s' % (target,))
        >>> assert result == target
    """
    if len(ext) > 0 and ext[0] != '.':
        raise ValueError('Please be explicit and use a dot in ext')
    prefix = fname
    max_len = 128
    cfgstr_hashlen = 32
    fname_cfgstr = consensed_cfgstr(prefix, cfgstr, max_len=max_len,
                                    cfgstr_hashlen=cfgstr_hashlen)
    fpath = join(dpath, fname_cfgstr + ext)
    fpath = normpath(fpath)
    return fpath


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_cache
        python -m ubelt.util_cache all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
