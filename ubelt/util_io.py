# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import six
from os.path import exists


def write_to(fpath, to_write, aslines=False, mode='w', verbose=None):
    """
    Writes text to a file. Automatically encodes text as utf8.

    Args:
        fpath (str): file path
        to_write (str): text to write (must be unicode text)
        aslines (bool): if True to_write is assumed to be a list of lines
        verbose (bool): verbosity flag
        mode (unicode): (default = u'w')
        n (int):  (default = 2)

    CommandLine:
        python -m ubelt.util_io write_to

    Example:
        >>> from ubelt.util_io import *  # NOQA
        >>> import ubelt as ub
        >>> fpath = ub.unixjoin(ub.get_app_resource_dir('ubelt'), 'testwrite.txt')
        >>> ub.delete(fpath)
        >>> to_write = 'utf-8 symbols Δ, Й, ק, م, ๗, あ, 叶, 葉, and 말.'
        >>> aslines = False
        >>> verbose = True
        >>> onlyifdiff = False
        >>> mode = u'w'
        >>> n = 2
        >>> write_to(fpath, to_write, aslines, verbose, onlyifdiff, mode, n)
        >>> read_ = ub.read_from(fpath)
        >>> print('read_    = ' + read_)
        >>> print('to_write = ' + to_write)
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
                to_write = to_write.encode('utf8')
            file_.write(to_write)


def read_from(fpath, aslines=False, errors='replace', verbose=None):
    """
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
