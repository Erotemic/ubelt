from __future__ import annotations

import io
import os
import platform
import sys
import types
import typing
from os.path import basename, exists, join

import pytest

import ubelt as ub

IS_PYPY = platform.python_implementation() == 'PyPy'
IS_WIN32 = sys.platform.startswith('win32')


TIMEOUT = (15 if IS_PYPY else 5) * 30


@pytest.mark.timeout(TIMEOUT)
def test_download_no_fpath() -> None:
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(url, appname='ubelt/tests/test_download')

    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_download_with_fpath() -> None:
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url(1201)

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(
        url, fpath=fpath, appname='ubelt/tests/test_download'
    )
    assert got_fpath == fpath
    assert exists(fpath)

    with open(got_fpath, 'rb') as file:  # type: ignore
        data = file.read()
    assert len(data) > 1200, 'should have downloaded some bytes'


@pytest.mark.timeout(TIMEOUT)
def test_download_chunksize() -> None:
    # url = 'https://www.dropbox.com/s/jl506apezj42zjz/ibeis-win32-setup-ymd_hm-2015-08-01_16-28.exe?dl=1'
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(
        url, chunksize=2, appname='ubelt/tests/test_download'
    )

    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_download_cover_hashers() -> None:
    # url = 'https://www.dropbox.com/s/jl506apezj42zjz/ibeis-win32-setup-ymd_hm-2015-08-01_16-28.exe?dl=1'
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)

    # add coverage for different hashers
    ub.download(
        url,
        hasher='md5',
        hash_prefix='e09c80c42fda55f9d992e59ca6b33',
        dpath=dpath,
        fname=fname,
    )
    ub.download(
        url,
        hasher='sha256',
        hash_prefix='bf2cb58a68f684d95a3b78ef8f',
        dpath=dpath,
        fname=fname,
    )


@pytest.mark.timeout(TIMEOUT)
def test_download_hashalgo() -> None:
    # url = 'https://www.dropbox.com/s/jl506apezj42zjz/ibeis-win32-setup-ymd_hm-2015-08-01_16-28.exe?dl=1'
    import hashlib

    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(
        url,
        hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
        appname='ubelt/tests/test_download',
        hasher=hashlib.md5(),
    )

    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_cache() -> None:
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url, appname='ubelt/tests/test_download')
    assert got_fpath == fpath
    assert exists(fpath)

    ub.delete(fpath)
    assert not exists(fpath)

    ub.grabdata(url, appname='ubelt/tests/test_download')
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_nohash() -> None:
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    url = _demo_url()
    dpath = ub.Path.appdir(
        'ubelt/tests/test_download/test-grabdata-nohash'
    ).ensuredir()
    fname = basename(url)
    fpath = (dpath / fname).delete()
    assert not fpath.exists()
    ub.grabdata(url, fpath=fpath, hasher=None, verbose=10)  # type: ignore
    assert fpath.exists()
    # Even without the hasher, if the size of the data changes at all
    # we should be able to detect and correct it.
    orig_text = fpath.read_text()
    fpath.write_text('corrupted')
    ub.grabdata(url, fpath=fpath, hasher=None, verbose=10)  # type: ignore
    assert fpath.read_text() == orig_text


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_url_only() -> None:
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt')
    fname = basename(url)
    fpath = os.fspath(dpath / fname)

    got_fpath = ub.grabdata(url)
    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_with_fpath() -> None:
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url, fpath=fpath, verbose=3)
    assert got_fpath == fpath
    assert exists(fpath)

    ub.delete(fpath)
    assert not exists(fpath)

    ub.grabdata(url, fpath=fpath, verbose=3)
    assert exists(fpath)


def test_grabdata_missing_content_length(monkeypatch, tmp_path):
    class _FakeHeaders:
        def get(self, name, default=None):
            return None

        def get_all(self, name):
            return None

        def getheaders(self, name):
            raise KeyError(name)

    class _FakeResponse:
        def __init__(self, payload):
            self._buffer = io.BytesIO(payload)

        def read(self, size=-1):
            return self._buffer.read(size)

        def info(self):
            return _FakeHeaders()

        def close(self):
            self._buffer.close()

    payload = b'downloaded data'
    url = 'https://example.com/no-content-length'
    destination = tmp_path / 'content.bin'

    calls = []

    def _fake_urlopen(request, timeout=ub.NoParam):
        calls.append(request)
        return _FakeResponse(payload)

    monkeypatch.setattr('urllib.request.urlopen', _fake_urlopen)

    result = ub.grabdata(url, fpath=os.fspath(destination), hasher=None, verbose=0)
    assert result == os.fspath(destination)
    assert destination.read_bytes() == payload
    assert len(calls) == 1

    def _unexpected(*args, **kwargs):
        # A cached result should avoid issuing any network calls on subsequent
        # invocations, so fail loudly if ``grabdata`` reaches this stub.
        raise AssertionError('grabdata should reuse the cached file')

    monkeypatch.setattr('urllib.request.urlopen', _unexpected)
    ub.grabdata(url, fpath=os.fspath(destination), hasher=None, verbose=0)


