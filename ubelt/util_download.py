"""
Helpers for downloading data

The :func:`download` function access the network and requests the content at a
specific url using :mod:`urllib`. You can either specify where the data goes or
download it to the default location in ubelt cache.  Either way this function
returns the location of the downloaded data. You can also specify the expected
hash in order to check the validity of the data. By default downloading is
verbose.

The :func:`grabdata` function is almost identitcal to :func:`download`, but it
checks if the data already exists in the download location, and only downloads
if it needs to.

"""

from __future__ import annotations

import os
import typing
from os.path import basename, dirname, exists, join, split

from ubelt.util_const import NoParam

if typing.TYPE_CHECKING:
    import datetime
    from typing import Any, BinaryIO, Mapping, cast

    from ubelt.util_const import NoParamType

    BytesLike = bytes | bytearray | memoryview

    class HasherLike(typing.Protocol):
        # name: str

        def update(self, data: BytesLike, /) -> None: ...

        def hexdigest(self) -> str: ...


__all__ = ['download', 'grabdata']

# todo: add overloads to indicate that when fpath is a str then str is returned


def download(
    url: str,
    fpath: str | os.PathLike | BinaryIO | None = None,
    dpath: str | os.PathLike | None = None,
    fname: str | None = None,
    appname: str | None = None,
    hash_prefix: str | None = None,
    hasher: str | HasherLike = 'sha512',
    chunksize: int = 8192,
    filesize: int | None = None,
    verbose: int | bool = 1,
    timeout: float | NoParamType = NoParam,
    progkw: Mapping[str, Any] | NoParamType | None = None,
    requestkw: Mapping[str, Any] | NoParamType | None = None,
) -> str | os.PathLike | BinaryIO:
    """
    Downloads a url to a file on disk and returns the path.

    If unspecified the location and name of the file is chosen automatically.
    A hash_prefix can be specified to verify the integrity of the downloaded
    data. This function will download the data every time its called. For
    cached downloading see :func:`grabdata`.

    Args:
        url (str):
            The url to download.

        fpath (str | os.PathLike[str] | BinaryIO | None):
            The path to download to. Defaults to basename of url and ubelt's
            application cache. If this is a :class:`io.BytesIO` object then
            information is directly written to this object (note this prevents
            the use of temporary files).

        dpath (str | os.PathLike[str] | None):
            where to download the file. If unspecified `appname` is used to
            determine this. Mutually exclusive with fpath.

        fname (str | None):
            What to name the downloaded file. Defaults to the url basename.
            Mutually exclusive with fpath.

        appname (str | None): set dpath to
            ``ub.Path.appdir(appname or 'ubelt', type='cache')``
            if dpath and fpath are not given.

        hash_prefix (str | None):
            If specified, download will retry / error if the file hash
            does not match this value. Defaults to None.

        hasher (str | HasherLike):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.

        chunksize (int):
            Download chunksize in bytes. Default to ``2 ** 13``

        filesize (int | None):
            If known, the filesize in bytes. If unspecified, attempts to
            read that data from content headers.

        verbose (int | bool):
            Verbosity flag. Quiet is 0, higher is more verbose. Defaults to 1.

        timeout (float | NoParamType):
            Specify timeout in seconds for :func:`urllib.request.urlopen`.  (if
            not specified, the global default timeout setting will be used)
            This only works for HTTP, HTTPS and FTP connections for blocking
            operations like the connection attempt.

        progkw (dict[str, object] | NoParamType | None):
            if specified provides extra arguments to the progress iterator.
            See :class:`ubelt.progiter.ProgIter` for available options.

        requestkw (dict[str, object] | NoParamType | None):
            if specified provides extra arguments to
            :class:`urllib.request.Request`, which can be used to customize
            headers and other low level information sent to the target server.
            The common use-case would be to specify ``headers: dict[str, str]``
            in order to "spoof" the user agent. E.g.
            ``headers={'User-Agent': 'Mozilla/5.0'}``. (new in ubelt 1.3.7).

    Returns:
        str | os.PathLike[str] | BinaryIO: fpath - path to the downloaded file.

    Raises:

        URLError - if there is problem downloading the url.

        RuntimeError - if the hash does not match the hash_prefix.

    Note:
        Based largely on code in pytorch [TorchDL]_ with modifications
        influenced by other resources [Shichao_2012]_ [SO_15644964]_
        [SO_16694907]_.

    References:
        .. [Shichao_2012] https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
        .. [SO_15644964] http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
        .. [SO_M16694907] http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        .. [TorchDL] https://github.com/pytorch/pytorch/blob/2787f1d8edbd4aadd4a8680d204341a1d7112e2d/torch/hub.py#L347

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> # The default usage is to simply download an image to the default
        >>> # download folder and return the path to the file.
        >>> import ubelt as ub
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = download(url)
        >>> print(ub.Path(fpath).name)
        rqwaDag.png

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> # To ensure you get the file you are expecting, it is a good idea
        >>> # to specify a hash that will be checked.
        >>> import ubelt as ub
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> fpath = ub.download(url, hasher='sha1', hash_prefix='f79ea24571da6ddd2ba12e3d57b515249ecb8a35')
        >>> print(ub.Path(fpath).name)
        Downloading url='http://i.imgur.com/rqwaDag.png' to fpath=...rqwaDag.png
        ...
        ...1233/1233... rate=... Hz, eta=..., total=...
        rqwaDag.png

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> # You can save directly to bytes in memory using a BytesIO object.
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
        >>> # Bad hashes will raise a RuntimeError, which could indicate
        >>> # corrupted data or a security issue.
        >>> import pytest
        >>> import ubelt as ub
        >>> url = 'http://i.imgur.com/rqwaDag.png'
        >>> with pytest.raises(RuntimeError):
        >>>     ub.download(url, hasher='sha512', hash_prefix='BAD_HASH')
    """
    import hashlib
    import pathlib
    import shutil
    import tempfile

    from ubelt import ProgIter as Progress
    from ubelt.util_platform import platform_cache_dir

    if timeout is NoParam:
        import socket

        timeout = socket._GLOBAL_DEFAULT_TIMEOUT  # type: ignore[unresolved-attribute]

    from urllib.request import Request, urlopen

    if fpath and (dpath or fname):
        raise ValueError('Cannot specify fpath with dpath or fname')
    if fpath is None:
        if dpath is None:
            cache_dpath = pathlib.Path(platform_cache_dir())
            dpath = cache_dpath / (appname or 'ubelt')
            dpath.mkdir(parents=True, exist_ok=True)
        if fname is None:
            fname = basename(url)
        fpath = join(dpath, fname)

    # Check if fpath was given as an BytesIO object
    _dst_is_io_object = hasattr(fpath, 'write')

    if not _dst_is_io_object and not exists(dirname(fpath)):  # type: ignore[no-matching-overload]
        raise Exception('parent of {} does not exist'.format(fpath))

    if verbose:
        if _dst_is_io_object:
            print('Downloading url={!r} to IO object'.format(url))
        else:
            print('Downloading url={!r} to fpath={!r}'.format(url, fpath))

    requestkw = requestkw or {}
    requestkw['headers'] = {'User-Agent': 'Mozilla/5.0'}  # type: ignore[invalid-assignment]
    req = Request(url, **requestkw)  # type: ignore[invalid-argument-type]
    urldata = urlopen(req, timeout=timeout)  # type: ignore[invalid-argument-type]

    meta = urldata.info()
    if filesize is None:
        try:
            if hasattr(meta, 'getheaders'):  # nocover
                filesize = int(meta.getheaders("Content-Length")[0])
            else:
                filesize = int(meta.get_all("Content-Length")[0])
        except Exception:  # nocover
            # sometimes the url does not contain content length metadata
            # TODO: find a public URL that exemplifies this or figure out how to
            # mock it locally.
            filesize = None

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

    if typing.TYPE_CHECKING:
        hasher = cast(HasherLike, hasher)

    if _dst_is_io_object:
        if typing.TYPE_CHECKING:
            fpath = cast(BinaryIO, fpath)
        _file_write = fpath.write
        tmp = None
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        _file_write = tmp.write

    # possible optimization (have not tested or timed)
    _urldata_read = urldata.read
    try:
        # TODO: this outputs a lot of information that can bog down a CI
        # Might need to update defaults of ProgIter to reduce clutter
        _progkw = {
            'total': filesize,
            # 'chunksize': chunksize,
            # 'freq': chunksize,
            'freq': 1,
            'time_thresh': 2,
            'adjust': False,
            'show_rate': False,
        }
        # import time
        # start_time = time.monotonic()

        def _build_extra():
            pbar._curr_measurement.time
            bytes_down = pbar._iter_idx
            total_seconds = pbar._total_seconds + 1E-9
            num_kb_down   = int(bytes_down) / 1024
            num_mb_down   = int(num_kb_down / 1024)
            kb_per_second = int(num_kb_down / (total_seconds))
            # fmt_msg = ' {:d} MB, {:d} KB/s'
            fmt_msg = ' {:d} KB/s'
            msg = fmt_msg.format(num_mb_down, kb_per_second)
            return msg

        if progkw is not None:
            _progkw.update(progkw)  # type: ignore[no-matching-overload]
        _progkw['disable'] = not verbose
        pbar = Progress(**_progkw)  # type: ignore[invalid-argument-type]

        pbar.set_extra(_build_extra)
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
            if typing.TYPE_CHECKING:
                tmp = cast(tempfile._TemporaryFileWrapper, tmp)
            tmp.close()

            # We keep a potentially corrupted file if the hash doesn't match.
            # It could be the case that the user simply specified the wrong
            # hash_prefix.
            if typing.TYPE_CHECKING:
                fpath = cast(str | os.PathLike, fpath)
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
            if typing.TYPE_CHECKING:
                tmp = cast(tempfile._TemporaryFileWrapper, tmp)
            tmp.close()
            # If for some reason the move failed, delete the temporary file
            if exists(tmp.name):
                os.remove(tmp.name)
    return fpath


