# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import exists
from os.path import expanduser
from os.path import join
from os.path import normpath
from os.path import islink
from os.path import isdir
import os
import sys
import pipes
import six
import warnings
from ubelt import util_path
from ubelt import util_io

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')
POSIX = 'posix' in sys.builtin_module_names


def platform_resource_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.

    Returns:
        str : path to the resource dir used by the current operating system
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Roaming'
    elif LINUX:  # nocover
        dpath_ = '~/.config'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Application Support'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def platform_cache_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for temporary deletable data.

    Returns:
        str : path to the cache dir used by the current operating system
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Local'
    elif LINUX:  # nocover
        dpath_ = '~/.cache'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Caches'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def get_app_resource_dir(appname, *args):
    r"""
    Returns a writable directory for an application
    This should be used for persistent configuration files.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable resource directory for this application

    SeeAlso:
        ensure_app_resource_dir
    """
    dpath = join(platform_resource_dir(), appname, *args)
    return dpath


def ensure_app_resource_dir(appname, *args):
    """
    Calls `get_app_resource_dir` but ensures the directory exists.

    SeeAlso:
        get_app_resource_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_resource_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def get_app_cache_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory for this application

    SeeAlso:
        ensure_app_cache_dir
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Calls `get_app_cache_dir` but ensures the directory exists.

    SeeAlso:
        get_app_cache_dir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_cache_dir(appname, *args)
    util_path.ensuredir(dpath)
    return dpath


def startfile(fpath, verbose=True):  # nocover
    """
    Uses default program defined by the system to open a file.

    Args:
        fpath (str): a file to open using the program associated with the
            files extension type.
        verbose (int): verbosity

    References:
        http://stackoverflow.com/questions/2692873/quote-posix

    DisableExample:
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> base = ub.ensure_app_cache_dir('ubelt')
        >>> fpath1 = join(base, 'test_open.txt')
        >>> ub.touch(fpath1)
        >>> proc = ub.startfile(fpath1)
    """
    import ubelt as ub
    if verbose:
        print('[ubelt] startfile("{}")'.format(fpath))
    fpath = normpath(fpath)
    if not exists(fpath):
        raise Exception('Cannot start nonexistant file: %r' % fpath)
    if not WIN32:
        fpath = pipes.quote(fpath)
    if LINUX:
        info = ub.cmd(('xdg-open', fpath), detatch=True, verbose=verbose)
    elif DARWIN:
        info = ub.cmd(('open', fpath), detatch=True, verbose=verbose)
    elif WIN32:
        os.startfile(fpath)
        info = None
    else:
        raise RuntimeError('Unknown Platform')
    if info is not None:
        if not info['proc']:
            raise Exception('startfile failed')


def editfile(fpath, verbose=True):  # nocover
    """
    Opens a file or python module in your preferred visual editor.

    Your preferred visual editor is gvim... unless you specify one using the
    VISUAL environment variable. This function is extremely useful in an
    IPython development environment.

    Args:
        fpath (str): a file path or python module / function
        verbose (int): verbosity

    DisableExample:
        >>> # This test interacts with a GUI frontend, not sure how to test.
        >>> import ubelt as ub
        >>> ub.editfile(ub.util_platform.__file__)
        >>> ub.editfile(ub)
        >>> ub.editfile(ub.editfile)
    """
    from six import types
    import ubelt as ub
    if not isinstance(fpath, six.string_types):
        if isinstance(fpath, types.ModuleType):
            fpath = fpath.__file__
        else:
            fpath =  sys.modules[fpath.__module__].__file__
        fpath_py = fpath.replace('.pyc', '.py')
        if exists(fpath_py):
            fpath = fpath_py

    if verbose:
        print('[ubelt] editfile("{}")'.format(fpath))

    editor = os.environ.get('VISUAL', 'gvim')

    if not exists(fpath):
        raise IOError('Cannot start nonexistant file: %r' % fpath)
    ub.cmd([editor, fpath], fpath, detatch=True)


def symlink(real_path, link_path, overwrite=False, verbose=0):
    """
    Create a symbolic link.

    Args:
        path (str): path to real file or directory
        link_path (str): path to desired location for symlink
        overwrite (bool): overwrite existing symlinks.
            This will not overwrite real files on systems with proper symlinks.
            However, on older versions of windows junctions are
            indistinguishable from real files, so we cannot make this
            guarantee.  (default = False)
        verbose (int):  verbosity level (default=0)

    Notes:
        There seems to be a corner case on Python2 and some versions of Windows
        (whatever appveyor is using). However, my windows box works so idk.

    Returns:
        str: link path

    CommandLine:
        python -m ubelt.util_platform symlink:0

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
        >>> test_links = ub.import_module_from_path(dirname(__file__) + '/tests/test_links.py')
        >>> dpath = ub.ensure_app_cache_dir('ubelt', 'test_symlink1')
        >>> ub.delete(dpath)
        >>> ub.ensuredir(dpath)
        >>> test_links.dirstats(dpath)
        >>> real_dpath = ub.ensuredir((dpath, 'real_dpath'))
        >>> link_dpath = ub.augpath(real_dpath, base='link_dpath')
        >>> real_path = join(dpath, 'afile.txt')
        >>> link_path = join(dpath, 'afile.txt')
        >>> [ub.delete(p) for p in [real_path, link_path]]
        >>> ub.writeto(real_path, 'foo')
        >>> result = symlink(real_dpath, link_dpath)
        >>> assert ub.readfrom(link_path) == 'foo', 'read should be same'
        >>> ub.writeto(link_path, 'bar')
        >>> test_links.dirstats(dpath)
        >>> assert ub.readfrom(link_path) == 'bar', 'very bad bar'
        >>> assert ub.readfrom(real_path) == 'bar', 'changing link did not change real'
        >>> ub.writeto(real_path, 'baz')
        >>> test_links.dirstats(dpath)
        >>> assert ub.readfrom(real_path) == 'baz', 'very bad baz'
        >>> assert ub.readfrom(link_path) == 'baz', 'changing real did not change link'
        >>> ub.delete(link_dpath, verbose=1)
        >>> test_links.dirstats(dpath)
        >>> assert not exists(link_dpath), 'link should not exist'
        >>> assert exists(real_path), 'real path should exist'
        >>> test_links.dirstats(dpath)
        >>> ub.delete(dpath, verbose=1)
        >>> test_links.dirstats(dpath)
        >>> assert not exists(real_path)

    TODO:
        Can this be fixed on windows?
        The main issue is that you need admin rights on Windows to symlink.
    """
    path = normpath(real_path)
    link = normpath(link_path)
    if verbose:
        print('Creating symlink: path={} link={}'.format(path, link))
    if islink(link):
        if verbose:
            print('symlink already exists')
        if _readlink(link) == path:
            if verbose > 1:
                print('... and points to the right place')
            return link
        if verbose > 1:
            if not exists(link):
                print('... but it is broken and points somewhere else')
            else:
                print('... but it points somewhere else')
        if overwrite:
            util_io.delete(link, verbose > 1)

    if WIN32:  # nocover
        if exists(link) and not islink(link):
            # On windows a broken link might still exist as a hard link or a
            # junction. Overwrite it if it is a file and we cannot symlink.
            # However, if it is a non-junction directory then do not overwrite
            if verbose:
                print('link location already exists')
            is_junc = _win32_is_junction(link)
            if os.path.isdir(link):
                if is_junc:
                    pointed = _win32_read_junction(link)
                    if path == pointed:
                        if verbose:
                            print('...and is a junction that points to the same place')
                        return link
                    else:
                        if verbose:
                            if not exists(pointed):
                                print('...and is a broken junction that points somewhere else')
                            else:
                                print('...and is a junction that points somewhere else')
                else:
                    if verbose:
                        print('...and is an existing real directory!')
                    raise IOError('Cannot overwrite a real directory')

            elif os.path.isfile(link):
                if os.stat(link).st_ino == os.stat(path).st_ino:
                    if verbose:
                        print('...and is a hard link that points to the same place')
                    return link
                else:
                    if verbose:
                        print('...and is a hard link that points somewhere else')
                    if _can_symlink():
                        raise IOError('Cannot overwrite potentially real file if we can symlink')
            if overwrite:
                if verbose:
                    print('...overwriting')
                util_io.delete(link, verbose > 1)
            else:
                if exists(link):
                    raise IOError('Link already exists')

        _win32_symlink2(path, link)
    else:
        os.symlink(path, link)
    return link


def _readlink(link):
    try:
        return os.readlink(link)
    except Exception:  # nocover
        # On modern operating systems, we should never get here. (I think)
        warnings.warn('Reading symlinks seems to not be supported')
        raise


__win32_can_symlink__ = None


def _can_symlink(verbose=0):  # nocover
    """
    Return true if we have permission to create real symlinks.
    This check always returns True on non-win32 systems.  If this check returns
    false, then we still may be able to use junctions.

    CommandLine:
        python -m ubelt.util_platform _can_symlink

    Example:
        >>> # Script
        >>> print(_can_symlink(verbose=1))
    """
    if WIN32:
        return False
        return _win32_can_symlink(verbose)
    else:
        return True


def _win32_can_symlink(verbose=0):  # nocover
    global __win32_can_symlink__
    if verbose:
        print('__win32_can_symlink__ = {!r}'.format(__win32_can_symlink__))
    if __win32_can_symlink__ is not None:
        return __win32_can_symlink__

    tempdir = ensure_app_cache_dir('ubelt', '_win32_can_symlink')
    # import shutil
    # shutil.rmtree(tempdir)
    util_io.delete(tempdir)
    util_path.ensuredir(tempdir)

    dpath = join(tempdir, 'dpath')
    fpath = join(tempdir, 'fpath.txt')
    dlink = join(tempdir, 'dlink')
    flink = join(tempdir, 'flink.txt')

    util_path.ensuredir(dpath)
    util_io.touch(fpath)

    try:
        _win32_symlink(dpath, dlink)
        can_symlink_directories = True
        # os.path.islink(dlink)
    except OSError:
        can_symlink_directories = False
    if verbose:
        print('can_symlink_directories = {!r}'.format(can_symlink_directories))

    try:
        _win32_symlink(fpath, flink)
        can_symlink_files = True
        # os.path.islink(flink)
    except OSError:
        can_symlink_files = False
    if verbose:
        print('can_symlink_files = {!r}'.format(can_symlink_files))

    assert int(can_symlink_directories) + int(can_symlink_files) != 1, (
        'can do one but not both. Unexpected {} {}'.format(
            can_symlink_directories, can_symlink_files))

    try:
        # test that we can create junctions, even if symlinks are disabled
        _win32_junction(dpath, join(tempdir, 'djunc'))
        _win32_junction(fpath, join(tempdir, 'fjunc.txt'))
    except Exception:
        warnings.warn('We cannot create junctions either!')
        raise

    # Cleanup the test directory
    util_io.delete(tempdir)

    can_symlink = can_symlink_directories and can_symlink_files
    __win32_can_symlink__ = can_symlink
    if not can_symlink:
        warnings.warn('Cannot make real symlink. Falling back to junction')

    if verbose:
        print('can_symlink = {!r}'.format(can_symlink))
        print('__win32_can_symlink__ = {!r}'.format(__win32_can_symlink__))
    return can_symlink


def _win32_junction(path, link):
    """
    On older (pre 10) versions of windows we need admin privledges to make
    symlinks, however junctions seem to work.

    For paths we do a junction (softlink) and for files we use a hard link

    TODO:
        # Need code to test if path is a junction
        # https://stackoverflow.com/questions/18883892/batch-file-windows-cmd-exe-test-if-a-directory-is-a-link-symlink

        # TODO: need to test readlink for junctions
    """
    from ubelt import util_cmd
    # if platform.release() == '7':
    if isdir(path):
        # try using a junction (soft link)
        command = 'mklink /J "{}" "{}"'.format(link, path)
    else:
        # try using a hard link
        command = 'mklink /H "{}" "{}"'.format(link, path)
    info = util_cmd.cmd(command, shell=True)
    if info['ret'] != 0:
        from ubelt import util_format
        print('Failed command:')
        print(info['command'])
        print(util_format.repr2(info, nl=1))
        raise OSError(str(info))


def _win32_is_junction(path):
    """
    Determines if a path is a win32 junction
    """
    if not exists(path):
        return False
    try:
        return _win32_read_junction(path) is not None
    except (ValueError, OSError):
        return False


def _win32_read_junction(path):
    """
    Returns the location that the junction points, raises ValueError if path is
    not a junction.

    CommandLine:
        python -m ubelt.util_platform _win32_read_junction

    Example:
        >>> # DISABLE_DOCTEST
        >>> # xdoc: +REQUIRES(WIN32)
        >>> import ubelt as ub
        >>> root = ub.ensure_app_cache_dir('ubelt', 'win32_symlink')
        >>> ub.delete(root)
        >>> ub.ensuredir(root)
        >>> fpath = join(root, 'fpath.txt')
        >>> dpath = join(root, 'dpath')
        >>> fjunc = join(root, 'fjunc.txt')
        >>> djunc = join(root, 'djunc')
        >>> ub.touch(fpath)
        >>> ub.ensuredir(dpath)
        >>> ub.ensuredir(join(root, 'djunc_fake'))
        >>> ub.ensuredir(join(root, 'djunc_fake with space'))
        >>> ub.touch(join(root, 'djunc_fake with space file'))
        >>> _win32_junction(fpath, fjunc)
        >>> _win32_junction(dpath, djunc)
        >>> # thank god colons are not allowed
        >>> djunc2 = join(root, 'djunc2 [with pathological attrs]')
        >>> _win32_junction(dpath, djunc2)
        >>> _win32_is_junction(djunc)
        >>> ub.writeto(join(djunc, 'afile.txt'), 'foo')
        >>> assert ub.readfrom(join(dpath, 'afile.txt')) == 'foo'
        >>> ub.writeto(fjunc, 'foo')


        # >>> if not _win32_can_symlink(verbose=1):
        # ...     import pytest
        # ...     pytest.skip()

    """
    if not WIN32:
        return False
    if not exists(path):
        if six.PY2:
            raise OSError('Cannot find path={}'.format(path))
        else:
            raise FileNotFoundError('Cannot find path={}'.format(path))
    target_name = os.path.basename(path)
    for type_or_size, name, pointed in _win32_dir(path, '*'):
        if type_or_size == '<JUNCTION>' and name == target_name:
            return pointed
    raise ValueError('not a junction')


def _win32_rmtree(path, verbose=0):
    """
    rmtree for win32 that treats junctions like directory symlinks.
    The junction removal portion may not be safe on race conditions.

    There is a known issue that prevents shutil.rmtree from
    deleting directories with junctions.
    https://bugs.python.org/issue31226
    """
    def _rmjunctions(root):
        subdirs = []
        for type_or_size, name, pointed in _win32_dir(root):
            if type_or_size == '<DIR>':
                subdirs.append(name)
            elif type_or_size == '<JUNCTION>':
                # remove any junctions as we encounter them
                os.unlink(join(root, name))
        # recurse in all real directories
        for name in subdirs:
            _rmjunctions(join(root, name))

    if _win32_is_junction(path):
        if verbose:
            print('Deleting <JUNCTION> directory="{}"'.format(path))
        os.unlink(path)
    else:
        if verbose:
            print('Deleting directory="{}"'.format(path))
        # first remove all junctions
        _rmjunctions(path)
        # now we can rmtree as normal
        import shutil
        shutil.rmtree(path)


def _win32_dir(path, star=''):
    from ubelt import util_cmd
    import re
    wrapper = 'cmd /S /C "{}"'  # the /S will preserve all inner quotes
    command = 'dir /-C "{}"{}'.format(path, star)
    wrapped = wrapper.format(command)
    info = util_cmd.cmd(wrapped, shell=True)
    if info['ret'] != 0:
        from ubelt import util_format
        print('Failed command:')
        print(info['command'])
        print(util_format.repr2(info, nl=1))
        raise OSError(str(info))
    # parse the output of dir to get some info
    # Remove header and footer
    lines = info['out'].split('\n')[5:-3]
    splitter = re.compile('( +)')
    for line in lines:
        parts = splitter.split(line)
        date, sep, time, sep, ampm, sep, type_or_size, sep = parts[:8]
        name = ''.join(parts[8:])
        # if type is a junction then name will also contain the linked loc
        if name == '.' or name == '..':
            continue
        if type_or_size in ['<JUNCTION>', '<SYMLINKD>', '<SYMLINK>']:
            # colons cannot be in path names, so use that to find where
            # the name ends
            pos = name.find(':')
            bpos = name[:pos].rfind('[')
            name = name[:bpos - 1]
            pointed = name[bpos + 1:-1]
            yield type_or_size, name, pointed
        else:
            yield type_or_size, name, None


def _win32_symlink(path, link):  # nocover
    from ubelt import util_cmd
    # # This strategy requires admin permissions
    # import ctypes
    # csl = ctypes.windll.kernel32.CreateSymbolicLinkW
    # csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    # csl.restype = ctypes.c_ubyte
    # flags = 1 if isdir(path) else 0
    # if csl(link, path, flags) == 0:
    #     raise ctypes.WinError('cannot create win32 symlink')

    # This strategy requires development mode to be on I believe.
    if isdir(path):
        # directory symbolic link
        command = 'mklink /D "{}" "{}"'.format(link, path)
    else:
        # file symbolic link
        command = 'mklink "{}" "{}"'.format(link, path)
    info = util_cmd.cmd(command, shell=True)
    if info['ret'] != 0:
        from ubelt import util_format
        permission_msg = 'You do not have sufficient privledges'
        if permission_msg not in info['err']:
            print('Failed command:')
            print(info['command'])
            print(util_format.repr2(info, nl=1))
        raise OSError(str(info))


def _win32_symlink2(path, link, allow_fallback=True):  # nocover
    """
    Perform a real symbolic link if possible. However, on most versions of
    windows you need special privledges to create a real symlink. Therefore, we
    try to create a symlink, but if that fails we fallback to using a junction.

    AFAIK, the main difference between symlinks and junctions are that symlinks
    can reference relative or absolute paths, where as junctions always
    reference absolute paths. Not 100% on this though. Windows is weird.

    Note that junctions will not register as links via `islink`, but I
    believe real symlinks will.

    References:
        https://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365006(v=vs.85).aspx
        https://superuser.com/a/902082/215232
    """
    if _can_symlink():
        _win32_symlink(path, link)
    else:
        _win32_junction(path, link)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
        pytest ubelt/util_platform.py
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