def _broken_content_length_accessor(name):
    raise ValueError('broken Content-Length metadata')


@pytest.mark.parametrize(
    ('headers', 'expected_total'),
    [
        pytest.param({'Content-Length': '9'}, 9, id='mapping-get'),
        # A get-only container is the case the implementation in main misses.
        pytest.param(
            types.SimpleNamespace(get=lambda name: '9'),
            9,
            id='get-only',
        ),
        pytest.param(
            types.SimpleNamespace(get=lambda name: b'9'),
            9,
            id='bytes',
        ),
        pytest.param(
            types.SimpleNamespace(get_all=lambda name: ['9']),
            9,
            id='get-all-only',
        ),
        pytest.param(
            types.SimpleNamespace(getheaders=lambda name: ['9']),
            9,
            id='getheaders-only',
        ),
        pytest.param(
            types.SimpleNamespace(
                get=lambda name: 'invalid', get_all=lambda name: ['9']
            ),
            9,
            id='malformed-get-falls-back',
        ),
        pytest.param(
            types.SimpleNamespace(
                get=_broken_content_length_accessor,
                get_all=lambda name: ['9'],
            ),
            9,
            id='raising-get-falls-back',
        ),
        pytest.param(
            types.SimpleNamespace(
                get=_broken_content_length_accessor,
                get_all=_broken_content_length_accessor,
                getheaders=lambda name: ['9'],
            ),
            9,
            id='raising-accessors-fall-back',
        ),
        pytest.param(
            types.SimpleNamespace(get=lambda name: None),
            None,
            id='missing',
        ),
        pytest.param(
            types.SimpleNamespace(get=lambda name: 'invalid'),
            None,
            id='invalid',
        ),
        pytest.param(
            types.SimpleNamespace(get=lambda name: '-9'),
            None,
            id='negative',
        ),
        pytest.param(
            types.SimpleNamespace(get=lambda name: '0'),
            0,
            id='zero',
        ),
        pytest.param(
            types.SimpleNamespace(get_all=lambda name: []),
            None,
            id='empty-get-all',
        ),
    ],
)
def test_download_content_length_progress_total(
    monkeypatch, headers, expected_total
):
    """Assert the inferred total, not just successful download or caching."""
    import urllib.request

    payload = b'123456789'
    observed_totals = []

    class FakeResponse:
        def __init__(self):
            self.stream = io.BytesIO(payload)

        def info(self):
            return headers

        def read(self, size=-1):
            return self.stream.read(size)

        def close(self):
            self.stream.close()

    original_progress = ub.ProgIter

    class RecordingProgress(original_progress):
        def __init__(self, **kwargs):
            observed_totals.append(kwargs.get('total'))
            super().__init__(**kwargs)

    monkeypatch.setattr(
        urllib.request, 'urlopen', lambda req, timeout=None: FakeResponse()
    )
    monkeypatch.setattr(ub, 'ProgIter', RecordingProgress)

    output = io.BytesIO()
    result = ub.download('https://example.test/file', fpath=output, verbose=0)
    assert result is output
    assert output.getvalue() == payload
    assert observed_totals == [expected_total]


def test_download_content_length_explicit_filesize(monkeypatch):
    """An explicit filesize takes precedence over response metadata."""
    import urllib.request

    observed_totals = []
    original_progress = ub.ProgIter

    class RecordingProgress(original_progress):
        def __init__(self, **kwargs):
            observed_totals.append(kwargs.get('total'))
            super().__init__(**kwargs)

    class FakeResponse:
        def info(self):
            raise AssertionError('do not inspect metadata when size is given')

        def read(self, size=-1):
            return b''

        def close(self):
            pass

    monkeypatch.setattr(
        urllib.request, 'urlopen', lambda req, timeout=None: FakeResponse()
    )
    monkeypatch.setattr(ub, 'ProgIter', RecordingProgress)

    ub.download(
        'https://example.test/file', fpath=io.BytesIO(), filesize=17, verbose=0
    )
    assert observed_totals == [17]


