# -*- coding: utf-8 -*-
"""
Functions for reading and writing files on disk.

`writeto` and `readfrom` wrap `open().write()` and `open().read()` and primarily
serve to indicate that the type of data being written and read is unicode text.

`delete` wraps `os.unlink` and `shutil.rmtree` and does not throw an error if
the file or directory does not exist. It also contains workarounds for win32
issues with `shutil`.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import six
import sys
import os
from os.path import exists, join  # NOQA


__all__ = [
    'readfrom', 'writeto', 'touch', 'delete',
]


def writeto(fpath, to_write, aslines=False, verbose=None):
    r"""
    Writes (utf8) text to a file.

    Args:
        fpath (PathLike): file path
        to_write (str): text to write (must be unicode text)
        aslines (bool): if True to_write is assumed to be a list of lines
        verbose (bool): verbosity flag

    CommandLine:
        python -m ubelt.util_io writeto --verbose

    Example:
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

    with open(fpath, 'wb') as file:
        if aslines:
            to_write = map(_ensure_bytes , to_write)
            file.writelines(to_write)
        else:
            # convert to bytes for writing
            bytes = _ensure_bytes(to_write)
            file.write(bytes)


if six.PY2:  # nocover
    def _ensure_bytes(text):
        if isinstance(text, unicode):  # NOQA
            text = text.encode('utf8')
        return text
else:
    def _ensure_bytes(text):
        """ ensures text is in a suitable format for writing """
        return text.encode('utf8')


def readfrom(fpath, aslines=False, errors='replace', verbose=None):
    """
    Reads (utf8) text from a file.

    Args:
        fpath (PathLike): file path
        aslines (bool): if True returns list of lines
        verbose (bool): verbosity flag

    Returns:
        str: text from fpath (this is unicode)
    """
    if verbose:
        print('Reading text file: %r ' % (fpath,))
    if not exists(fpath):
        raise IOError('File %r does not exist' % (fpath,))
    with open(fpath, 'rb') as file:
        if aslines:
            text = [line.decode('utf8', errors=errors)
                    for line in file.readlines()]
            if sys.platform.startswith('win32'):  # nocover
                # fix line endings on windows
                text = [
                    line[:-2] + '\n' if line.endswith('\r\n') else line
                    for line in text
                ]
        else:
            text = file.read().decode('utf8', errors=errors)
    return text


def touch(fpath, mode=0o666, dir_fd=None, verbose=0, **kwargs):
    """
    change file timestamps

    Works like the touch unix utility

    Args:
        fpath (PathLike): name of the file
        mode (int): file permissions (python3 and unix only)
        dir_fd (file): optional directory file descriptor. If specified, fpath
            is interpreted as relative to this descriptor (python 3 only).
        verbose (int): verbosity
        **kwargs : extra args passed to `os.utime` (python 3 only).

    Returns:
        PathLike: path to the file

    References:
        https://stackoverflow.com/questions/1158076/implement-touch-using-python

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> fpath = join(dpath, 'touch_file')
        >>> assert not exists(fpath)
        >>> ub.touch(fpath)
        >>> assert exists(fpath)
        >>> os.unlink(fpath)
    """
    if verbose:
        print('Touching file {}'.format(fpath))
    if six.PY2:  # nocover
        with open(fpath, 'a'):
            os.utime(fpath, None)
    else:
        flags = os.O_CREAT | os.O_APPEND
        with os.fdopen(os.open(fpath, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
            os.utime(f.fileno() if os.utime in os.supports_fd else fpath,
                     dir_fd=None if os.supports_fd else dir_fd, **kwargs)
    return fpath


def delete(path, verbose=False):
    """
    Removes a file or recursively removes a directory.
    If a path does not exist, then this is does nothing.

    Args:
        path (PathLike): file or directory to remove
        verbose (bool): if True prints what is being done

    SeeAlso:
        send2trash - A cross-platform Python package for sending files
            to the trash instead of irreversibly deleting them.
            https://github.com/hsoft/send2trash

    Doctest:
        >>> import ubelt as ub
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

    Doctest:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'delete_test2')
        >>> dpath1 = ub.ensuredir(join(dpath, 'dir'))
        >>> fpath1 = ub.touch(join(dpath1, 'to_remove.txt'))
        >>> assert exists(fpath1)
        >>> ub.delete(dpath)
        >>> assert not exists(fpath1)
    """
    if not os.path.exists(path):
        # if the file does exists and is not a broken link
        if os.path.islink(path):
            if verbose:  # nocover
                print('Deleting broken link="{}"'.format(path))
            os.unlink(path)
        elif os.path.isdir(path):  # nocover
            # Only on windows will a file be a directory and not exist
            if verbose:
                print('Deleting broken directory link="{}"'.format(path))
            os.rmdir(path)
        elif os.path.isfile(path):  # nocover
            # This is a windows only case
            if verbose:
                print('Deleting broken file link="{}"'.format(path))
            os.unlink(path)
        else:
            if verbose:  # nocover
                print('Not deleting non-existant path="{}"'.format(path))
    else:
        if os.path.islink(path):
            if verbose:  # nocover
                print('Deleting symbolic link="{}"'.format(path))
            os.unlink(path)
        elif os.path.isfile(path):
            if verbose:  # nocover
                print('Deleting file="{}"'.format(path))
            os.unlink(path)
        elif os.path.isdir(path):
            if verbose:  # nocover
                print('Deleting directory="{}"'.format(path))
            if sys.platform.startswith('win32'):  # nocover
                # Workaround bug that prevents shutil from working if
                # the directory contains junctions
                from ubelt import _win32_links
                _win32_links._win32_rmtree(path, verbose=verbose)
            else:
                import shutil
                shutil.rmtree(path)
