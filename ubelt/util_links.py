r"""
Cross-platform logic for dealing with symlinks. Basic functionality should work
on all operating systems including everyone's favorite pathological OS (note
that there is an additional helper file for this case), but there are some
corner cases depending on your version. Recent versions of Windows tend to
work, but there certain system settings that cause issues. Obviously, any POSIX
system work without difficulty.

CommandLine:
    xdoctest -m ubelt.util_links __doc__:0

Example:
    >>> import ubelt as ub
    >>> from os.path import normpath, join
    >>> dpath = ub.ensure_app_cache_dir('ubelt', normpath('demo/symlink'))
    >>> real_path = join(dpath, 'real_file.txt')
    >>> link_path = join(dpath, 'link_file.txt')
    >>> ub.touch(real_path)
    >>> result = ub.symlink(real_path, link_path, overwrite=True, verbose=3)
    >>> parts = result.split(os.path.sep)
    >>> print(parts[-1])
    link_file.txt
"""
from os.path import exists
from os.path import islink
from os.path import join
from os.path import normpath
from os.path import os
import six
import sys
import warnings
from ubelt import util_io
from ubelt import util_platform

if sys.platform.startswith('win32'):  # nocover
    from ubelt import _win32_links
else:
    _win32_links = None

if six.PY2:
    FileExistsError = IOError


def symlink(real_path, link_path, overwrite=False, verbose=0):
    """
    Create a symbolic link.

    This will work on linux or windows, however windows does have some corner
    cases. For more details see notes in `ubelt._win32_links`.

    Args:
        path (PathLike): path to real file or directory
        link_path (PathLike): path to desired location for symlink
        overwrite (bool): overwrite existing symlinks.
            This will not overwrite real files on systems with proper symlinks.
            However, on older versions of windows junctions are
            indistinguishable from real files, so we cannot make this
            guarantee.  (default = False)
        verbose (int):  verbosity level (default=0)

    Returns:
        PathLike: link path

    CommandLine:
        python -m ubelt.util_links symlink:0

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'test_symlink0')
        >>> real_path = join(dpath, 'real_file.txt')
        >>> link_path = join(dpath, 'link_file.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_path, link_path)
        >>> assert ub.readfrom(result) == 'foo'
        >>> [ub.delete(p) for p in [real_path, link_path]]

    Example:
        >>> import ubelt as ub
        >>> from os.path import dirname
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'test_symlink1')
        >>> ub.delete(dpath)
        >>> ub.ensuredir(dpath)
        >>> _dirstats(dpath)
        >>> real_dpath = ub.ensuredir((dpath, 'real_dpath'))
        >>> link_dpath = ub.augpath(real_dpath, base='link_dpath')
        >>> real_path = join(dpath, 'afile.txt')
        >>> link_path = join(dpath, 'afile.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_dpath, link_dpath)
        >>> assert ub.readfrom(link_path) == 'foo', 'read should be same'
        >>> ub.writeto(link_path, 'bar')
        >>> _dirstats(dpath)
        >>> assert ub.readfrom(link_path) == 'bar', 'very bad bar'
        >>> assert ub.readfrom(real_path) == 'bar', 'changing link did not change real'
        >>> ub.writeto(real_path, 'baz')
        >>> _dirstats(dpath)
        >>> assert ub.readfrom(real_path) == 'baz', 'very bad baz'
        >>> assert ub.readfrom(link_path) == 'baz', 'changing real did not change link'
        >>> ub.delete(link_dpath, verbose=1)
        >>> _dirstats(dpath)
        >>> assert not exists(link_dpath), 'link should not exist'
        >>> assert exists(real_path), 'real path should exist'
        >>> _dirstats(dpath)
        >>> ub.delete(dpath, verbose=1)
        >>> _dirstats(dpath)
        >>> assert not exists(real_path)
    """
    path = normpath(real_path)
    link = normpath(link_path)

    if not os.path.isabs(path):
        # if path is not absolute it must be specified relative to link
        if _can_symlink():
            path = os.path.relpath(path, os.path.dirname(link))
        else:  # nocover
            # On windows, we need to use absolute paths
            path = os.path.abspath(path)

    if verbose:
        print('Symlink: {path} -> {link}'.format(path=path, link=link))
    if islink(link):
        if verbose:
            print('... already exists')
        pointed = _readlink(link)
        if pointed == path:
            if verbose > 1:
                print('... and points to the right place')
            return link
        if verbose > 1:
            if not exists(link):
                print('... but it is broken and points somewhere else: {}'.format(pointed))
            else:
                print('... but it points somewhere else: {}'.format(pointed))
        if overwrite:
            util_io.delete(link, verbose=verbose > 1)
    elif exists(link):
        if _win32_links is None:
            if verbose:
                print('... already exists, but its a file. This will error.')
            raise FileExistsError(
                'cannot overwrite a physical path: "{}"'.format(path))
        else:  # nocover
            if verbose:
                print('... already exists, and is either a file or hard link. '
                      'Assuming it is a hard link. '
                      'On non-win32 systems this would error.')

    if _win32_links is None:
        os.symlink(path, link)
    else:  # nocover
        _win32_links._symlink(path, link, overwrite=overwrite, verbose=verbose)

    return link


