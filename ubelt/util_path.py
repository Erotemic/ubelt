# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import splitext, split, join
import os


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
        python -m ubelt.util_path
        python -m ubelt.util_path all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