def grabdata(
    url: str,
    fpath: str | os.PathLike | None = None,
    dpath: str | os.PathLike | None = None,
    fname: str | None = None,
    redo: bool = False,
    verbose: int = 1,
    appname: str | None = None,
    hash_prefix: str | None = None,
    hasher: str | HasherLike = 'sha512',
    expires: str | int | 'datetime.datetime' | None = None,
    **download_kw: Any,
) -> str | os.PathLike:
    """
    Downloads a file, caches it, and returns its local path.

    If unspecified the location and name of the file is chosen automatically.
    A hash_prefix can be specified to verify the integrity of the downloaded
    data.

    Args:
        url (str): url of the file to download

        fpath (str | os.PathLike[str] | None):
            The full path to download the file to. If unspecified, the
            arguments `dpath` and `fname` are used to determine this.

        dpath (str | os.PathLike[str] | None):
            where to download the file. If unspecified `appname` is used to
            determine this. Mutually exclusive with fpath.

        fname (str | None):
            What to name the downloaded file. Defaults to the url basename.
            Mutually exclusive with fpath.

        redo (bool): if True forces redownload of the file. Defaults to False.

        verbose (int):
            Verbosity flag. Quiet is 0, higher is more verbose. Defaults to 1.

        appname (str | None): set dpath to
            ``ub.get_app_cache_dir(appname or 'ubelt')`` if dpath and fpath are
            not given.

        hash_prefix (str | None):
            If specified, grabdata verifies that this matches the hash of the
            file, and then saves the hash in a adjacent file to certify that
            the download was successful. Defaults to None.

        hasher (str | _Hasher):
            If hash_prefix is specified, this indicates the hashing
            algorithm to apply to the file. Defaults to sha512.
            NOTE: Only pass hasher as a string. Passing as an instance is
            deprecated and can cause unexpected results.

        expires (str | int | datetime.datetime | None):
            when the cache should expire and redownload or the number of
            seconds to wait before the cache should expire.

        **download_kw: additional kwargs to pass to
            :func:`ubelt.util_download.download`. This includes ``chunksize``,
            ``filesize``, ``timeout``, ``progkw``, and ``requestkw``.

    Ignore:
        # helper logic to determine what needs to be documented for download_kw
        import ubelt as ub
        import inspect
        grabdata_sig = inspect.signature(ub.grabdata)
        download_sig = inspect.signature(ub.download)
        extra = ub.udict(download_sig.parameters) - ub.udict(grabdata_sig.parameters)
        print(', '.join([f'``{k}``' for k in extra.keys()]))

    Returns:
        str | os.PathLike[str]: fpath - path to downloaded or cached file.

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
    import pathlib

    from ubelt.util_cache import CacheStamp
    from ubelt.util_platform import platform_cache_dir

    if appname and dpath:
        raise ValueError('Cannot specify appname with dpath')
    if fpath and (dpath or fname or appname):
        raise ValueError('Cannot specify fpath with dpath or fname')

    if fpath is None:
        if dpath is None:
            cache_dpath = pathlib.Path(platform_cache_dir())
            dpath = cache_dpath / (appname or 'ubelt')
            dpath.mkdir(parents=True, exist_ok=True)
        if fname is None:
            fname = basename(url)
        fpath = join(dpath, fname)

    if dpath is None or fname is None:
        dpath, fname = split(fpath)

    if hasher is not None:
        if isinstance(hasher, str):
            hasher_name = hasher
        else:  # nocover
            from ubelt import schedule_deprecation
            schedule_deprecation(
                modname='ubelt',
                migration='Pass hasher as a string, otherwise unexpected behavior can occur',
                name='hasher', type='grabdata arg',
                deprecate='1.1.0', error='1.3.0', remove='1.5.0')
            hasher_name = getattr(hasher, 'name', None)
    else:
        hasher_name = None

    if hasher_name is not None and hash_prefix:
        depends = hasher_name
    else:
        depends = ''
        # If the hash isn't specified, should we force download a different url
        # to the same file?
        # depends = url

    if hasher_name is None:
        hasher_name = 'sha1'  # cache stamp doesnt handle none values

    # TODO: it would be nice to have better control over the name of the stamp.
    # Specifically we have no control over the separator between fname,
    # depends, and the extension.
    stamp = CacheStamp(
        fname + '.stamp',
        dpath,
        depends=depends,
        hasher=hasher_name,
        ext='.json',
        product=fpath,
        hash_prefix=hash_prefix,
        verbose=verbose,
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
                hasher=hasher, **download_kw)  # type: ignore[invalid-assignment]
            stamp.renew()
    assert fpath is not None
    return fpath
