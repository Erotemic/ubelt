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
from ubelt.util_const import NoParam
from os.path import basename, join, exists, dirname, split
import os


__all__ = ['download', 'grabdata']


def download(url, fpath=None, dpath=None, fname=None, appname=None,
             hash_prefix=None, hasher='sha512', chunksize=8192, verbose=1,
             timeout=NoParam, progkw=None):
    """
    Downloads a url to a file on disk.

    If unspecified the location and name of the file is chosen automatically.
    A hash_prefix can be specified to verify the integrity of the downloaded
    data. This function will download the data every time its called. For
    cached downloading see `grabdata`.

    Args:
        url (str):
            The url to download.

        fpath (Optional[str | PathLike | io.BytesIO]):
            The path to download to. Defaults to basename of url and ubelt's
            application cache. If this is a io.BytesIO object then information
            is directly written to this object (note this prevents the use of
            temporary files).

        dpath (Optional[PathLike]):
            where to download the file. If unspecified `appname` is used to
            determine this. Mutually exclusive with fpath.

        fname (Optional[str]):
            What to name the downloaded file. Defaults to the url basename.
            Mutually exclusive with fpath.

        appname (str): set dpath to
            ``ub.get_app_cache_dir(appname or 'ubelt')`` if dpath and fpath are
            not given.

        hash_prefix (None | str):
            If specified, download will retry / error if the file hash
            does not match this value. Defaults to None.

        hasher (str | Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        chunksize (int):
            Download chunksize. Default to ``2 ** 13``

        verbose (int | bool):
            Verbosity flag. Quiet is 0, higher is more verbose. Defaults to 1.

        timeout (float | NoParamType):
            Specify timeout in seconds for :func:`urllib.request.urlopen`.  (if
            not specified, the global default timeout setting will be used)
            This only works for HTTP, HTTPS and FTP connections for blocking
            operations like the connection attempt.

        progkw (Dict | NoParamType):
            if specified provides extra arguments to the progress iterator.
            See :class:`ubelt.progiter.ProgIter` for available options.

    Returns:
        str | PathLike: fpath - path to the downloaded file.

    Raises:
        URLError - if there is problem downloading the url
        RuntimeError - if the hash does not match the hash_prefix

    Note:
        Based largely on code in pytorch [TorchDL]_ with modifications
        influenced by other resources [Shichao_2012]_ [SO_15644964]_
        [SO_16694907]_.

    References:
        .. [Shichao_2012] https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
        .. [SO_15644964] http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
        .. [SO_16694907] http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        .. [TorchDL] https://github.com/pytorch/pytorch/blob/2787f1d8edbd4aadd4a8680d204341a1d7112e2d/torch/hub.py#L347

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
        >>> import pytest
        >>> import ubelt as ub
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> #fpath = download(url, hasher='sha1', hash_prefix='f79ea24571da6ddd2ba12e3d57b515249ecb8a35')
        >>> # test download from girder
        >>> #url = 'https://data.kitware.com/api/v1/item/5b4039308d777f2e6225994c/download'
        >>> #ub.download(url, hasher='sha512', hash_prefix='c98a46cb31205cf')
        >>> with pytest.raises(RuntimeError):
        >>>     ub.download(url, hasher='sha512', hash_prefix='BAD_HASH')
    """
    from ubelt import ProgIter as Progress
    from ubelt.util_path import Path
    import shutil
    import tempfile
    import hashlib

    if timeout is NoParam:
        import socket
        timeout = socket._GLOBAL_DEFAULT_TIMEOUT

    from urllib.request import urlopen  # NOQA

    if fpath and (dpath or fname):
        raise ValueError('Cannot specify fpath with dpath or fname')
    if fpath is None:
        if dpath is None:
            dpath = Path.appdir(appname or 'ubelt').ensuredir()
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

    # TODO: might want to open the url with different args
    urldata = urlopen(url, timeout=timeout)

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
        if isinstance(hasher, str):
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
        # TODO: this outputs a lot of information that can bog down a CI
        # Might need to update defaults of ProgIter to reduce clutter
        _progkw = {
            'total': file_size,
            'freq': chunksize,
            'time_thresh': 1,
        }
        if progkw is not None:
            _progkw.update(progkw)
        _progkw['disable'] = not verbose
        pbar = Progress(**_progkw)
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
             expires=None, **download_kw):
    """
    Downloads a file, caches it, and returns its local path.

    If unspecified the location and name of the file is chosen automatically.
    A hash_prefix can be specified to verify the integrity of the downloaded
    data.

    Args:
        url (str): url of the file to download

        fpath (Optional[str | PathLike]):
            The full path to download the file to. If unspecified, the
            arguments `dpath` and `fname` are used to determine this.

        dpath (Optional[str | PathLike]):
            where to download the file. If unspecified `appname` is used to
            determine this. Mutually exclusive with fpath.

        fname (Optional[str]):
            What to name the downloaded file. Defaults to the url basename.
            Mutually exclusive with fpath.

        redo (bool, default=False): if True forces redownload of the file

        verbose (int):
            Verbosity flag. Quiet is 0, higher is more verbose. Defaults to 1.

        appname (str): set dpath to
            ``ub.get_app_cache_dir(appname or 'ubelt')`` if dpath and fpath are
            not given.

        hash_prefix (None | str):
            If specified, grabdata verifies that this matches the hash of the
            file, and then saves the hash in a adjacent file to certify that
            the download was successful. Defaults to None.

        hasher (str | Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.
            NOTE: Only pass hasher as a string. Passing as an instance is
            deprecated and can cause unexpected results.

        expires (str | int | datetime.datetime):
            when the cache should expire and redownload or the number of
            seconds to wait before the cache should expire.

        **download_kw: additional kwargs to pass to
            :func:`ubelt.util_download.download`

    Returns:
        str | PathLike: fpath - path to downloaded or cached file.

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
        >>> import json
        >>> fname = 'foo.bar'
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> prefix1 = '944389a39dfb8fa9'
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, verbose=3)
        >>> stamp_fpath = ub.Path(fpath + '.stamp_sha512.json')
        >>> assert json.loads(stamp_fpath.read_text())['hash'][0].startswith(prefix1)
        >>> # Check that the download doesn't happen again
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> # todo: check file timestamps have not changed
        >>> #
        >>> # Check redo works with hash
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, redo=True)
        >>> # todo: check file timestamps have changed
        >>> #
        >>> # Check that a redownload occurs when the stamp is changed
        >>> with open(stamp_fpath, 'w') as file:
        >>>     file.write('corrupt-stamp')
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> assert json.loads(stamp_fpath.read_text())['hash'][0].startswith(prefix1)
        >>> #
        >>> # Check that a redownload occurs when the stamp is removed
        >>> ub.delete(stamp_fpath)
        >>> with open(fpath, 'w') as file:
        >>>     file.write('corrupt-data')
        >>> assert not ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)
        >>> fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        >>> assert ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)
        >>> #
        >>> # Check that requesting new data causes redownload
        >>> #url2 = 'https://data.kitware.com/api/v1/item/5b4039308d777f2e6225994c/download'
        >>> #prefix2 = 'c98a46cb31205cf'  # hack SSL
        >>> url2 = 'http://i.imgur.com/rqwaDag.png'
        >>> prefix2 = '944389a39dfb8fa9'
        >>> fpath = ub.grabdata(url2, fname=fname, hash_prefix=prefix2)
        >>> assert json.loads(stamp_fpath.read_text())['hash'][0].startswith(prefix2)
    """
    from ubelt.util_path import Path
    from ubelt.util_cache import CacheStamp
    if appname and dpath:
        raise ValueError('Cannot specify appname with dpath')
    if fpath and (dpath or fname or appname):
        raise ValueError('Cannot specify fpath with dpath or fname')

    if fpath is None:
        if dpath is None:
            dpath = Path.appdir(appname or 'ubelt').ensuredir()
        if fname is None:
            fname = basename(url)
        fpath = join(dpath, fname)

    if dpath is None or fname is None:
        dpath, fname = split(fpath)

    if hasher is not None:
        if not isinstance(hasher, str):
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Pass hasher as a string, otherwise unexpected behavior can occur',
                name='hasher', type='grabdata arg',
                deprecate='1.1.0', error='1.3.0', remove='1.4.0')
            hasher_name = hasher.name
        else:
            hasher_name = hasher
    else:
        hasher_name = None

    if hasher_name is not None and hash_prefix:
        depends = hasher_name
    else:
        depends = ''
        # If the hash isn't specified, should we force download a different url
        # to the same file?
        # depends = url

    # TODO: it would be nice to have better control over the name of the stamp.
    # Specifically we have no control over the separator between fname,
    # depends, and the extension.
    stamp = CacheStamp(
        fname + '.stamp', dpath, depends=depends, hasher=hasher,
        ext='.json', product=fpath,
        hash_prefix=hash_prefix, verbose=verbose,
        expires=expires,
    )
    if redo or stamp.expired():
        try:
            if not hash_prefix or redo:
                raise Exception
            # If an expected hash is specified and the file exists, but the
            # stamp is invalid, try to simply compute the hash of the existing
            # file instead of redownloading it. Redownload if this fails.
            stamp.renew()
        except Exception:
            needs_download = 1
        else:
            needs_download = 0
        if needs_download:
            fpath = download(
                url, fpath, verbose=verbose, hash_prefix=hash_prefix,
                hasher=hasher, **download_kw)
            stamp.renew()
    return fpath
