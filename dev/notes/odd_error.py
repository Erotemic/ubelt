3.10 on ubuntu-latest, arch=auto with tests
failed 2 hours ago in 30s


Run # Find the path to the wheel
Processing ./wheelhouse/ubelt-1.2.1-py3-none-any.whl
Collecting coverage
  Downloading coverage-6.4.2-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (212 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 212.3/212.3 kB 10.6 MB/s eta 0:00:00
Collecting pytest
  Downloading pytest-7.1.2-py3-none-any.whl (297 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 297.0/297.0 kB 31.0 MB/s eta 0:00:00
Collecting pytest-cov
  Downloading pytest_cov-3.0.0-py3-none-any.whl (20 kB)
Collecting codecov
  Downloading codecov-2.1.12-py2.py3-none-any.whl (16 kB)
Collecting requests
  Downloading requests-2.28.1-py3-none-any.whl (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.8/62.8 kB 24.0 MB/s eta 0:00:00
Collecting xdoctest
  Downloading xdoctest-1.0.1-py3-none-any.whl (130 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 130.5/130.5 kB 43.5 MB/s eta 0:00:00
Collecting pytest-timeout
  Downloading pytest_timeout-2.1.0-py3-none-any.whl (12 kB)
Collecting idna<4,>=2.5
  Downloading idna-3.3-py3-none-any.whl (61 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 61.2/61.2 kB 25.4 MB/s eta 0:00:00
Collecting certifi>=2017.4.17
  Downloading certifi-2022.6.15-py3-none-any.whl (160 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 160.2/160.2 kB 54.2 MB/s eta 0:00:00
Collecting charset-normalizer<3,>=2
  Downloading charset_normalizer-2.1.0-py3-none-any.whl (39 kB)
Collecting urllib3<1.27,>=1.21.1
  Downloading urllib3-1.26.11-py2.py3-none-any.whl (139 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 139.9/139.9 kB 49.1 MB/s eta 0:00:00
Collecting py>=1.8.2
  Downloading py-1.11.0-py2.py3-none-any.whl (98 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 98.7/98.7 kB 39.4 MB/s eta 0:00:00
Collecting iniconfig
  Downloading iniconfig-1.1.1-py2.py3-none-any.whl (5.0 kB)
Requirement already satisfied: packaging in /opt/hostedtoolcache/Python/3.10.5/x64/lib/python3.10/site-packages (from pytest->ubelt==1.2.1) (21.3)
Collecting attrs>=19.2.0
  Downloading attrs-22.1.0-py2.py3-none-any.whl (58 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 58.8/58.8 kB 25.7 MB/s eta 0:00:00
Requirement already satisfied: tomli>=1.0.0 in /opt/hostedtoolcache/Python/3.10.5/x64/lib/python3.10/site-packages (from pytest->ubelt==1.2.1) (2.0.1)
Collecting pluggy<2.0,>=0.12
  Downloading pluggy-1.0.0-py2.py3-none-any.whl (13 kB)
Collecting six
  Downloading six-1.16.0-py2.py3-none-any.whl (11 kB)
Requirement already satisfied: pyparsing!=3.0.5,>=2.0.2 in /opt/hostedtoolcache/Python/3.10.5/x64/lib/python3.10/site-packages (from packaging->pytest->ubelt==1.2.1) (3.0.9)
Installing collected packages: iniconfig, urllib3, ubelt, six, py, pluggy, idna, coverage, charset-normalizer, certifi, attrs, xdoctest, requests, pytest, pytest-timeout, pytest-cov, codecov
Successfully installed attrs-22.1.0 certifi-2022.6.15 charset-normalizer-2.1.0 codecov-2.1.12 coverage-6.4.2 idna-3.3 iniconfig-1.1.1 pluggy-1.0.0 py-1.11.0 pytest-7.1.2 pytest-cov-3.0.0 pytest-timeout-2.1.0 requests-2.28.1 six-1.16.0 ubelt-1.2.1 urllib3-1.26.11 xdoctest-1.0.1
MOD_DPATH = /opt/hostedtoolcache/Python/3.10.5/x64/lib/python3.10/site-packages/ubelt
============================= test session starts ==============================
platform linux -- Python 3.10.5, pytest-7.1.2, pluggy-1.0.0
rootdir: /home/runner/work/ubelt/ubelt, configfile: pyproject.toml
plugins: timeout-2.1.0, cov-3.0.0, xdoctest-1.0.1
collected 517 items



=================================== FAILURES ===================================
________________________________ test_grabdata _________________________________

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
        stat0 = ub.Path(fpath).stat()
        stamp_fpath = ub.Path(fpath).augment(tail='.stamp_sha512.json')
        assert json.loads(stamp_fpath.read_text())['hash'][0].startswith(prefix1)
        #
        print("2. Rerun and check that the download doesn't happen again")
        fpath = ub.grabdata(url, fname=fname, hash_prefix=prefix1)
        stat1 = ub.Path(fpath).stat()
>       assert stat0 == stat1, 'the file should not be modified'
E       AssertionError: the file should not be modified
E       assert os.stat_resul...me=1659755459) == os.stat_resul...me=1659755459)
E         At index 7 diff: 1659755459 != 1659755460
E         Full diff:
E         - os.stat_result(st_mode=33152, st_ino=62343, st_dev=2049, st_nlink=1, st_uid=1001, st_gid=121, st_size=1408, st_atime=1659755460, st_mtime=1659755459, st_ctime=1659755459)
E         ?                                                                                                                              ^^
E         + os.stat_result(st_mode=33152, st_ino=62343, st_dev=2049, st_nlink=1, st_uid=1001, st_gid=121, st_size=1408, st_atime=1659755459, st_mtime=1659755459, st_ctime=1659755459)
E         ?                                                                                                                              ^^

../tests/test_download.py:573: AssertionError
----------------------------- Captured stdout call -----------------------------
1. Download the file once
[cacher] ... foo2.bar.stamp cache miss
[cacher] stamp expired no_cert
Downloading url='http://localhost:43031/file_1408_0.txt' to fpath='/home/runner/.cache/ubelt/foo2.bar'

    0/1408... rate=0 Hz, eta=?, total=0:00:00
 1408/1408... rate=16487312.50 Hz, eta=0:00:00, total=0:00:00
[cacher] ... foo2.bar.stamp cache save
2. Rerun and check that the download doesn't happen again
=============================== warnings summary ===============================
tests/test_color.py::test_global_color_disable
tests/test_links.py::test_rel_dir_link
tests/test_links.py::test_rel_file_link
tests/test_links.py::test_delete_symlinks
tests/test_links.py::test_broken_link
tests/test_links.py::test_cant_overwrite_file_with_symlink
tests/test_links.py::test_overwrite_symlink
  /home/runner/work/ubelt/ubelt/ubelt/util_colors.py:171: UserWarning: pygments is not installed, text will not be colored
    warnings.warn('pygments is not installed, text will not be colored')

tests/test_color.py::test_global_color_disable
  /home/runner/work/ubelt/ubelt/ubelt/util_colors.py:98: UserWarning: pygments is not installed, code will not be highlighted
    warnings.warn('pygments is not installed, code will not be highlighted')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

---------- coverage: platform linux, python 3.10.5-final-0 -----------
Name                                                           Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------------------
