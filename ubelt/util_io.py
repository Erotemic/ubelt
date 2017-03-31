# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import six
from os.path import exists


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
        >>> import os
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
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
        >>> import os
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
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
            if six.PY2 and isinstance(to_write, unicode):
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
        else:
            text = file_.read().decode('utf8', errors=errors)
    return text


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_io
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
