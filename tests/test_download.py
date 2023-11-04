import ubelt as ub
import os
import pytest
import sys
from os.path import basename, join, exists
import platform


IS_PYPY = platform.python_implementation() == 'PyPy'
IS_WIN32 = sys.platform.startswith('win32')


TIMEOUT = (15 if IS_PYPY else 5) * 30


@pytest.mark.timeout(TIMEOUT)
def test_download_no_fpath():
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
def test_download_with_fpath():
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url(1201)

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)

    ub.delete(fpath)
    assert not exists(fpath)

    got_fpath = ub.download(url, fpath=fpath,
                            appname='ubelt/tests/test_download')
    assert got_fpath == fpath
    assert exists(fpath)

    with open(got_fpath, 'rb') as file:
        data = file.read()
    assert len(data) > 1200, 'should have downloaded some bytes'


@pytest.mark.timeout(TIMEOUT)
def test_download_chunksize():
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

    got_fpath = ub.download(url, chunksize=2, appname='ubelt/tests/test_download')

    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_download_cover_hashers():
    # url = 'https://www.dropbox.com/s/jl506apezj42zjz/ibeis-win32-setup-ymd_hm-2015-08-01_16-28.exe?dl=1'
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)

    # add coverage for different hashers
    ub.download(url, hasher='md5', hash_prefix='e09c80c42fda55f9d992e59ca6b33',
                dpath=dpath, fname=fname)
    ub.download(url, hasher='sha256', hash_prefix='bf2cb58a68f684d95a3b78ef8f',
                dpath=dpath, fname=fname)


@pytest.mark.timeout(TIMEOUT)
def test_download_hashalgo():
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

    got_fpath = ub.download(url,
                            hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
                            appname='ubelt/tests/test_download',
                            hasher=hashlib.md5())

    assert got_fpath == fpath
    assert exists(fpath)


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_cache():
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
def test_grabdata_nohash():
    """
    Check where the url is downloaded to when fpath is not specified.
    """
    url = _demo_url()
    dpath = ub.Path.appdir('ubelt/tests/test_download/test-grabdata-nohash').ensuredir()
    fname = basename(url)
    fpath = (dpath / fname).delete()
    assert not fpath.exists()
    ub.grabdata(url, fpath=fpath, hasher=None, verbose=10)
    assert fpath.exists()
    # Even without the hasher, if the size of the data changes at all
    # we should be able to detect and correct it.
    orig_text = fpath.read_text()
    fpath.write_text('corrupted')
    ub.grabdata(url, fpath=fpath, hasher=None, verbose=10)
    assert fpath.read_text() == orig_text


@pytest.mark.timeout(TIMEOUT)
def test_grabdata_url_only():
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
def test_grabdata_with_fpath():
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


def test_grabdata_value_error():
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
def test_download_bad_url():
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
def test_grabdata_fname_only():
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
def test_grabdata_dpath_only():
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
def test_grabdata_fpath_and_dpath():
    # url = 'http://i.imgur.com/rqwaDag.png'
    # if not ub.argflag('--network'):
    #     pytest.skip('not running network tests')
    url = _demo_url()

    with pytest.raises(ValueError):
        ub.grabdata(url, fpath='foo', dpath='bar')


# @pytest.mark.timeout(TIMEOUT)
def test_grabdata_hash_typo():
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
                url, hash_prefix='e09c80c42fda5-typo-5f9d992e59ca6b3307d',
                hasher='md5', verbose=verbose,
                appname='ubelt/tests/test_download')
        assert fpath.exists()
        real_hash = ub.hash_file(fpath, hasher='md5')
        real_hash

        print('[STEP2] Fixing the typo recomputes the hash, but does not redownload the file')
        got_fpath = ub.grabdata(url,
                                hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
                                hasher='md5', verbose=verbose,
                                appname='ubelt/tests/test_download')
        assert ub.Path(got_fpath).resolve() == fpath.resolve()
        assert fpath.exists()

        # If we delete the .hash file we will simply recompute
        stamp_fpath.delete()
        print('[STEP3] Deleting the hash file recomputes the hash')
        got_fpath = ub.grabdata(url, fpath=fpath,
                                hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
                                hasher='md5', verbose=verbose)
        assert stamp_fpath.exists()


