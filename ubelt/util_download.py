# -*- coding: utf-8 -*-
"""
Helpers for downloading data
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from os.path import basename, join, exists
import sys
import os
import shutil
import tempfile
from ubelt import util_platform


try:  # nocover
    from requests.utils import urlparse
    import requests.get as urlopen
    _have_requests = True
except ImportError:  # nocover
    _have_requests = False
    if sys.version_info[0] == 2:
        from urlparse import urlparse  # NOQA
        from urllib2 import urlopen  # NOQA
    else:
        from urllib.request import urlopen  # NOQA
        from urllib.parse import urlparse  # NOQA

try:  # nocover
    from tqdm import tqdm as _tqdm
except ImportError:  # nocover
    # fake tqdm if it's not installed
    from ubelt import progiter
    class _FakeTQDM(progiter.ProgIter):
        def __init__(self, total, disable=False):
            super(_FakeTQDM, self).__init__(enabled=not disable, length=total)

        def update(self, n):
            if self.enabled:
                self.step(n)
    _tqdm = _FakeTQDM


def download(url, fpath=None, hash_prefix=None, chunksize=8192, verbose=1):
    """
    downloads a url to a fpath.

    Args:
        url (str): url to download
        fpath (str): path to download to. Defaults to basename of url
        chunksize (int): download chunksize
        verbose (bool): verbosity

    Notes:
        Original code taken from pytorch in torch/utils/model_zoo.py and
        slightly modified.

    References:
        http://blog.moleculea.com/2012/10/04/urlretrieve-progres-indicator/
        http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
        http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py

    Example:
        >>> from ubelt.util_download import *  # NOQA
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = download(url)
        >>> print(basename(fpath))
        rqwaDag.png
    """
    if fpath is None:
        dpath = util_platform.ensure_app_cache_dir('ubelt')
        fname = basename(url)
        fpath = join(dpath, fname)

    urldata = urlopen(url)
    if _have_requests:
        file_size = int(urldata.headers["Content-Length"])
        urldata = urldata.raw
    else:
        meta = urldata.info()
        if hasattr(meta, 'getheaders'):
            file_size = int(meta.getheaders("Content-Length")[0])
        else:
            file_size = int(meta.get_all("Content-Length")[0])

    if verbose:
        print('Downloading url=%r to fpath=%r' % (url, fpath))

    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        # if hash_prefix:
        #     sha256 = hashlib.sha256()
        with _tqdm(total=file_size, disable=not verbose) as pbar:
            while True:
                buffer = urldata.read(8192)
                if len(buffer) == 0:
                    break
                tmp.write(buffer)
                # if hash_prefix:
                #     sha256.update(buffer)
                pbar.update(len(buffer))

        tmp.close()
        # if hash_prefix:
        #     digest = sha256.hexdigest()
        #     if digest[:len(hash_prefix)] != hash_prefix:
        #         raise RuntimeError('invalid hash value (expected "{}", got "{}")'
        #                            .format(hash_prefix, digest))
        shutil.move(tmp.name, fpath)
    finally:
        tmp.close()
        if exists(tmp.name):
            os.remove(tmp.name)
    return fpath


def grabdata(url, fpath=None, dpath=None, fname=None, redo=False,
             verbose=1, **download_kw):
    """
    Downloads a file, caches it, and returns its local path.

    Args:
        url (str): url to the file to download
        fpath (str): The full path to download the file to. If unspecified, the
            arguments `dpath` and `fname` are used to determine this.
        dpath (str): where to download the file. Defaults to ubelt's
            application cache.
        fname (str): What to name the downloaded file. Defaults to the url
            basename.
        redo (bool): if True forces redownload of the file (default = False)
        verbose (bool):  verbosity flag (default = True)
        **download_kw: additional kwargs to pass to ub.download

    Returns:
        str: fpath - file path string

    Example:
        >>> import ubelt as ub
        >>> file_url = 'http://i.imgur.com/rqwaDag.png'
        >>> lena_fpath = ub.grabdata(file_url, fname='mario.png')
        >>> result = basename(lena_fpath)
        >>> print(result)
        mario.png
    """
    if fpath is None:
        if dpath is None:
            dpath = util_platform.ensure_app_cache_dir('ubelt')
        if fname is None:
            fname = basename(url)
        fpath = join(dpath, fname)
    elif dpath is not None or fname is not None:
        raise ValueError('Cannot specify dpath or fname with fpath')

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