class _TrackedDownloadResponse:
    """Minimal urllib-like response with observable cleanup and read errors."""

    def __init__(self, data, *, read_failure=False, metadata_failure=False):
        self.buffer = io.BytesIO(data)
        self.data_len = len(data)
        self.read_failure = read_failure
        self.metadata_failure = metadata_failure
        self.read_count = 0
        self.close_count = 0
        self.on_read = None

    def info(self):
        if self.metadata_failure:
            raise ValueError('bad response metadata')
        return {'Content-Length': str(self.data_len)}

    def read(self, size=-1):
        self.read_count += 1
        if self.on_read is not None:
            self.on_read()
        if self.read_failure and self.read_count == 2:
            raise OSError('interrupted transfer')
        return self.buffer.read(size)

    def close(self):
        self.close_count += 1
        self.buffer.close()


@pytest.mark.parametrize('existing', [False, True], ids=['new', 'existing'])
@pytest.mark.parametrize(
    'hash_ok', [False, True], ids=['bad-hash', 'valid-hash']
)
def test_download_verified_file_replacement(
    monkeypatch, tmp_path, existing, hash_ok
):
    """A rejected transfer cannot destroy a previous destination."""
    import hashlib
    import urllib.request

    destination = tmp_path / 'destination.bin'
    original = b'previous valid data'
    payload = b'new response bytes'
    if existing:
        destination.write_bytes(original)

    response = _TrackedDownloadResponse(payload)
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)

    def check_during_transfer():
        # Even after writing some chunks, the old destination is untouched.
        if existing:
            assert destination.read_bytes() == original
        else:
            assert not destination.exists()
        candidates = [p for p in tmp_path.iterdir() if p != destination]
        assert len(candidates) == 1
        assert candidates[0].is_file()

    response.on_read = check_during_transfer
    digest = hashlib.sha256(payload).hexdigest()
    prefix = digest[:16] if hash_ok else 'bad-digest'

    if hash_ok:
        got = ub.download(
            'https://example.test/file', fpath=destination,
            hash_prefix=prefix, hasher='sha256', chunksize=4, verbose=0,
        )
        assert got == destination
    else:
        with pytest.raises(RuntimeError, match='invalid hash value'):
            ub.download(
                'https://example.test/file', fpath=destination,
                hash_prefix=prefix, hasher='sha256', chunksize=4, verbose=0,
            )

    # Hash-typo recovery is intentionally retained if there was no file.
    expected = payload if hash_ok or not existing else original
    assert destination.read_bytes() == expected
    assert list(tmp_path.iterdir()) == [destination]
    assert response.close_count == 1


@pytest.mark.parametrize('existing', [False, True], ids=['new', 'existing'])
def test_download_interrupted_read_keeps_destination(
    monkeypatch, tmp_path, existing
):
    """Failed reads discard temporary data and leave old files unchanged."""
    import urllib.request

    destination = tmp_path / 'destination.bin'
    original = b'previous valid data'
    if existing:
        destination.write_bytes(original)
    response = _TrackedDownloadResponse(
        b'new response bytes', read_failure=True
    )
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)

    with pytest.raises(OSError, match='interrupted transfer'):
        ub.download(
            'https://example.test/file', fpath=destination,
            chunksize=4, verbose=0,
        )

    if existing:
        assert destination.read_bytes() == original
        assert list(tmp_path.iterdir()) == [destination]
    else:
        assert not list(tmp_path.iterdir())
    assert response.close_count == 1


def test_download_write_error_keeps_existing_file(monkeypatch, tmp_path):
    """Partial temporary-file writes never reach the old destination."""
    import tempfile
    import urllib.request

    destination = tmp_path / 'destination.bin'
    destination.write_bytes(b'previous valid data')
    response = _TrackedDownloadResponse(b'new response bytes')
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)

    original_named_temp = tempfile.NamedTemporaryFile

    def failing_tempfile(*args, **kwargs):
        tmp = original_named_temp(*args, **kwargs)

        def fail_after_partial_write(data):
            tmp.file.write(data[:1])
            raise OSError('disk write failure')

        tmp.write = fail_after_partial_write
        return tmp

    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', failing_tempfile)
    with pytest.raises(OSError, match='disk write failure'):
        ub.download(
            'https://example.test/file', fpath=destination,
            verbose=0, chunksize=4,
        )
    assert destination.read_bytes() == b'previous valid data'
    assert list(tmp_path.iterdir()) == [destination]
    assert response.close_count == 1