def test_deprecated_grabdata_args():
    # with pytest.warns(DeprecationWarning):
    with pytest.raises(RuntimeError):
        import hashlib
        url = _demo_url()
        # dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
        # fname = basename(url)
        # fpath = join(dpath, fname)
        got_fpath = ub.grabdata(
            url, hash_prefix='e09c80c42fda55f9d992e59ca6b3307d',
            hasher=hashlib.md5())
        got_fpath


def _devcheck_progres_download_bar():
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
        def write(self, msg):
            time.sleep(0.0005)
            ...

    file = DummyIO()
    url = urls[0]
    dl_file = ub.download(url, fpath=file, progkw=dict(desc='dling'))
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

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is not None:
            self = cls._instance
        else:
            self = cls()
            cls._instance = self
        return self

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()
        self.__class__.instance = None

    def __nice__(self):
        return '{} - {}'.format(self.root_url, self.proc.returncode)

    def __init__(self):
        import requests
        import time
        import sys
        import ubelt as ub
        import socket
        from contextlib import closing
        def find_free_port():
            """
            References:
                .. [SO1365265] https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
            """
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(('', 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return s.getsockname()[1]

        # Find an open port
        port = find_free_port()
        print('port = {!r}'.format(port))

        dpath = ub.Path.appdir('ubelt/tests/test_download/simple_server').ensuredir()

        if sys.platform.startswith('win32'):
            pyexe = 'python'
        else:
            pyexe = sys.executable

        server_cmd = [
            pyexe, '-m', 'http.server', str(port)
        ]
        info = ub.cmd(server_cmd, detach=True, cwd=dpath)
        proc = info['proc']
        self.proc = proc
        self.dpath = dpath
        self.root_url = 'http://localhost:{}'.format(port)

        if IS_PYPY and IS_WIN32:
            # not sure why
            import pytest
            pytest.skip('not sure why download tests are failing on pypy win32')
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
            raise AssertionError('Simple server did not start {}'.format(poll_ret))

        self.urls = []
        self.write_file()

    def write_file(self, filebytes=10, num_files=1):
        fnames = ['file_{}_{}.txt'.format(filebytes, i) for i in range(num_files)]
        for fname in fnames:
            # data = ''.join(random.choices(string.ascii_letters, k=filebytes))
            data = 'a' * filebytes
            fpath = join(self.dpath, fname)
            with open(fpath, 'w') as file:
                file.write(data)
        urls = ['{}/{}'.format(self.root_url, fname) for fname in fnames]
        self.urls.extend(urls)
        return urls


def test_local_download():
    server = SingletonTestServer.instance()
    url = server.write_file(filebytes=int(10 * 2 ** 20))[0]
    # also test with a timeout for lazy coverage
    ub.download(url, timeout=3000)


def _demo_url(num_bytes=None):
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
def test_download_with_progkw():
    """
    Test that progkw is properly passed through to ub.download
    """
    url = _demo_url(128 * 10)
    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)
    with ub.CaptureStdout() as cap:
        ub.download(url, fpath=fpath, progkw={'verbose': 3, 'freq': 1, 'adjust': False, 'time_thresh': 0}, chunksize=128)
    assert len(cap.text.split('\n')) > 10


@pytest.mark.timeout(TIMEOUT)
def test_download_with_filesize():
    """
    Test that progkw is properly passed through to ub.download
    """
    url = _demo_url(128 * 10)
    dpath = ub.Path.appdir('ubelt/tests/test_download').ensuredir()
    fname = basename(url)
    fpath = join(dpath, fname)
    with ub.CaptureStdout() as cap:
        ub.download(url, filesize=11, fpath=fpath, progkw={'verbose': 3, 'freq': 1, 'adjust': False, 'time_thresh': 0}, chunksize=128)
    import re
    assert re.search(r'\d\d\d\d\.\d\d%', cap.text), 'should report over 100%'


def make_stat_dict(stat_obj):
    # Convert the stat tuple to a dict we can manipulate
    # and ignore access time
    ignore_keys = {'st_atime', 'st_atime_ns'}
    return {
        k: getattr(stat_obj, k) for k in dir(stat_obj)
        if k.startswith('st_') and k not in ignore_keys}


def test_grabdata():
    import ubelt as ub
    import json
    import time
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
        fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, redo=True,
                            hasher='sha512')
        stat2 = make_stat_dict(ub.Path(fpath).stat())
        # Note: the precision of mtime is too low for this test work reliably
        # https://apenwarr.ca/log/20181113
        if stat2 != stat1:
            break
        print('... Sometimes the redownload happens so fast we need to '
              'wait to notice the file is actually different')
        time.sleep(sleep_time)
    else:
        raise AssertionError(
            'the file stat should be modified, we waited over {}s.'.format(
                sleep_time * num_tries))
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
    assert not ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1, hasher='sha512')
    assert ub.hash_file(fpath, base='hex', hasher='sha512').startswith(prefix1)


