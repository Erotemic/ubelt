r"""
Cross-platform logic for dealing with symlinks. Basic functionality should work
on all operating systems including everyone's favorite pathological OS (note
that there is an additional helper file for this case), but there are some
corner cases depending on your version. Recent versions of Windows tend to
work, but there certain system settings that cause issues. Any POSIX system
works without difficulty.

Example:
    >>> import ubelt as ub
    >>> from os.path import normpath, join
    >>> dpath = ub.Path.appdir('ubelt', normpath('demo/symlink')).ensuredir()
    >>> real_path = dpath / 'real_file.txt'
    >>> link_path = dpath / 'link_file.txt'
    >>> ub.touch(real_path)
    >>> result = ub.symlink(real_path, link_path, overwrite=True, verbose=3)
    >>> parts = result.split(os.path.sep)
    >>> print(parts[-1])
    link_file.txt
"""
from os.path import exists, islink, join, normpath
import os
import sys
import warnings
from ubelt import util_io
from ubelt import util_platform

__all__ = ['symlink']

if sys.platform.startswith('win32'):  # nocover
    from ubelt import _win32_links
else:
    _win32_links = None


def symlink(real_path, link_path, overwrite=False, verbose=0):
    """
    Create a link ``link_path`` that mirrors ``real_path``.

    This function attempts to create a real symlink, but will fall back on a
    hard link or junction if symlinks are not supported.

    Args:
        real_path (str | PathLike): path to real file or directory

        link_path (str | PathLike): path to desired location for symlink

        overwrite (bool, default=False): overwrite existing symlinks.
            This will not overwrite real files on systems with proper symlinks.
            However, on older versions of windows junctions are
            indistinguishable from real files, so we cannot make this
            guarantee.

        verbose (int, default=0): verbosity level

    Returns:
        str | PathLike: link path

    Note:
        On systems that do not contain support for symlinks (e.g. some versions
        / configurations of Windows), this function will fall back on hard
        links or junctions [WikiNTFSLinks]_, [WikiHardLink]_. The differences
        between the two are explained in [WikiSymLink]_.

        If symlinks are not available, then ``link_path`` and ``real_path``
        must exist on the same filesystem.  Given that, this function always
        works in the sense that (1) ``link_path`` will mirror the data from
        ``real_path``, (2) updates to one will effect the other, and (3) no
        extra space will be used.

        More details can be found in :mod:`ubelt._win32_links`. On systems that
        support symlinks (e.g. Linux), none of the above applies.

    References:
        .. [WikiSymLink] https://en.wikipedia.org/wiki/Symbolic_link
        .. [WikiHardLink] https://en.wikipedia.org/wiki/Hard_link
        .. [WikiNTFSLinks] https://en.wikipedia.org/wiki/NTFS_links

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('ubelt', 'test_symlink0').delete().ensuredir()
        >>> real_path = (dpath / 'real_file.txt')
        >>> link_path = (dpath / 'link_file.txt')
        >>> real_path.write_text('foo')
        >>> result = ub.symlink(real_path, link_path)
        >>> assert ub.Path(result).read_text() == 'foo'
        >>> dpath.delete()  # clenaup

    Example:
        >>> import ubelt as ub
        >>> from ubelt.util_links import _dirstats
        >>> dpath = ub.Path.appdir('ubelt', 'test_symlink1').delete().ensuredir()
        >>> _dirstats(dpath)
        >>> real_dpath = (dpath / 'real_dpath').ensuredir()
        >>> link_dpath = real_dpath.augment(stem='link_dpath')
        >>> real_path = (dpath / 'afile.txt')
        >>> link_path = (dpath / 'afile.txt')
        >>> real_path.write_text('foo')
        >>> result = ub.symlink(real_dpath, link_dpath)
        >>> assert link_path.read_text() == 'foo', 'read should be same'
        >>> link_path.write_text('bar')
        >>> _dirstats(dpath)
        >>> assert link_path.read_text() == 'bar', 'very bad bar'
        >>> assert real_path.read_text() == 'bar', 'changing link did not change real'
        >>> real_path.write_text('baz')
        >>> _dirstats(dpath)
        >>> assert real_path.read_text() == 'baz', 'very bad baz'
        >>> assert link_path.read_text() == 'baz', 'changing real did not change link'
        >>> ub.delete(link_dpath, verbose=1)
        >>> _dirstats(dpath)
        >>> assert not link_dpath.exists(), 'link should not exist'
        >>> assert real_path.exists(), 'real path should exist'
        >>> _dirstats(dpath)
        >>> ub.delete(dpath, verbose=1)
        >>> _dirstats(dpath)
        >>> assert not real_path.exists()

    Example:
        >>> # Specifying bad paths should error.
        >>> import ubelt as ub
        >>> import pytest
        >>> dpath = ub.Path.appdir('ubelt', 'test_symlink2').ensuredir()
        >>> real_path = dpath / 'real_file.txt'
        >>> link_path = dpath / 'link_file.txt'
        >>> real_path.write_text('foo')
        >>> with pytest.raises(ValueError, match='link_path .* cannot be empty'):
        >>>     ub.symlink(real_path, '')
        >>> with pytest.raises(ValueError, match='real_path .* cannot be empty'):
        >>>     ub.symlink('', link_path)
    """
    if not real_path:
        raise ValueError('The real_path argument cannot be empty')
    if not link_path:
        raise ValueError('The link_path argument cannot be empty')

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
        print('Symlink: {link} -> {path}'.format(path=path, link=link))
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
    # Note:
    # https://docs.python.org/3/library/os.html#os.readlink
    # os.readlink was changed on win32 in version 3.8: Added support for
    # directory junctions, and changed to return the substitution path (which
    # typically includes \\?\ prefix) rather than the optional “print name”
    # field that was previously returned.

    if _win32_links:  # nocover
        if _win32_links._win32_is_junction(link):
            return _win32_links._win32_read_junction(link)
    try:
        path = os.readlink(link)
        if util_platform.WIN32:  # nocover
            junction_prefix = '\\\\?\\'
            if path.startswith(junction_prefix):
                path = path[len(junction_prefix):]
        return path
    except Exception:  # nocover
        # On modern operating systems, we should never get here. (I think)
        if exists(link):
            warnings.warn('Reading symlinks seems to not be supported')
        raise


