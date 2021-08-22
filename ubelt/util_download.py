# -*- coding: utf-8 -*-
"""
Helpers for downloading data

The :func:`download` function access the network and requests the content at a
specific url using :mod:`urllib` or :mod:`urllib2`. You can either specify
where the data goes or download it to the default location in ubelt cache.
Either way this function returns the location of the downloaded data. You can
also specify the expected hash in order to check the validity of the data. By
default downloading is verbose.

The :func:`grabdata` function is almost identitcal to :func:`download`, but it
checks if the data already exists in the download location, and only downloads
if it needs to.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from os.path import basename, join, exists, dirname
import os
import sys


__all__ = ['download', 'grabdata']


PY2 = sys.version_info[0] == 2


if PY2:
    import six
    string_types = six.string_types
else:
    string_types = (str,)


def download(url, fpath=None, dpath=None, fname=None, hash_prefix=None,
             hasher='sha512', chunksize=8192, verbose=1):
    """
    Downloads a url to a file on disk.

    If unspecified the location and name of the file is chosen automatically.
    A hash_prefix can be specified to verify the integrity of the downloaded
    data. This function will download the data every time its called. For
    cached downloading see `grabdata`.

    Args:
        url (str):
            The url to download.

        fpath (PathLike | io.BytesIO):
            The path to download to. Defaults to basename of url and ubelt's
            application cache. If this is a io.BytesIO object then information
            is directly written to this object (note this prevents the use of
            temporary files).

        dpath (PathLike): where to download the file. If unspecified `appname`
            is used to determine this. Mutually exclusive with fpath.

        fname (str): What to name the downloaded file. Defaults to the url
            basename. Mutually exclusive with fpath.

        hash_prefix (None | str):
            If specified, download will retry / error if the file hash
            does not match this value. Defaults to None.

        hasher (str | Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        chunksize (int, default=2 ** 13):
            Download chunksize.

        verbose (int, default=1):
            Verbosity level 0 or 1.

    Returns:
        PathLike: fpath - path to the downloaded file.

    Raises:
        URLError - if there is problem downloading the url
        RuntimeError - if the hash does not match the hash_prefix

    Notes:
        Based largely on code in pytorch [4]_ with modifications influenced by
        other resources [1]_ [2]_ [3]_.

    References:
        .. [1] http://blog.moleculea.com/2012/10/04/urlretrieve-progres-indicator/
        .. [2] http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
        .. [3] http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        .. [4] https://github.com/pytorch/pytorch/blob/2787f1d8edbd4aadd4a8680d204341a1d7112e2d/torch/hub.py#L347

    TODO:
        - [ ] fine-grained control of progress

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> from ubelt.util_download import *  # NOQA
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = download(url)
        >>> print(basename(fpath))
        rqwaDag.png

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> import ubelt as ub
        >>> import io
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> file = io.BytesIO()
        >>> fpath = ub.download(url, file)
        >>> file.seek(0)
        >>> data = file.read()
        >>> assert ub.hash_data(data, hasher='sha1').startswith('f79ea24571')

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = download(url, hasher='sha1', hash_prefix='f79ea24571da6ddd2ba12e3d57b515249ecb8a35')
        Downloading url='http://i.imgur.com/rqwaDag.png' to fpath=...rqwaDag.png
        ...
        ...1233/1233... rate=... Hz, eta=..., total=...

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
    from ubelt import ProgIter as Progress
    from ubelt import ensure_app_cache_dir
    import shutil
    import tempfile
    import hashlib

    if PY2:  # nocover
        from urllib2 import urlopen  # NOQA
    else:
        from urllib.request import urlopen  # NOQA

    if fpath and (dpath or fname):
        raise ValueError('Cannot specify fpath with dpath or fname')
    if fpath is None:
        if dpath is None:
            dpath = ensure_app_cache_dir('ubelt')
        if fname is None:
            fname = basename(url)
        fpath = join(dpath, fname)

    # Check if fpath was given as an BytesIO object
    _dst_is_io_object = hasattr(fpath, 'write')

    if not _dst_is_io_object and not exists(dirname(fpath)):
        raise Exception('parent of {} does not exist'.format(fpath))

    if verbose:
        if _dst_is_io_object:
            print('Downloading url={!r} to IO object'.format(url))
        else:
            print('Downloading url={!r} to fpath={!r}'.format(
                url, fpath))

    urldata = urlopen(url)
    meta = urldata.info()
    try:
        if hasattr(meta, 'getheaders'):  # nocover
            file_size = int(meta.getheaders("Content-Length")[0])
        else:
            file_size = int(meta.get_all("Content-Length")[0])
    except Exception:  # nocover
        # sometimes the url does not contain content length metadata
        # TODO: find a public URL that exemplifies this or figure out how to
        # mock it locally.
        file_size = None

    if hash_prefix:
        if isinstance(hasher, string_types):
            if hasher == 'sha1':
                hasher = hashlib.sha1()
            elif hasher == 'md5':
                hasher = hashlib.md5()
            elif hasher == 'sha256':
                hasher = hashlib.sha256()
            elif hasher == 'sha512':
                hasher = hashlib.sha512()
            else:
                raise KeyError(hasher)

    if _dst_is_io_object:
        _file_write = fpath.write
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        _file_write = tmp.write

    # possible optimization (have not tested or timed)
    _urldata_read = urldata.read
    try:
        pbar = Progress(total=file_size, disable=not verbose,
                        freq=chunksize)
        with pbar:
            _pbar_update = pbar.update

            def _critical_loop():
                # Initialize the buffer to a non-empty object
                buffer = ' '
                if hash_prefix:
                    _hasher_update = hasher.update
                    while buffer:
                        buffer = _urldata_read(chunksize)
                        _file_write(buffer)
                        _hasher_update(buffer)
                        _pbar_update(len(buffer))
                else:
                    # Same code as above, just without the hasher update.
                    # (tight loop optimization: remove in-loop conditional)
                    while buffer:
                        buffer = _urldata_read(chunksize)
                        _file_write(buffer)
                        _pbar_update(len(buffer))
            _critical_loop()

        if not _dst_is_io_object:
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
                if _dst_is_io_object:
                    raise RuntimeError(
                        'invalid hash value '
                        '(expected "{}", got "{}")'.format(hash_prefix, got))
                else:
                    raise RuntimeError(
                        'invalid hash value for fpath={!r} '
                        '(expected "{}", got "{}")'.format(
                            fpath, hash_prefix, got))
    finally:
        if not _dst_is_io_object:  # nocover
            tmp.close()
            # If for some reason the move failed, delete the temporary file
            if exists(tmp.name):
                os.remove(tmp.name)
    return fpath


def grabdata(url, fpath=None, dpath=None, fname=None, redo=False,
             verbose=1, appname=None, hash_prefix=None, hasher='sha512',
             **download_kw):
    """
    Downloads a file, caches it, and returns its local path.

    If unspecified the location and name of the file is chosen automatically.
    A hash_prefix can be specified to verify the integrity of the downloaded
    data.

    Args:
        url (str): url to the file to download

        fpath (PathLike): The full path to download the file to. If
            unspecified, the arguments `dpath` and `fname` are used to
            determine this.

        dpath (PathLike): where to download the file. If unspecified `appname`
            is used to determine this. Mutually exclusive with fpath.

        fname (str): What to name the downloaded file. Defaults to the url
            basename. Mutually exclusive with fpath.

        redo (bool, default=False): if True forces redownload of the file

        verbose (bool, default=True):  verbosity flag

        appname (str): set dpath to `ub.get_app_cache_dir(appname)`.
            Mutually exclusive with dpath and fpath.

        hash_prefix (None | str):
            If specified, grabdata verifies that this matches the hash of the
            file, and then saves the hash in a adjacent file to certify that
            the download was successful. Defaults to None.

        hasher (str | Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        **download_kw: additional kwargs to pass to ub.download

    Returns:
        PathLike: fpath - path to downloaded or cached file.

    CommandLine:
        xdoctest -m ubelt.util_download grabdata --network

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
        >>> stamp_fpath = fpath + '.sha512.hash'
        >>> assert ub.readfrom(stamp_fpath) == prefix1
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
        >>> assert ub.readfrom(stamp_fpath) == prefix1
        >>> #
        >>> # Check that a redownload occurs when the stamp is removed
        >>> ub.delete(stamp_fpath)
        >>> open(fpath, 'w').write('corrupt-data')
        >>> assert not ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> assert ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)
        >>> #
        >>> # Check that requesting new data causes redownload
        >>> url2 = 'https://data.kitware.com/api/v1/item/5b4039308d777f2e6225994c/download'
        >>> prefix2 = 'c98a46cb31205cf'
        >>> fpath = ub.grabdata(url2, fname=fname, hash_prefix=prefix2)
        >>> assert ub.readfrom(stamp_fpath) == prefix2
    """
    from ubelt.util_platform import ensure_app_cache_dir
    if appname and dpath:
        raise ValueError('Cannot specify appname with dpath')
    if fpath and (dpath or fname or appname):
        raise ValueError('Cannot specify fpath with dpath or fname')

    if fpath is None:
        if dpath is None:
            appname = appname or 'ubelt'
            dpath = ensure_app_cache_dir(appname)
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
        stamp_fpath, needs_download = _check_hash_stamp(
            fpath, hash_prefix, hasher, verbose, needs_download)

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


def _check_hash_stamp(fpath, hash_prefix, hasher, verbose, needs_download=False):
    if isinstance(hasher, string_types):
        hasher_name = hasher
    else:
        hasher_name = hasher.name

    stamp_fpath = '{}.{}.hash'.format(fpath, hasher_name)
    # Force a re-download if the hash file does not exist or it does
    # not match the expected hash
    if exists(stamp_fpath):
        with open(stamp_fpath, 'r') as file:
            hashstr = file.read()
        if not hashstr.startswith(hash_prefix):
            if verbose:  # pragma: nobranch
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
            if verbose:  # pragma: nobranch
                print('invalid hash value (expected "{}", got "{}")'.format(
                    hash_prefix, hashstr))
            needs_download = True
    else:
        needs_download = True

    return stamp_fpath, needs_download