@pytest.mark.parametrize(
    'hash_ok', [False, True], ids=['bad-hash', 'valid-hash']
)
def test_download_stream_is_caller_owned(monkeypatch, hash_ok):
    """Caller-provided streams are never closed, even on hash failure."""
    import hashlib
    import urllib.request

    payload = b'new response bytes'
    response = _TrackedDownloadResponse(payload)
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)
    stream = io.BytesIO()
    digest = hashlib.sha256(payload).hexdigest()
    prefix = digest[:16] if hash_ok else 'bad-digest'

    if hash_ok:
        assert ub.download(
            'https://example.test/file', fpath=stream, hash_prefix=prefix,
            hasher='sha256', chunksize=4, verbose=0,
        ) is stream
    else:
        with pytest.raises(RuntimeError, match='invalid hash value'):
            ub.download(
                'https://example.test/file', fpath=stream, hash_prefix=prefix,
                hasher='sha256', chunksize=4, verbose=0,
            )
    assert stream.getvalue() == payload
    assert not stream.closed
    assert response.close_count == 1


@pytest.mark.parametrize(('option', 'value'), [
    ('chunksize', 0), ('chunksize', -3), ('chunksize', 1.5),
    ('chunksize', True), ('filesize', -1),
])
def test_download_invalid_sizes_prevent_network(monkeypatch, option, value):
    """Invalid transfer sizes fail before opening a URL."""
    import urllib.request

    def unexpected_request(*args, **kwargs):
        raise AssertionError('should not reach the network')

    monkeypatch.setattr(urllib.request, 'urlopen', unexpected_request)
    with pytest.raises(ValueError):
        ub.download(
            'https://example.test/file', fpath=io.BytesIO(), verbose=0,
            **{option: value},
        )


def test_download_response_closes_on_metadata_failure(monkeypatch, tmp_path):
    """Failure before opening the temporary file still closes the response."""
    import urllib.request

    destination = tmp_path / 'destination.bin'
    destination.write_bytes(b'keep me')
    response = _TrackedDownloadResponse(b'data', metadata_failure=True)
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)
    with pytest.raises(ValueError, match='bad response metadata'):
        ub.download('https://example.test/file', fpath=destination, verbose=0)
    assert response.close_count == 1
    assert destination.read_bytes() == b'keep me'
    assert list(tmp_path.iterdir()) == [destination]


def test_download_response_closes_when_tempfile_fails(monkeypatch, tmp_path):
    """Opening the destination temp file must not leak the HTTP response."""
    import tempfile
    import urllib.request

    response = _TrackedDownloadResponse(b'data')
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)

    def fail_to_open_temp(*args, **kwargs):
        raise OSError('cannot create temporary file')

    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', fail_to_open_temp)
    destination = tmp_path / 'destination.bin'
    with pytest.raises(OSError, match='cannot create temporary file'):
        ub.download('https://example.test/file', fpath=destination, verbose=0)
    assert response.close_count == 1
    assert not list(tmp_path.iterdir())



def test_download_relative_destination(monkeypatch, tmp_path):
    """A bare relative filename uses the current directory for its temp."""
    import urllib.request

    monkeypatch.chdir(tmp_path)
    response = _TrackedDownloadResponse(b'bytes')
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)
    assert ub.download(
        'https://example.test/file', fpath='relative.bin', verbose=0,
    ) == 'relative.bin'
    assert (tmp_path / 'relative.bin').read_bytes() == b'bytes'
    assert list(tmp_path.iterdir()) == [tmp_path / 'relative.bin']
    assert response.close_count == 1


def test_download_explicit_no_param_progress(monkeypatch):
    """The public NoParam sentinel behaves like an omitted progkw."""
    import urllib.request

    response = _TrackedDownloadResponse(b'bytes')
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: response)
    dest = io.BytesIO()
    assert ub.download(
        'https://example.test/file', fpath=dest,
        progkw=ub.NoParam, verbose=0,
    ) is dest
    assert dest.getvalue() == b'bytes'
    assert response.close_count == 1


def test_grabdata_value_error() -> None:
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    with pytest.raises(ValueError):
        ub.grabdata(url, fname=fname, fpath=fpath, dpath=dpath)

    with pytest.raises(ValueError):
        ub.grabdata(url, fname=fname, fpath=fpath)

    with pytest.raises(ValueError):
        ub.grabdata(url, dpath=dpath, fpath=fpath)

    with pytest.raises(ValueError):
        ub.grabdata(url, fpath=fpath, appname='foobar')

    with pytest.raises(ValueError):
        ub.grabdata(url, dpath=dpath, appname='foobar')


