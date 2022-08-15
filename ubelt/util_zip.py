"""
Abstractions for working with zipfiles and archives

This may be renamed to util_archive in the future.

The :func:`ubelt.split_archive` works with paths that reference a file inside
of an archive (e.g. a zipfile). It splits it into two parts, the full path to
the archive and then the path to the file inside of the archive. By convention
these are separated with either a pathsep or a colon.

The :func:`ubelt.zopen` works to open a file that lives inside of an archive
without the user needing to worry about extracting it first. When possible it
will read it directly from the archive, but in some cases it may extract it to
a temporary directory first.
"""
import io
import os
from os.path import exists, join
from ubelt.util_mixins import NiceRepr

__all__ = ['zopen', 'split_archive']


def split_archive(fpath, ext='.zip'):
    """
    If fpath specifies a file inside a zipfile, it breaks it into two parts the
    path to the zipfile and the internal path in the zipfile.

    Example:
        >>> split_archive('/a/b/foo.txt')
        >>> split_archive('/a/b/foo.zip/bar.txt')
        >>> split_archive('/a/b/foo.zip/baz/biz.zip/bar.py')
        >>> split_archive('archive.zip')
        >>> import ubelt as ub
        >>> split_archive(ub.Path('/a/b/foo.zip/baz/biz.zip/bar.py'))
        >>> split_archive('/a/b/foo.zip/baz.pt/bar.zip/bar.zip', '.pt')

    TODO:
        Fix got/want for win32

        (None, None)
        ('/a/b/foo.zip', 'bar.txt')
        ('/a/b/foo.zip/baz/biz.zip', 'bar.py')
        ('archive.zip', None)
        ('/a/b/foo.zip/baz/biz.zip', 'bar.py')
        ('/a/b/foo.zip/baz.pt', 'bar.zip/bar.zip')
    """
    import re
    fpath = os.fspath(fpath)
    # fpath = os.fspath(fpath)
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
    else:  # nocover
        raise AssertionError('impossible state')
    return archivepath, internal