def _can_symlink(verbose=0):  # nocover
    """
    Return true if we have permission to create real symlinks.
    This check always returns True on non-win32 systems.
    If this check returns false, then we still may be able to use junctions.

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

    The column prefixes stand for:
    (E - exists), (L - islink), (F - isfile), (D - isdir), (J - isjunction)
    """
    from ubelt import util_colors
    if dpath is None:
        dpath = os.getcwd()
    print('+--------------')
    print('Listing for dpath={}'.format(dpath))
    print('E L F D J - path')
    print('+--------------')
    if not os.path.exists(dpath):
        print('... does not exist')
    else:
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
                # A file (or a hard link, they're indistinguishable with 1 query)
                path = util_colors.color_text(path, 'white')
            elif ELFDJ == [1, 0, 0, 1, 1]:
                # A directory junction
                path = util_colors.color_text(path, 'yellow')
            elif ELFDJ == [1, 1, 1, 0, 0]:
                # A file link
                path = util_colors.color_text(path, 'brightgreen')
            elif ELFDJ == [1, 1, 0, 1, 0]:
                # A directory link
                path = util_colors.color_text(path, 'brightcyan')
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
                # A file junction? That's not good.
                # I guess this is a windows 7 thing?
                path = util_colors.color_text(path, 'red')
            elif ELFDJ == [1, 1, 0, 0, 0]:
                # Windows? Why? What does this mean!?
                # A directory link that can't be resolved?
                path = util_colors.color_text(path, 'red')
            elif ELFDJ == [0, 0, 0, 0, 0]:
                # Windows? AGAIN? HOW DO YOU LIST FILES THAT DONT EXIST?
                # I get it, they are probably broken junctions, but common
                # That should probably be 00011 not 00000
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
                    resolved = _win32_links._win32_read_junction(full_path)
                    line += ' => ' + resolved
            print(line)
    print('+--------------')