@pytest.mark.timeout(TIMEOUT * 2)
def test_download_bad_url() -> None:
    """
    Check that we error when the url is bad

    Notes:
        For some reason this can take a long time to realize there is no URL,
        even if the timeout is specified and fairly low.

    CommandLine:
        python tests/test_download.py test_download_bad_url --verbose
    """
    import pytest

    pytest.skip('This takes a long time to timeout and I dont understand why')

    url = 'http://www.a-very-incorrect-url.gov/does_not_exist.txt'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')

    # Ensure the opener exist
    # import urllib.request as urllib_x
    from urllib.error import URLError  # NOQA
    # if urllib_x._opener is None:
    #     urllib_x.install_opener(urllib_x.build_opener())

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    with pytest.raises(URLError):
        ub.download(url, fpath=fpath, verbose=1, timeout=1.0)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_fname_only() -> None:
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    # fname = 'mario.png'

    url = _demo_url()

    dpath = ub.Path.appdir('ubelt')
    fname = 'custom_text.txt'
    fpath = os.fspath(dpath / fname)

    got_fpath = ub.grabdata(url, fname=fname)
    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_dpath_only() -> None:
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    got_fpath = ub.grabdata(url, dpath=dpath)
    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_fpath_and_dpath() -> None:
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    with pytest.raises(ValueError):
        ub.grabdata(url, fpath='foo', dpath='bar')


# @pytest.mark.timeout(TIMEOUT)
def test_grabdata_hash_typo() -> None:
    """
    CommandLine:
        pytest ~/code/ubelt/tests/test_download.py -k test_grabdata_hash_typo --network -s
        xdoctest ~/code/ubelt/tests/test_download.py test_grabdata_hash_typo --network

    """
    # url = 'https://www.dropbox.com/s/jl506apezj42zjz/ibeis-win32-setup-ymd_hm-2015-08-01_16-28.exe?dl=1'
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')

    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download')
    fname = basename(url)
    fpath = dpath / fname
    stamp_fpath = fpath.augment(tail='.stamp_md5.json')

    for verbose in [5]:
        fpath.delete()
        stamp_fpath.delete()
        assert not exists(fpath)

        print('[STEP1] Downloading file, but we have a typo in the hash')
        with pytest.raises(RuntimeError):
            got_fpath = ub.grabdata(
                url,
                hash_prefix='e09c80c42fda5-typo-5f9d992e59ca6b3307d',
                hasher='md5',
                verbose=verbose,
                appname='ubelt/tests/test_download',
            )
        assert fpath.exists()
        real_hash = ub.hash_file(fpath, hasher='md5')
        real_hash

        print(
            '[STEP2] Fixing the typo recomputes the hash, but does not redownload the file'
        )
        got_fpath = ub.grabdata(
            url,
            hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
            hasher='md5',
            verbose=verbose,
            appname='ubelt/tests/test_download',
        )
        assert ub.Path(got_fpath).resolve() == fpath.resolve()
        assert fpath.exists()

        # If we delete the .hash file we will simply recompute
        stamp_fpath.delete()
        print('[STEP3] Deleting the hash file recomputes the hash')
        got_fpath = ub.grabdata(
            url,
            fpath=fpath,
            hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
            hasher='md5',
            verbose=verbose,
        )
        assert stamp_fpath.exists()


def test_grabdata_rejects_nonstring_hasher() -> None:
    import hashlib

    url = _demo_url()
    with pytest.raises(TypeError, match='hasher must be a string'):
        ub.grabdata(
            url,
            hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
            hasher=hashlib.md5(),
        )


def _devcheck_progres_download_bar() -> None:
    """
    import sys, ubelt
    sys.path.append(ubelt.expandpath('~/remote/toothbrush/code/ubelt/tests'))
    from test_download import SingletonTestServer
    import ubelt as ub
    """
    self = SingletonTestServer.instance()
    urls = self.write_file(filebytes=85717624)

    import time

    class DummyIO:
        def write(self, msg: str) -> None:
            time.sleep(0.0005)
            ...

    file = DummyIO()
    url = urls[0]
    dl_file = ub.download(url, fpath=file, progkw=dict(desc='dling'))  # type: ignore
    dl_file