def test_grabdata_same_fpath_different_url():
    url1 = _demo_url(128 * 11)
    url2 = _demo_url(128 * 12)
    url3 = _demo_url(128 * 13)

    fname = 'foobar'
    fpath1 = ub.grabdata(url1, fname=fname, hash_prefix='b7fa848cd088ae842a89ef', hasher='sha512', verbose=100)
    stat1 = make_stat_dict(ub.Path(fpath1).stat())

    # Should requesting a new url, even with the same fpath, cause redownload?
    fpath2 = ub.grabdata(url2, fname=fname, hash_prefix=None, hasher='sha512', verbose=100)
    stat2 = make_stat_dict(ub.Path(fpath2).stat())

    fpath3 = ub.grabdata(url3, fname=fname, hash_prefix=None, hasher='sha512', verbose=100)
    stat3 = make_stat_dict(ub.Path(fpath3).stat())

    assert stat1 != stat2, 'the stats will change because we did not specify a hash prefix'
    assert stat2 == stat3, 'we may change this behavior in the future'

    fpath3 = ub.grabdata(url2, fname=fname, hash_prefix='43f92597d7eb08b57c88b6', hasher='sha512', verbose=100)
    stat3 = make_stat_dict(ub.Path(fpath3).stat())
    assert stat1 != stat3, 'if we do specify a new hash, we should get a new download'
    assert url1 != url2, 'urls should be different'
    assert ub.allsame([fpath1, fpath2, fpath3]), 'all fpaths should be the same'


def test_grabdata_delete_hash_stamp():
    import ubelt as ub
    fname = 'foo3.bar'
    url = _demo_url(128 * 12)
    prefix1 = '43f92597d7eb08b57c88b636'
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
    stamp_fpath = ub.Path(fpath + '.stamp_sha512.json')
    ub.delete(stamp_fpath)
    fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)


def test_download_with_io():
    import ubelt as ub
    import io
    url = _demo_url(128 * 3)
    file = io.BytesIO()
    fpath = ub.download(url, file)
    assert fpath is file
    file.seek(0)
    data = file.read()
    hashstr = ub.hash_data(data, hasher='sha1')
    assert hashstr.startswith('45a5c851bf12d1')


def test_download_with_sha1_hasher():
    import ubelt as ub
    url = _demo_url(128 * 4)
    ub.download(url, hasher='sha1', hash_prefix='164557facb7392')


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    SingletonTestServer.instance()


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    SingletonTestServer.instance().close()


if __name__ == '__main__':
    """
    CommandLine:
        pytest ubelt/tests/test_download.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
