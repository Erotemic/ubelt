# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import io
import re
import tempfile
import zipfile
from os.path import exists, join
from ubelt.util_mixins import NiceRepr


def split_archive(fpath, ext='.zip'):
    """
    If fpath specifies a file inside a zipfile, it breaks it into two parts the
    path to the zipfile and the internal path in the zipfile.

    Example:
        >>> split_archive('/a/b/foo.txt')
        (None, None)
        >>> split_archive('/a/b/foo.zip/bar.txt')
        ('/a/b/foo.zip', 'bar.txt')
        >>> split_archive('/a/b/foo.zip/baz/bar.txt')
        >>> split_archive('/a/b/foo.zip/baz/biz.zip/bar.txt')
        >>> split_archive('/a/b/foo.zip/baz/biz.zip/bar.py')
        >>> # xdoctest: +REQUIRES(module:pathlib)
        >>> import pathlib
        >>> split_archive(pathlib.Path('/a/b/foo.zip/baz/biz.zip/bar.py'))
        >>> split_archive('/a/b/foo.zip')
        >>> split_archive('/a/b/foo.zip/baz.zip/bar.zip')
        >>> split_archive('/a/b/foo.zip/baz.pt/bar.zip/bar.zip', '.pt')
        ('/a/b/foo.zip/baz.pt', 'bar.zip/bar.zip')

    TODO:
        should this work for the case where there is nothing after the zip?
    """
    fpath = os.fspath(fpath)
    pat = '({}[{}/:])'.format(re.escape(ext), re.escape(os.path.sep))
    # pat = r'(\'' + ext + '[' + re.escape(os.path.sep) + '/:])'
    parts = re.split(pat, fpath, flags=re.IGNORECASE)
    if len(parts) > 2:
        archivepath = ''.join(parts[:-1])[:-1]
        internal = parts[-1]
    elif len(parts) == 1:
        archivepath = parts[0]
        if not archivepath.endswith(ext):
            archivepath = None
        internal = None
    else:
        archivepath = None
        internal = None
    return archivepath, internal