class SingletonTestServer(ub.NiceRepr):
    """
    A singleton class used for testing.

    This could be done via a pytest fixture, but... I don't want to use
    fixtures until its easy and clear how to make an instance of them in an
    independent IPython session.

    CommandLine:
        xdoctest -m tests/test_download.py SingletonTestServer

    Note:
        We rely on python process close mechanisms to clean this server up.
        Might need to re-investigate this in the future.

    Ignore:
        >>> self = SingletonTestServer.instance()
        >>> print('self = {!r}'.format(self))
        >>> url = self.urls[0]
        >>> print('url = {!r}'.format(url))
        >>> dl_file = ub.download(url)
    """

    _instance: typing.Any = None

    @classmethod
    def instance(cls) -> 'SingletonTestServer':
        if cls._instance is not None:
            self = cls._instance
        else:
            self = cls()
            cls._instance = self
        return self

    def close(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()
        self.__class__.instance = None  # type: ignore

    def __nice__(self) -> str:
        if self.proc is None:
            return '{} - file'.format(self.root_url)
        return '{} - {}'.format(self.root_url, self.proc.returncode)

    def __init__(self) -> None:
        import socket
        import sys
        import time
        from contextlib import closing

        import ubelt as ub

        def find_free_port() -> int:
            """
            References:
                .. [SO1365265] https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
            """
            with closing(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ) as s:
                s.bind(('', 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return s.getsockname()[1]

        dpath = ub.Path.appdir(
            'ubelt/tests/test_download/simple_server'
        ).ensuredir()
        self.dpath = dpath

        # Fallback to file:// URLs when sockets are restricted. This keeps
        # download tests meaningful in sandboxed environments where binding
        # localhost is not permitted.
        self.use_file_urls = False
        try:
            port = find_free_port()
        except PermissionError:
            # Socket creation/bind not allowed; use local file URLs instead.
            self.use_file_urls = True
            port = None
        else:
            print('port = {!r}'.format(port))

        if self.use_file_urls:
            # No HTTP server process; serve files directly via file:// URLs.
            self.proc = None
            self.root_url = self.dpath.resolve().as_uri()
        else:
            # Normal path: spin up a localhost HTTP server for real downloads.
            import requests  # type: ignore[import-untyped]

            if sys.platform.startswith('win32'):
                pyexe = 'python'
            else:
                pyexe = sys.executable

            server_cmd = [pyexe, '-m', 'http.server', str(port)]
            info = ub.cmd(server_cmd, detach=True, cwd=dpath)
            proc = info['proc']
            self.proc = proc
            self.root_url = 'http://localhost:{}'.format(port)

            if IS_PYPY and IS_WIN32:
                # not sure why
                import pytest

                pytest.skip(
                    'not sure why download tests are failing on pypy win32'
                )
                init_sleeptime = 0.5
                fail_sleeptime = 0.3
                timeout = 10
            else:
                init_sleeptime = 0.002
                fail_sleeptime = 0.01
                timeout = 1

            time.sleep(init_sleeptime)
            # Wait for the server to be alive
            status_code = None
            max_tries = 300
            for _ in range(max_tries):
                try:
                    resp = requests.get(self.root_url, timeout=timeout)
                except requests.exceptions.ConnectionError:
                    time.sleep(fail_sleeptime)
                else:
                    status_code = resp.status_code
                if status_code == 200:
                    break

            poll_ret = self.proc.poll()

            if poll_ret is not None:
                print('poll_ret = {!r}'.format(poll_ret))
                print(self.proc.communicate())
                raise AssertionError(
                    'Simple server did not start {}'.format(poll_ret)
                )

        self.urls: list[str] = []
        self.write_file()

    def write_file(self, filebytes: int = 10, num_files: int = 1) -> list[str]:
        fnames = [
            'file_{}_{}.txt'.format(filebytes, i) for i in range(num_files)
        ]
        for fname in fnames:
            # data = ''.join(random.choices(string.ascii_letters, k=filebytes))
            data = 'a' * filebytes
            fpath = join(self.dpath, fname)
            with open(fpath, 'w') as file:
                file.write(data)
        if self.use_file_urls:
            # Build file:// URLs when we cannot use sockets.
            urls = [
                ub.Path(join(self.dpath, fname)).resolve().as_uri()
                for fname in fnames
            ]
        else:
            # Build http:// URLs when we have a local server.
            urls = ['{}/{}'.format(self.root_url, fname) for fname in fnames]
        self.urls.extend(urls)
        return urls


def test_local_download() -> None:
    server = SingletonTestServer.instance()
    url = server.write_file(filebytes=int(10 * 2**20))[0]
    # also test with a timeout for lazy coverage
    ub.download(url, timeout=3000)


def _demo_url(num_bytes: int | None = None) -> str:
    REAL_URL = False
    if REAL_URL:
        url = 'http://i.imgur.com/rqwaDag.png'
        if not ub.argflag('--network'):
            pytest.skip('not running network tests')
    else:
        if num_bytes is None:
            url = SingletonTestServer.instance().urls[0]
        else:
            url = SingletonTestServer.instance().write_file(num_bytes)[0]
    return url


@pytest.mark.timeout(TIMEOUT)
def test_download_with_progkw() -> None:
    """
    Test that progkw is properly passed through to ub.download
    """
    url = _demo_url(128 * 10)
    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)
    with ub.CaptureStdout() as cap:
        ub.download(
            url,
            fpath=fpath,
            progkw={'verbose': 3, 'freq': 1, 'adjust': False, 'time_thresh': 0},
            chunksize=128,
        )
    assert cap.text is not None
    assert len(cap.text.split('\n')) > 10


@pytest.mark.timeout(TIMEOUT)
def test_download_with_filesize() -> None:
    """
    Test that progkw is properly passed through to ub.download
    """
    url = _demo_url(128 * 10)
    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)
    with ub.CaptureStdout() as cap:
        ub.download(
            url,
            filesize=11,
            fpath=fpath,
            progkw={'verbose': 3, 'freq': 1, 'adjust': False, 'time_thresh': 0},
            chunksize=128,
        )
    import re

    assert cap.text is not None
    assert re.search(r'\d\d\d\d\.\d\d%', cap.text), 'should report over 100%'


def make_stat_dict(stat_obj: object) -> dict[str, object]:
    # Convert the stat tuple to a dict we can manipulate
    # and ignore access time
    ignore_keys = {'st_atime', 'st_atime_ns'}
    return {
        k: getattr(stat_obj, k)
        for k in dir(stat_obj)
        if k.startswith('st_') and k not in ignore_keys
    }


def test_grabdata() -> None:
    import json
    import time

    import ubelt as ub

    # fname = 'foo.bar'
    # url = 'http://i.imgur.com/rqwaDag.png'
    # prefix1 = '944389a39dfb8fa9'
    url = _demo_url(128 * 11)
    prefix1 = 'b7fa848cd088ae842a89'
    fname = 'foo2.bar'
    #
    print('1. Download the file once')
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, hasher='sha512')
    stat0 = make_stat_dict(ub.Path(fpath).stat())
    stamp_fpath = ub.Path(fpath).augment(tail='.stamp_sha512.json')
    assert json.loads(stamp_fpath.read_text())['hash'][0].startswith(prefix1)
    #
    print("2. Rerun and check that the download doesn't happen again")
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
    stat1 = make_stat_dict(ub.Path(fpath).stat())
    assert stat0 == stat1, 'the file should not be modified'
    #
    print('3. Set redo=True, which should force a redownload')
    sleep_time = 0.1
    num_tries = 60
    for _ in range(num_tries):
        fpath = ub.grabdata(
            url, fname=fname, hash_prefix=prefix1, redo=True, hasher='sha512'
        )
        stat2 = make_stat_dict(ub.Path(fpath).stat())
        # Note: the precision of mtime is too low for this test work reliably
        # https://apenwarr.ca/log/20181113
        if stat2 != stat1:
            break
        print(
            '... Sometimes the redownload happens so fast we need to '
            'wait to notice the file is actually different'
        )
        time.sleep(sleep_time)
    else:
        raise AssertionError(
            'the file stat should be modified, we waited over {}s.'.format(
                sleep_time * num_tries
            )
        )
    #
    print('4. Check that a redownload occurs when the stamp is changed')
    stamp_fpath.write_text('corrupt-stamp')
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, hasher='sha512')
    assert json.loads(stamp_fpath.read_text())['hash'][0].startswith(prefix1)
    #
    print('5. Check that a redownload occurs when the stamp is removed')
    ub.delete(stamp_fpath)
    fpath = ub.Path(fpath)
    fpath.write_text('corrupt-stamp')
    assert not ub.hash_file(fpath, base='hex', hasher='sha512').startswith(
        prefix1
    )
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, hasher='sha512')
    assert ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)