def _readlink(link):
    if _win32_links:  # nocover
        if _win32_links._win32_is_junction(link):
            return _win32_links._win32_read_junction(link)
    try:
        return os.readlink(link)
    except Exception:  # nocover
        # On modern operating systems, we should never get here. (I think)
        warnings.warn('Reading symlinks seems to not be supported')
        raise


def _can_symlink(verbose=0):  # nocover
    """
    Return true if we have permission to create real symlinks.
    This check always returns True on non-win32 systems.
    If this check returns false, then we still may be able to use junctions.

    CommandLine:
        python -m ubelt.util_platform _can_symlink

    Example:
        >>> # Script
        >>> print(_can_symlink(verbose=1))
    """
    if _win32_links is not None:
        return _win32_links._win32_can_symlink(verbose)
    else:
        return True


def _dirstats(dpath=None):  # nocover
    """
    Testing helper for printing directory information
    (mostly for investigating windows weirdness)

    CommandLine:
        python -m ubelt.util_links _dirstats
    """
    from ubelt import util_colors
    if dpath is None:
        dpath = os.getcwd()
    print('===============')
    print('Listing for dpath={}'.format(dpath))
    print('E L F D J - path')
    print('--------------')
    if not os.path.exists(dpath):
        print('... does not exist')
        return
    paths = sorted(os.listdir(dpath))
    for path in paths:
        full_path = join(dpath, path)
        E = os.path.exists(full_path)
        L = os.path.islink(full_path)
        F = os.path.isfile(full_path)
        D = os.path.isdir(full_path)
        J = util_platform.WIN32 and _win32_links._win32_is_junction(full_path)
        ELFDJ = [E, L, F, D, J]
        if   ELFDJ == [1, 0, 0, 1, 0]:
            # A directory
            path = util_colors.color_text(path, 'green')
        elif ELFDJ == [1, 0, 1, 0, 0]:
            # A file (or a hard link they are indistinguishable with one query)
            path = util_colors.color_text(path, 'white')
        elif ELFDJ == [1, 0, 0, 1, 1]:
            # A directory junction
            path = util_colors.color_text(path, 'yellow')
        elif ELFDJ == [1, 1, 1, 0, 0]:
            # A file link
            path = util_colors.color_text(path, 'turquoise')
        elif ELFDJ == [1, 1, 0, 1, 0]:
            # A directory link
            path = util_colors.color_text(path, 'teal')
        elif ELFDJ == [0, 1, 0, 0, 0]:
            # A broken file link
            path = util_colors.color_text(path, 'red')
        elif ELFDJ == [0, 1, 0, 1, 0]:
            # A broken directory link
            path = util_colors.color_text(path, 'darkred')
        elif ELFDJ == [0, 0, 0, 1, 1]:
            # A broken directory junction
            path = util_colors.color_text(path, 'purple')
        elif ELFDJ == [1, 0, 1, 0, 1]:
            # A file junction? Thats not good.
            # I guess this is a windows 7 thing?
            path = util_colors.color_text(path, 'red')
        elif ELFDJ == [1, 1, 0, 0, 0]:
            # Windows? Why? What does this mean!?
            # A directory link that cant be resolved?
            path = util_colors.color_text(path, 'red')
        else:
            print('dpath = {!r}'.format(dpath))
            print('path = {!r}'.format(path))
            raise AssertionError(str(ELFDJ) + str(path))
        line = '{E:d} {L:d} {F:d} {D:d} {J:d} - {path}'.format(**locals())
        if os.path.islink(full_path):
            line += ' -> ' + os.readlink(full_path)
        elif _win32_links is not None:
            if _win32_links._win32_is_junction(full_path):
                line += ' => ' + _win32_links._win32_read_junction(full_path)
        print(line)