class zopen(NiceRepr):
    """
    Can open a file normally or open a file within a zip file (readonly). Tries
    to read from memory only, but will extract to a tempfile if necessary.

    Just treat the zipfile like a directory,
    e.g. /path/to/myzip.zip/compressed/path.txt OR?
    e.g. /path/to/myzip.zip:compressed/path.txt

    TODO:
        - [ ] Fast way to open a base zipfile, query what is inside, and
              then choose a file to further zopen (and passing along the same
              open zipfile refernce maybe?).

    Example:
        >>> from ubelt.util_zip import *  # NOQA
        >>> import pathlib
        >>> import pickle
        >>> dpath = ub.ensure_app_cache_dir('ubelt/tests/util_zip')
        >>> dpath = pathlib.Path(dpath)
        >>> data_fpath = dpath / 'test.pkl'
        >>> data = {'demo': 'data'}
        >>> with open(data_fpath, 'wb') as file:
        >>>     pickle.dump(data, file)
        >>> # Write data
        >>> import zipfile
        >>> zip_fpath = dpath / 'test_zip.archive'
        >>> stl_w_zfile = zipfile.ZipFile(zip_fpath, mode='w')
        >>> stl_w_zfile.write(data_fpath, data_fpath.relative_to(dpath))
        >>> stl_w_zfile.close()
        >>> stl_r_zfile = zipfile.ZipFile(zip_fpath, mode='r')
        >>> stl_r_zfile.namelist()
        >>> stl_r_zfile.close()
        >>> # Test zopen
        >>> self = zopen(zip_fpath / 'test.pkl', mode='rb', ext='.archive')
        >>> print(self._split_archive())
        >>> print(self.namelist())
        >>> self = zopen(zip_fpath / 'test.pkl', mode='rb', ext='.archive')
        >>> recon1 = pickle.loads(self.read())
        >>> self = zopen(zip_fpath / 'test.pkl', mode='rb', ext='.archive')
        >>> recon2 = pickle.load(self)
        >>> assert recon1 == recon2
        >>> assert recon1 is not recon2

    Example:
        >>> # Test we can load json data from a zipfile
        >>> from ubelt.util_zip import *  # NOQA
        >>> dpath = ub.ensure_app_cache_dir('ubelt/tests/util_zip')
        >>> infopath = join(dpath, 'info.json')
        >>> open(infopath, 'w').write('{"x": "1"}')
        >>> zippath = join(dpath, 'infozip.zip')
        >>> internal = 'folder/info.json'
        >>> with zipfile.ZipFile(zippath, 'w') as myzip:
        >>>     myzip.write(infopath, internal)
        >>> fpath = zippath + '/' + internal
        >>> self = zopen(fpath, 'r')
        >>> print(self._split_archive())
        >>> import json
        >>> info2 = json.load(self)
        >>> assert info2['x'] == '1'
    """
    def __init__(self, fpath, mode='r', seekable=False, ext='.zip'):
        self.fpath = fpath
        self.ext = ext
        self.name = fpath
        self.mode = mode
        self._seekable = seekable
        assert 'r' in self.mode
        self._handle = None
        self._zfpath = None
        self._temp_dpath = None
        self._temp_fpath = None
        self._zfile_read = None
        self._open()

    @property
    def zfile(self):
        if self._zfile_read is None:
            archivefile, internal = self._split_archive()
            myzip = zipfile.ZipFile(archivefile, 'r')
            self._zfile_read = myzip
        return self._zfile_read

    def namelist(self):
        """
        Lists the contents of this zipfile
        """
        myzip = self.zfile
        namelist = myzip.namelist()
        return namelist

    def __nice__(self):
        if self._zfpath is None:
            return str(self._handle) + ' mode=' + self.mode
        else:
            return '{} in zipfile {}, mode={}'.format(self._handle, self._zfpath, self.mode)

    def __getattr__(self, key):
        # Expose attributes of wrapped handle
        if hasattr(self._handle, key):
            return getattr(self._handle, key)
        raise AttributeError(key)

    def __dir__(self):
        # Expose attributes of wrapped handle
        zopen_attributes = {
            'namelist',
            'zfile',
        }
        keyset = set(dir(super(zopen, self)))
        keyset.update(set(self.__dict__.keys()))
        if self._handle is not None:
            keyset.update(set(dir(self._handle)))
        return sorted(keyset | zopen_attributes)

    def _cleanup(self):
        # print('self._cleanup = {!r}'.format(self._cleanup))
        if not getattr(self, 'closed', True):
            getattr(self, 'close', lambda: None)()
        if self._temp_dpath and exists(self._temp_dpath):
            import ubelt as ub
            ub.delete(self._temp_dpath)

    def __del__(self):
        self._cleanup()

    def _split_archive(self):
        archivefile, internal = split_archive(self.fpath, self.ext)
        return archivefile, internal

    @property
    def _temporary_extract(self):
        # If we need data to be seekable, then we must extract it to a
        # temporary file first.
        archivefile, internal = self._split_archive()
        self._temp_dpath = tempfile.mkdtemp()
        myzip = self.zfile
        temp_fpath = join(self._temp_dpath, internal)
        myzip.extract(internal, self._temp_dpath)
        return temp_fpath

    def _open(self):
        _handle = None
        fpath = os.fspath(self.fpath)
        if exists(fpath):
            _handle = open(fpath, self.mode)
        elif self.ext + '/' in fpath or self.ext + os.path.sep in fpath:
            archivefile, internal = self._split_archive()
            myzip = self.zfile
            if self._seekable:
                # If we need data to be seekable, then we must extract it to a
                # temporary file first.
                self._temp_dpath = tempfile.mkdtemp()
                temp_fpath = join(self._temp_dpath, internal)
                myzip.extract(internal, self._temp_dpath)
                _handle = open(temp_fpath, self.mode)
            else:
                # Try to load data directly from the zipfile
                _handle = myzip.open(internal, 'r')
                if self.mode == 'rb':
                    data = _handle.read()
                    _handle = io.BytesIO(data)
                elif self.mode == 'r':
                    # FIXME: doesnt always work. handle seems to be closed too
                    # soon in the case util.zopen(module.__file__).read()
                    _handle = io.TextIOWrapper(_handle)
                else:
                    raise KeyError(self.mode)
                self._zfpath = archivefile
        if _handle is None:
            raise IOError('file {!r} does not exist'.format(fpath))
        self._handle = _handle

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == '__main__':
    import xdoctest
    xdoctest.doctest_module(__file__)