class zopen(NiceRepr):
    """
    An abstraction of the normal :func:`open` function that can also handle
    reading data directly inside of zipfiles.

    This is a file-object like interface [FileObj] --- i.e. it supports the
    read and write methods to an underlying resource.

    Can open a file normally or open a file within a zip file (readonly).
    Tries to read from memory only, but will extract to a tempfile if necessary.

    Just treat the zipfile like a directory,
    e.g. /path/to/myzip.zip/compressed/path.txt OR?
    e.g. /path/to/myzip.zip:compressed/path.txt

    References:
        .. [FileObj] https://docs.python.org/3/glossary.html#term-file-object

    TODO:
        - [ ] Fast way to open a base zipfile, query what is inside, and
              then choose a file to further zopen (and passing along the same
              open zipfile reference maybe?).
        - [ ] Write mode in some restricted setting?

    Args:
        fpath (str | PathLike):
            path to a file, or a special path that denotes both a
            path to a zipfile and a path to a archived file inside of
            the zipfile.

        mode (str):
            Currently only "r" - readonly mode is supported

        seekable (bool):
            If True, attempts to force "seekability" of the underlying
            file-object, for compressed files this will first extract
            the file to a temporary location on disk.  If False, any underlying
            compressed file will be opened directly which may result in the
            object being non-seekable.

        ext (str):
            The extension of the zipfile. Modify this is a non-standard
            extension is used (e.g. for torch packages).

    Example:
        >>> from ubelt.util_zip import *  # NOQA
        >>> import pickle
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('ubelt/tests/util_zip').ensuredir()
        >>> dpath = ub.Path(dpath)
        >>> data_fpath = dpath / 'test.pkl'
        >>> data = {'demo': 'data'}
        >>> with open(str(data_fpath), 'wb') as file:
        >>>     pickle.dump(data, file)
        >>> # Write data
        >>> import zipfile
        >>> zip_fpath = dpath / 'test_zip.archive'
        >>> stl_w_zfile = zipfile.ZipFile(os.fspath(zip_fpath), mode='w')
        >>> stl_w_zfile.write(os.fspath(data_fpath), os.fspath(data_fpath.relative_to(dpath)))
        >>> stl_w_zfile.close()
        >>> stl_r_zfile = zipfile.ZipFile(os.fspath(zip_fpath), mode='r')
        >>> stl_r_zfile.namelist()
        >>> stl_r_zfile.close()
        >>> # Test zopen
        >>> self = zopen(zip_fpath / 'test.pkl', mode='rb', ext='.archive')
        >>> print(self._split_archive())
        >>> print(self.namelist())
        >>> self.close()
        >>> self = zopen(zip_fpath / 'test.pkl', mode='rb', ext='.archive')
        >>> recon1 = pickle.loads(self.read())
        >>> self.close()
        >>> self = zopen(zip_fpath / 'test.pkl', mode='rb', ext='.archive')
        >>> recon2 = pickle.load(self)
        >>> self.close()
        >>> assert recon1 == recon2
        >>> assert recon1 is not recon2

    Example:
        >>> # Test we can load json data from a zipfile
        >>> from ubelt.util_zip import *  # NOQA
        >>> import ubelt as ub
        >>> import json
        >>> import zipfile
        >>> dpath = ub.Path.appdir('ubelt/tests/util_zip').ensuredir()
        >>> infopath = join(dpath, 'info.json')
        >>> ub.writeto(infopath, '{"x": "1"}')
        >>> zippath = join(dpath, 'infozip.zip')
        >>> internal = 'folder/info.json'
        >>> with zipfile.ZipFile(zippath, 'w') as myzip:
        >>>     myzip.write(infopath, internal)
        >>> fpath = zippath + '/' + internal
        >>> # Test context manager
        >>> with zopen(fpath, 'r') as self:
        >>>     info2 = json.load(self)
        >>>     assert info2['x'] == '1'
        >>> # Test outside of context manager
        >>> self = zopen(fpath, 'r')
        >>> print(self._split_archive())
        >>> info2 = json.load(self)
        >>> assert info2['x'] == '1'
        >>> # Test nice repr (with zfile)
        >>> print('self = {!r}'.format(self))
        >>> self.close()

    Example:
        >>> # Coverage tests --- move to unit-test
        >>> from ubelt.util_zip import *  # NOQA
        >>> import ubelt as ub
        >>> import json
        >>> import zipfile
        >>> dpath = ub.Path.appdir('ubelt/tests/util_zip').ensuredir()
        >>> textpath = join(dpath, 'seekable_test.txt')
        >>> text = chr(10).join(['line{}'.format(i) for i in range(10)])
        >>> ub.writeto(textpath, text)
        >>> zippath = join(dpath, 'seekable_test.zip')
        >>> internal = 'folder/seekable_test.txt'
        >>> with zipfile.ZipFile(zippath, 'w') as myzip:
        >>>     myzip.write(textpath, internal)
        >>> ub.delete(textpath)
        >>> fpath = zippath + '/' + internal
        >>> # Test seekable
        >>> self_seekable = zopen(fpath, 'r', seekable=True)
        >>> assert self_seekable.seekable()
        >>> self_seekable.seek(8)
        >>> assert self_seekable.readline() == 'ne1' + chr(10)
        >>> assert self_seekable.readline() == 'line2' + chr(10)
        >>> self_seekable.seek(8)
        >>> assert self_seekable.readline() == 'ne1' + chr(10)
        >>> assert self_seekable.readline() == 'line2' + chr(10)
        >>> # Test non-seekable?
        >>> # Sometimes non-seekable files are still seekable
        >>> maybe_seekable = zopen(fpath, 'r', seekable=False)
        >>> if maybe_seekable.seekable():
        >>>     maybe_seekable.seek(8)
        >>>     assert maybe_seekable.readline() == 'ne1' + chr(10)
        >>>     assert maybe_seekable.readline() == 'line2' + chr(10)
        >>>     maybe_seekable.seek(8)
        >>>     assert maybe_seekable.readline() == 'ne1' + chr(10)
        >>>     assert maybe_seekable.readline() == 'line2' + chr(10)


    Example:
        >>> # More coverage tests --- move to unit-test
        >>> from ubelt.util_zip import *  # NOQA
        >>> import ubelt as ub
        >>> import pytest
        >>> dpath = ub.Path.appdir('ubelt/tests/util_zip').ensuredir()
        >>> with pytest.raises(OSError):
        >>>     self = zopen('', 'r')
        >>> # Test open non-zip exsting file
        >>> existing_fpath = join(dpath, 'exists.json')
        >>> ub.writeto(existing_fpath, '{"x": "1"}')
        >>> self = zopen(existing_fpath, 'r')
        >>> assert self.read() == '{"x": "1"}'
        >>> # Test dir
        >>> dir(self)
        >>> # Test nice
        >>> print(self)
        >>> print('self = {!r}'.format(self))
        >>> self.close()
        >>> # Test open non-zip non-existing file
        >>> nonexisting_fpath = join(dpath, 'does-not-exist.txt')
        >>> ub.delete(nonexisting_fpath)
        >>> with pytest.raises(OSError):
        >>>     self = zopen(nonexisting_fpath, 'r')
        >>> with pytest.raises(NotImplementedError):
        >>>     self = zopen(nonexisting_fpath, 'w')
        >>> # Test nice-repr
        >>> self = zopen(existing_fpath, 'r')
        >>> print('self = {!r}'.format(self))
        >>> # pathological
        >>> self = zopen(existing_fpath, 'r')
        >>> self._handle = None
        >>> dir(self)
    """
    def __init__(self, fpath, mode='r', seekable=False, ext='.zip'):
        self.fpath = fpath
        self.ext = ext
        self.name = fpath
        self.mode = mode
        self._seekable = seekable
        self._zfpath = None  # points to the base zipfile (if appropriate)
        self._temp_dpath = None  # for temporary extraction
        self._zfile_read = None  # underlying opened zipfile object
        # The _handle pointer should be a file-like object that this zopen
        # object impersonate, by forwarding most every getattr call to it.
        self._handle = None
        self._open()

    @property
    def zfile(self):
        """
        Access the underlying archive file
        """
        if self._zfile_read is None:
            import zipfile
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
            return 'handle={}, mode={}'.format(str(self._handle), self.mode)
        else:
            return 'handle={} in zipfpath={}, mode={}'.format(self._handle, self._zfpath, self.mode)

    def __getattr__(self, key):
        # Expose attributes of wrapped handle
        if hasattr(self._handle, key):
            assert self._handle is not self
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
        if self._handle is not None:
            if not getattr(self, 'closed', True):
                closemethod = getattr(self, 'close', None)
                if closemethod is not None:  # nocover
                    closemethod()
                closemethod = None
        self._handle = None
        if self._temp_dpath and exists(self._temp_dpath):
            # os.unlink(self._temp_dpath)
            import ubelt as ub
            ub.delete(self._temp_dpath)

    def __del__(self):
        self._cleanup()

    def _split_archive(self):
        archivefile, internal = split_archive(self.fpath, self.ext)
        return archivefile, internal

    def _open(self):
        """
        This logic sets the "_handle" to the appropriate backend object
        such that zopen can behave like a standard IO object.

        In read-only mode:
            * If fpath is a normal file, _handle is the standard `open` object
            * If fpath is a seekable zipfile, _handle is an IOWrapper pointing
                to the internal data
            * If fpath is a non-seekable zipfile, the data is extracted behind
                the scenes and a standard `open` object to the extracted file
                is given.

        In write mode:
            * NotImpelemented
        """
        if 'r' not in self.mode:
            raise NotImplementedError('Only read mode is supported for now')
        _handle = None
        fpath = os.fspath(self.fpath)
        if exists(fpath):
            _handle = open(fpath, self.mode)
        elif self.ext + '/' in fpath or self.ext + os.path.sep in fpath:
            archivefile, internal = self._split_archive()
            myzip = self.zfile
            if self._seekable:
                import tempfile
                # If we need data to be seekable, then we must extract it to a
                # temporary file first.
                self._temp_dpath = tempfile.mkdtemp(prefix='zopen_')
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
                    # FIXME: does not always work. handle seems to be closed
                    # too soon in the case util.zopen(module.__file__).read()
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
