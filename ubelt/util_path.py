# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import splitext, split, join


def augpath(path, suffix='', prefix=''):
    """
    Augments a filename with a suffix and/or a prefix while maintaining the
    extension.

    Args:
        path (str):
        suffix (str): augment filename before extension

    Returns:
        str: newpath

    Example:
        >>> import ubelt as ub
        >>> path = 'foo.bar'
        >>> suffix = '_suff'
        >>> prefix = 'pref_'
        >>> newpath = ub.augpath(path, suffix, prefix)
        >>> print('newpath = %s' % (newpath,))
        newpath = pref_foo_suff.bar
    """
    # Breakup path
    dpath, fname = split(path)
    fname_noext, orig_ext = splitext(fname)
    # Augment and recombine into new path
    new_fname = ''.join((prefix, fname_noext, suffix, orig_ext))
    newpath = join(dpath, new_fname)
    return newpath


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_path
        python -m ubelt.util_path all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