def test_grabdata_same_fpath_different_url() -> None:
    url1 = _demo_url(128 * 11)
    url2 = _demo_url(128 * 12)
    url3 = _demo_url(128 * 13)

    fname = 'foobar'
    fpath1 = ub.grabdata(
        url1,
        fname=fname,
        hash_prefix='b7fa848cd088ae842a89ef',
        hasher='sha512',
        verbose=100,
    )
    stat1 = make_stat_dict(ub.Path(fpath1).stat())

    # Should requesting a new url, even with the same fpath, cause redownload?
    fpath2 = ub.grabdata(
        url2, fname=fname, hash_prefix=None, hasher='sha512', verbose=100
    )
    stat2 = make_stat_dict(ub.Path(fpath2).stat())

    fpath3 = ub.grabdata(
        url3, fname=fname, hash_prefix=None, hasher='sha512', verbose=100
    )
    stat3 = make_stat_dict(ub.Path(fpath3).stat())

    assert stat1 != stat2, (
        'the stats will change because we did not specify a hash prefix'
    )
    assert stat2 == stat3, 'we may change this behavior in the future'

    fpath3 = ub.grabdata(
        url2,
        fname=fname,
        hash_prefix='43f92597d7eb08b57c88b6',
        hasher='sha512',
        verbose=100,
    )
    stat3 = make_stat_dict(ub.Path(fpath3).stat())
    assert stat1 != stat3, (
        'if we do specify a new hash, we should get a new download'
    )
    assert url1 != url2, 'urls should be different'
    assert ub.allsame([fpath1, fpath2, fpath3]), 'all fpaths should be the same'


