# -*- coding: utf-8 -*-
"""
Helpers for downloading data
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from os.path import basename, join, exists
import six
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
# import sys
# if six.PY2:  # nocover
#     # from urlparse import urlparse  # NOQA
#     from urllib2 import urlopen  # NOQA
#     # from urllib2 import URLError  # NOQA
# else:
#     from urllib.request import urlopen  # NOQA
#     # from urllib.parse import urlparse  # NOQA
#     # from urllib.error import URLError  # NOQA


# try:  # nocover
#     raise ImportError()
#     from tqdm import tqdm as Progress
# except ImportError:  # nocover
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

        fpath (PathLike):
            The path to download to. Defaults to basename of url and ubelt's
            application cache.

        hash_prefix (None or str):
            If specified, download will retry / error if the file hash
            does not match this value. Defaults to None.

        hasher (str or Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        chunksize (int):
            Download chunksize. Defaults to 2 ** 13.

        verbose (int):
            Verbosity level 0 or 1. Defaults to 1.

    Returns:
        PathLike: fpath - file path string

    Raises:
        URLError - if there is problem downloading the url
        RuntimeError - if the hash does not match the hash_prefix

    Notes:
        Original code taken from pytorch in torch/utils/model_zoo.py and
        slightly modified.

    References:
        http://blog.moleculea.com/2012/10/04/urlretrieve-progres-indicator/
        http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
        http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py

    CommandLine:
        python -m xdoctest ubelt.util_download download:1

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
        >>> fpath = download(url, hasher='sha1', hash_prefix='f79ea24571da6ddd2ba12e3d57b515249ecb8a35')
        Downloading url='http://i.imgur.com/rqwaDag.png' to fpath=...rqwaDag.png
        ...
        ...1233/1233... rate=... Hz, eta=..., total=..., wall=...

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
    if six.PY2:  # nocover
        from urllib2 import urlopen  # NOQA
    else:
        from urllib.request import urlopen  # NOQA
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

    if hash_prefix:
        if isinstance(hasher, six.string_types):
            if hasher == 'sha1':
                hasher = hashlib.sha1()
            elif hasher == 'sha512':
                hasher = hashlib.sha512()
            else:
                raise KeyError(hasher)

    tmp = tempfile.NamedTemporaryFile(delete=False)

    # possible optimization (have not tested or timed)
    _tmp_write = tmp.write
    _urldata_read = urldata.read
    # _hasher_update = (lambda buffer: buffer.encode('utf8') if six.PY2 else)  # NOQA
    #                   hasher.update)
    try:
        with Progress(total=file_size, disable=not verbose) as pbar:
            _pbar_update = pbar.update

            def _critical_loop():
                # Initialize the buffer to a non-empty object
                buffer = ' '
                if hash_prefix:
                    _hasher_update = hasher.update
                    while buffer:
                        buffer = _urldata_read(chunksize)
                        _tmp_write(buffer)
                        _hasher_update(buffer)
                        _pbar_update(len(buffer))
                else:
                    # Same code as above, just without the hasher update.
                    # (tight loop optimization: remove in-loop conditional)
                    while buffer:
                        buffer = _urldata_read(chunksize)
                        _tmp_write(buffer)
                        _pbar_update(len(buffer))
            _critical_loop()

        tmp.close()

        # We keep a potentially corrupted file if the hash doesn't match.
        # It could be the case that the user simply specified the wrong
        # hash_prefix.
        shutil.move(tmp.name, fpath)

        if hash_prefix:
            got = hasher.hexdigest()
            if got[:len(hash_prefix)] != hash_prefix:
                print('hash_prefix = {!r}'.format(hash_prefix))
                print('got = {!r}'.format(got))
                raise RuntimeError(
                    'invalid hash value (expected "{}", got "{}")'.format(
                        hash_prefix, got))
    finally:
        tmp.close()
        # If for some reason the move failed, delete the temporary file
        if exists(tmp.name):  # nocover
            os.remove(tmp.name)
    return fpath


def grabdata(url, fpath=None, dpath=None, fname=None, redo=False,
             verbose=1, appname=None, hash_prefix=None, hasher='sha512',
             **download_kw):
    """
    Downloads a file, caches it, and returns its local path.

    Args:
        url (str): url to the file to download

        fpath (PathLike): The full path to download the file to. If
            unspecified, the arguments `dpath` and `fname` are used to
            determine this.

        dpath (PathLike): where to download the file. If unspecified `appname`
            is used to determine this. Mutually exclusive with fpath.

        fname (str): What to name the downloaded file. Defaults to the url
            basename. Mutually exclusive with fpath.

        redo (bool): if True forces redownload of the file (default = False)

        verbose (bool):  verbosity flag (default = True)

        appname (str): set dpath to `ub.get_app_cache_dir(appname)`.
            Mutually exclusive with dpath and fpath.

        hash_prefix (None or str):
            If specified, grabdata verifies that this matches the hash of the
            file, and then saves the hash in a adjacent file to certify that
            the download was successful. Defaults to None.

        hasher (str or Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        **download_kw: additional kwargs to pass to ub.download

    Returns:
        PathLike: fpath - file path string

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> import ubelt as ub
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = ub.grabdata(url, fname='mario.png')
        >>> result = basename(fpath)
        >>> print(result)
        mario.png

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> import ubelt as ub
        >>> fname = 'foo.bar'
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> prefix1 = '944389a39dfb8fa9'
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> stamp_fpath = fpath + '.hash'
        >>> assert open(stamp_fpath, 'r').read() == prefix1
        >>> # Check that the download doesn't happen again
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> # todo: check file timestamps have not changed
        >>> #
        >>> # Check redo works with hash
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, redo=True)
        >>> # todo: check file timestamps have changed
        >>> #
        >>> # Check that a redownload occurs when the stamp is changed
        >>> open(stamp_fpath, 'w').write('corrupt-stamp')
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> assert open(stamp_fpath, 'r').read() == prefix1
        >>> #
        >>> # Check that a redownload occurs when the stamp is removed
        >>> ub.delete(stamp_fpath)
        >>> open(fpath, 'w').write('corrupt-data')
        >>> assert not ub.hash_file(fpath, base='hex').startswith(prefix1)
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> assert ub.hash_file(fpath, base='hex').startswith(prefix1)
        >>> #
        >>> # Check that requesting new data causes redownload
        >>> url2 = 'https://data.kitware.com/api/v1/item/5b4039308d777f2e6225994c/download'
        >>> prefix2 = 'c98a46cb31205cf'
        >>> fpath = ub.grabdata(url2, fname=fname, hash_prefix=prefix2)
        >>> assert open(stamp_fpath, 'r').read() == prefix2
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

    # note that needs_download is never set to false after it becomes true
    # this is the key to working through the logic of the following checks
    needs_download = redo

    if not exists(fpath):
        # always download if we are missing the file
        needs_download = True

    if hash_prefix:
        stamp_fpath = fpath + '.hash'
        # Force a re-download if the hash file does not exist or it does
        # not match the expected hash
        if exists(stamp_fpath):
            with open(stamp_fpath, 'r') as file:
                hashstr = file.read()
            if not hashstr.startswith(hash_prefix):
                if verbose:
                    print('invalid hash value (expected "{}", got "{}")'.format(
                        hash_prefix, hashstr))
                needs_download = True
        elif exists(fpath):
            # If the file exists, but the hash doesnt exist, simply compute the
            # hash of the existing file instead of redownloading it.
            # Redownload if this fails.
            from ubelt import util_hash
            hashstr = util_hash.hash_file(fpath, hasher=hasher)
            if hashstr.startswith(hash_prefix):
                # Write the missing stamp file if it matches
                with open(stamp_fpath, 'w') as file:
                    file.write(hash_prefix)
            else:
                if verbose:
                    print('invalid hash value (expected "{}", got "{}")'.format(
                        hash_prefix, hashstr))
                needs_download = True
        else:
            needs_download = True

    if needs_download:
        fpath = download(url, fpath, verbose=verbose,
                         hash_prefix=hash_prefix, hasher=hasher,
                         **download_kw)

        if hash_prefix:
            # If the file successfully downloaded then the hashes match.
            # write out the expected prefix so we can check it later
            with open(stamp_fpath, 'w') as file:
                file.write(hash_prefix)
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
