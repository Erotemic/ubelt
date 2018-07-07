# -*- coding: utf-8 -*-
"""
Helpers for downloading data
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from os.path import basename, join, exists
import os
import shutil
import tempfile
import hashlib
from ubelt import util_platform


# try:  # nocover
# from requests import get as urlopen
# _have_requests = True
# except ImportError:  # nocover
# _have_requests = False
import sys
if sys.version_info[0] == 2:  # nocover
    from urlparse import urlparse  # NOQA
    from urllib2 import urlopen  # NOQA
    from urllib2 import URLError  # NOQA
else:
    from urllib.request import urlopen  # NOQA
    from urllib.parse import urlparse  # NOQA
    from urllib.error import URLError  # NOQA


try:  # nocover
    raise ImportError()
    from tqdm import tqdm as Progress
except ImportError:  # nocover
    # fake tqdm if it's not installed
    from ubelt import progiter
    Progress = progiter.ProgIter


__all__ = ['download', 'grabdata']


def download(url, fpath=None, hash_prefix=None, hasher='sha512',
             chunksize=8192, verbose=1):
    """
    downloads a url to a fpath.

    Args:
        url (str):
            The url to download.

        fpath (str):
            The path to download to. Defaults to basename of url and ubelt's
            application cache.

        hash_prefix (None or str):
            If specified, download will retry / error if the file hash
            does not match this value. Defaults to None.

        hasher (key or Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        chunksize (int):
            Download chunksize. Defaults to 2 ** 13.

        verbose (int):
            Verbosity level 0 or 1. Defaults to 1.

    Notes:
        Original code taken from pytorch in torch/utils/model_zoo.py and
        slightly modified.

    References:
        http://blog.moleculea.com/2012/10/04/urlretrieve-progres-indicator/
        http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
        http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> from ubelt.util_download import *  # NOQA
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = download(url)
        >>> print(basename(fpath))
        rqwaDag.png

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = download(url, hash_prefix='f79ea24571da6ddd2ba12e3d57b515249ecb8a35')
        Downloading url='http://i.imgur.com/rqwaDag.png' to fpath='/home/joncrall/.cache/ubelt/rqwaDag.png'
         1233/1233... rate=... Hz, eta=..., total=..., wall=...

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> # test download from girder
        >>> import pytest
        >>> import ubelt as ub
        >>> url = 'https://data.kitware.com/api/v1/item/5b4039308d777f2e6225994c/download'
        >>> ub.download(url, hasher='sha512', hash_prefix='c98a46cb31205cf')
        >>> with pytest.raises(RuntimeError):
        >>>     ub.download(url, hasher='sha512', hash_prefix='BAD_HASH')
    """
    if fpath is None:
        dpath = util_platform.ensure_app_cache_dir('ubelt')
        fname = basename(url)
        fpath = join(dpath, fname)

    if verbose:
        print('Downloading url=%r to fpath=%r' % (url, fpath))

    urldata = urlopen(url)
    meta = urldata.info()
    if hasattr(meta, 'getheaders'):  # nocover
        file_size = int(meta.getheaders("Content-Length")[0])
    else:
        file_size = int(meta.get_all("Content-Length")[0])

    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        if hash_prefix:
            if isinstance(hasher, str):
                if hasher == 'sha1':
                    hasher = hashlib.sha1()
                elif hasher == 'sha512':
                    hasher = hashlib.sha512()
                else:
                    raise KeyError(hasher)
        with Progress(total=file_size, disable=not verbose) as pbar:
            if hash_prefix:
                while True:
                    buffer = urldata.read(chunksize)
                    if len(buffer) == 0:
                        break
                    tmp.write(buffer)
                    hasher.update(buffer)
                    pbar.update(len(buffer))
            else:
                # Same code as above, just without the hasher update.
                # (tight loop optimization: remove in-loop conditional)
                while True:
                    buffer = urldata.read(chunksize)
                    if len(buffer) == 0:
                        break
                    tmp.write(buffer)
                    pbar.update(len(buffer))

        tmp.close()
        if hash_prefix:
            digest = hasher.hexdigest()
            if digest[:len(hash_prefix)] != hash_prefix:
                raise RuntimeError(
                    'invalid hash value (expected "{}", got "{}")'.format(
                        hash_prefix, digest))
        shutil.move(tmp.name, fpath)
    finally:
        tmp.close()
        # If for some reason the move failed, delete the temporary file
        if exists(tmp.name):  # nocover
            os.remove(tmp.name)
    return fpath


def grabdata(url, fpath=None, dpath=None, fname=None, redo=False,
             verbose=1, appname=None, **download_kw):
    """
    Downloads a file, caches it, and returns its local path.

    Args:
        url (str): url to the file to download
        fpath (str): The full path to download the file to. If unspecified, the
            arguments `dpath` and `fname` are used to determine this.
        dpath (str): where to download the file. If unspecified `appname`
            is used to determine this. Mutually exclusive with fpath.
        fname (str): What to name the downloaded file. Defaults to the url
            basename. Mutually exclusive with fpath.
        redo (bool): if True forces redownload of the file (default = False)
        verbose (bool):  verbosity flag (default = True)
        appname (str): set dpath to `ub.get_app_cache_dir(appname)`.
            Mutually exclusive with dpath and fpath.
        **download_kw: additional kwargs to pass to ub.download

    Returns:
        str: fpath - file path string

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> import ubelt as ub
        >>> file_url = 'http://i.imgur.com/rqwaDag.png'
        >>> lena_fpath = ub.grabdata(file_url, fname='mario.png')
        >>> result = basename(lena_fpath)
        >>> print(result)
        mario.png
    """
    if appname and dpath:
        raise ValueError('Cannot specify appname with dpath')
    if fpath and (dpath or fname or appname):
        raise ValueError('Cannot specify fpath with dpath or fname')

    if fpath is None:
        if dpath is None:
            appname = appname or 'ubelt'
            dpath = util_platform.ensure_app_cache_dir(appname)
        if fname is None:
            fname = basename(url)
        fpath = join(dpath, fname)

    if redo or not exists(fpath):
        fpath = download(url, fpath, verbose=verbose, **download_kw)
    else:
        if verbose >= 2:
            print('Already have file %s' % fpath)
    return fpath


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_download all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
