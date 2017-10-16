# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import six
import sys
import os
from os.path import exists, join  # NOQA


def writeto(fpath, to_write, aslines=False, mode='w', verbose=None):
    r"""
    Writes text to a file. Automatically encodes text as utf8.

    Args:
        fpath (str): file path
        to_write (str): text to write (must be unicode text)
        aslines (bool): if True to_write is assumed to be a list of lines
        verbose (bool): verbosity flag
        mode (unicode): (default = u'w')
        n (int):  (default = 2)

    CommandLine:
        python -m ubelt.util_io writeto --verbose

    Example:
        >>> from ubelt.util_io import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> fpath = dpath + '/' + 'testwrite.txt'
        >>> if exists(fpath):
        >>>     os.remove(fpath)
        >>> to_write = 'utf-8 symbols Δ, Й, ק, م, ๗, あ, 叶, 葉, and 말.'
        >>> writeto(fpath, to_write)
        >>> read_ = ub.readfrom(fpath)
        >>> print('read_    = ' + read_)
        >>> print('to_write = ' + to_write)
        >>> assert read_ == to_write

    Example:
        >>> from ubelt.util_io import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> fpath = dpath + '/' + 'testwrite2.txt'
        >>> if exists(fpath):
        >>>     os.remove(fpath)
        >>> to_write = ['a\n', 'b\n', 'c\n', 'd\n']
        >>> writeto(fpath, to_write, aslines=True)
        >>> read_ = ub.readfrom(fpath, aslines=True)
        >>> print('read_    = {}'.format(read_))
        >>> print('to_write = {}'.format(to_write))
        >>> assert read_ == to_write
    """
    if verbose:
        print('Writing to text file: %r ' % (fpath,))

    with open(fpath, mode) as file_:
        if aslines:
            file_.writelines(to_write)
        else:
            # Ensure python2 writes in bytes
            if six.PY2 and isinstance(to_write, unicode):  # NOQA
                to_write = to_write.encode('utf8')  # nocover
            file_.write(to_write)


def readfrom(fpath, aslines=False, errors='replace', verbose=None):
    r"""
    Reads text from a file. Automatically returns utf8.

    Args:
        fpath (str): file path
        aslines (bool): if True returns list of lines
        verbose (bool): verbosity flag

    Returns:
        str: text from fpath (this is unicode)

    Ignore:
        x = b'''/whaleshark_003_fors\xc3\xb8g.wmv" />\r\n'''
        ub.writeto('foo.txt', x)
        y = ub.readfrom('foo.txt')
        y.encode('utf8') == x
    """
    if verbose:
        print('[util_io] * Reading text file: %r ' % (fpath,))
    if not exists(fpath):
        raise IOError('File %r does not exist' % (fpath,))
    with open(fpath, 'rb') as file_:
        if aslines:
            text = [line.decode('utf8', errors=errors)
                    for line in file_.readlines()]
            if sys.platform.startswith('win32'):  # nocover
                # fix line endings on windows
                text = [
                    line[:-2] + '\n' if line.endswith('\r\n') else line
                    for line in text
                ]
        else:
            text = file_.read().decode('utf8', errors=errors)
    return text


def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    r"""
    change file timestamps

    Works like the touch unix utility

    References:
        https://stackoverflow.com/questions/1158076/implement-touch-using-python

    Example:
        >>> from ubelt.util_io import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> fpath = join(dpath, 'touch_file')
        >>> assert not exists(fpath)
        >>> ub.touch(fpath)
        >>> assert exists(fpath)
        >>> os.unlink(fpath)
    """
    if six.PY2:  # nocover
        with open(fname, 'a'):
            os.utime(fname, None)
    else:
        flags = os.O_CREAT | os.O_APPEND
        with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
            os.utime(f.fileno() if os.utime in os.supports_fd else fname,
                     dir_fd=None if os.supports_fd else dir_fd, **kwargs)


def delete(path, verbose=False):
    """
    Removes a file or recursively removes a directory.
    If a path does not exist, then this is a noop

    Args:
        path (str): file or directory to remove

    Doctest:
        >>> import ubelt as ub
        >>> from os.path import join, exists
        >>> base = ub.ensure_app_cache_dir('ubelt', 'delete_test')
        >>> dpath1 = ub.ensuredir(join(base, 'dir'))
        >>> ub.ensuredir(join(base, 'dir', 'subdir'))
        >>> ub.touch(join(base, 'dir', 'to_remove1.txt'))
        >>> fpath1 = join(base, 'dir', 'subdir', 'to_remove3.txt')
        >>> fpath2 = join(base, 'dir', 'subdir', 'to_remove2.txt')
        >>> ub.touch(fpath1)
        >>> ub.touch(fpath2)
        >>> assert all(map(exists, (dpath1, fpath1, fpath2)))
        >>> ub.delete(fpath1)
        >>> assert all(map(exists, (dpath1, fpath2)))
        >>> assert not exists(fpath1)
        >>> ub.delete(dpath1)
        >>> assert not any(map(exists, (dpath1, fpath1, fpath2)))
    """
    import shutil
    if not os.path.exists(path):
        if verbose:  # nocover
            print('Not deleting non-existant path="{}"'.format(path))
    else:
        if os.path.isfile(path) or os.path.islink(path):
            if verbose:  # nocover
                print('Deleting file="{}"'.format(path))
            os.unlink(path)
        elif os.path.isdir(path):
            if verbose:  # nocover
                print('Deleting directory="{}"'.format(path))
            shutil.rmtree(path)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_io
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