def test_grabdata_delete_hash_stamp() -> None:
    import ubelt as ub

    fname = 'foo3.bar'
    url = _demo_url(128 * 12)
    prefix1 = '43f92597d7eb08b57c88b636'
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
    stamp_fpath = ub.Path(str(fpath) + '.stamp_sha512.json')
    ub.delete(stamp_fpath)
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)


def test_download_with_io() -> None:
    import io

    import ubelt as ub

    url = _demo_url(128 * 3)
    file = io.BytesIO()
    fpath = ub.download(url, file)
    assert fpath is file
    file.seek(0)
    data = file.read()
    hashstr = ub.hash_data(data, hasher='sha1')
    assert hashstr.startswith('45a5c851bf12d1')


def test_download_with_sha1_hasher() -> None:
    import ubelt as ub

    url = _demo_url(128 * 4)
    ub.download(url, hasher='sha1', hash_prefix='164557facb7392')


def setup_module(module: object) -> None:
    """setup any state specific to the execution of the given module."""
    SingletonTestServer.instance()


def teardown_module(module: object) -> None:
    """teardown any state that was previously setup with a setup_module
    method.
    """
    SingletonTestServer.instance().close()


def test_download_requestkw_headers_are_merged_without_mutation(monkeypatch) -> None:
    import copy
    import io
    import urllib.request

    import ubelt as ub

    captured = {}
    data = b'payload'

    class FakeMeta:
        def get_all(self, key):
            if key == 'Content-Length':
                return [str(len(data))]
            return None

    class FakeResponse:
        def __init__(self):
            self.stream = io.BytesIO(data)

        def info(self):
            return FakeMeta()

        def read(self, size=-1):
            return self.stream.read(size)

        def close(self):
            self.stream.close()

    def fake_request(url, **kwargs):
        captured['url'] = url
        captured['requestkw'] = kwargs
        return object()

    def fake_urlopen(req, timeout=None):
        return FakeResponse()

    monkeypatch.setattr(urllib.request, 'Request', fake_request)
    monkeypatch.setattr(urllib.request, 'urlopen', fake_urlopen)

    requestkw = {
        'headers': {
            'Authorization': 'secret',
            'User-Agent': 'custom-agent',
        },
        'method': 'GET',
    }
    original = copy.deepcopy(requestkw)
    file = io.BytesIO()
    ub.download(
        'https://example.test/data',
        fpath=file,
        verbose=0,
        requestkw=requestkw,
    )

    assert requestkw == original
    assert captured['requestkw']['method'] == 'GET'
    assert captured['requestkw']['headers'] == {
        'Authorization': 'secret',
        'User-Agent': 'custom-agent',
    }
    assert file.getvalue() == data


def test_download_progress_reports_rate(monkeypatch) -> None:
    import io
    import types
    import urllib.request

    import ubelt as ub

    data = b'x' * 2048
    extras = []

    class FakeMeta:
        def get_all(self, key):
            if key == 'Content-Length':
                return [str(len(data))]
            return None

    class FakeResponse:
        def __init__(self):
            self.stream = io.BytesIO(data)

        def info(self):
            return FakeMeta()

        def read(self, size=-1):
            return self.stream.read(size)

        def close(self):
            self.stream.close()

    class FakeProgress:
        def __init__(self, **kwargs):
            self._iter_idx = 0
            self._total_seconds = 0.25
            self._curr_measurement = types.SimpleNamespace(time=0.25)
            self._extra_fn = None

        def set_extra(self, func):
            self._extra_fn = func

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def update(self, amount):
            self._iter_idx += amount
            if self._extra_fn is not None:
                extras.append(self._extra_fn())

    monkeypatch.setattr(urllib.request, 'Request', lambda url, **kw: object())
    monkeypatch.setattr(
        urllib.request, 'urlopen', lambda req, timeout=None: FakeResponse()
    )
    monkeypatch.setattr(ub, 'ProgIter', FakeProgress)

    ub.download(
        'https://example.test/data',
        fpath=io.BytesIO(),
        verbose=1,
        chunksize=len(data),
    )
    assert extras
    assert extras[-1] == ' 7 KB/s'

if __name__ == '__main__':
    """
    CommandLine:
        pytest ubelt/tests/test_download.py
    """
    import xdoctest

    xdoctest.doctest_module(__file__)
