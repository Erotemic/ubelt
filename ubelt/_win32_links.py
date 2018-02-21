# -*- coding: utf-8 -*-
"""
For dealing with symlinks, junctions, and hard-links on windows.

References:
    https://stackoverflow.com/questions/18883892/batch-file-windows-cmd-exe-test-if-a-directory-is-a-link-symlink

    https://stackoverflow.com/questions/21561850/python-test-for-junction-point-target
    http://timgolden.me.uk/python/win32_how_do_i/see_if_two_files_are_the_same_file.html
    https://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa365006(v=vs.85).aspx
    https://superuser.com/a/902082/215232
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import warnings
from os.path import exists
from os.path import join
from ubelt import util_io
from ubelt import util_path
import sys

if sys.platform.startswith('win32'):
    import win32file
    import jaraco.windows.filesystem as jwfs
    # import jaraco.windows.filesystem

# import ctypes
# import ctypes.wintypes as wintypes
# from ctypes import Structure
# from ctypes import byref
# FILE_ATTRIBUTE_DIRECTORY = 16  # (0x10)
# FILE_ATTRIBUTE_REPARSE_POINT = 1024  # (0x400)
# MAX_PATH = 260

# GetLastError = ctypes.windll.kernel32.GetLastError


# class FILETIME(Structure):
#     _fields_ = [("dwLowDateTime", wintypes.DWORD),
#                 ("dwHighDateTime", wintypes.DWORD)]


# class WIN32_FIND_DATAW(Structure):
#     _fields_ = [("dwFileAttributes", wintypes.DWORD),
#                 ("ftCreationTime", FILETIME),
#                 ("ftLastAccessTime", FILETIME),
#                 ("ftLastWriteTime", FILETIME),
#                 ("nFileSizeHigh", wintypes.DWORD),
#                 ("nFileSizeLow", wintypes.DWORD),
#                 ("dwReserved0", wintypes.DWORD),
#                 ("dwReserved1", wintypes.DWORD),
#                 ("cFileName", wintypes.WCHAR * MAX_PATH),
#                 ("cAlternateFileName", wintypes.WCHAR * 20)]


__win32_can_symlink__ = None


def _win32_can_symlink(verbose=0, force=0, testing=0):  # nocover
    """
    CommandLine:
        python -m ubelt._win32_links _win32_can_symlink

    Example:
        >>> # xdoc: +REQUIRES(WIN32)
        >>> import ubelt as ub
        >>> _win32_can_symlink(verbose=1, force=1, testing=1)
    """
    global __win32_can_symlink__
    if verbose:
        print('__win32_can_symlink__ = {!r}'.format(__win32_can_symlink__))
    if __win32_can_symlink__ is not None and not force:
        return __win32_can_symlink__

    from ubelt import util_platform
    tempdir = util_platform.ensure_app_cache_dir('ubelt', '_win32_can_symlink')
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

    # Add broken variants of the links for testing purposes
    # Its ugly, but so is all this windows code.
    if testing:
        broken_dpath = join(tempdir, 'broken_dpath')
        broken_fpath = join(tempdir, 'broken_fpath.txt')
        # Create files that we will delete after we link to them
        util_path.ensuredir(broken_dpath)
        util_io.touch(broken_fpath)

    try:
        _win32_symlink(dpath, dlink)
        if testing:
            _win32_symlink(broken_dpath, join(tempdir, 'broken_dlink'))
        can_symlink_directories = os.path.islink(dlink)
    except OSError:
        can_symlink_directories = False
    if verbose:
        print('can_symlink_directories = {!r}'.format(can_symlink_directories))

    try:
        _win32_symlink(fpath, flink)
        if testing:
            _win32_symlink(broken_fpath, join(tempdir, 'broken_flink'))
        can_symlink_files = os.path.islink(flink)
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
        djunc = _win32_junction(dpath, join(tempdir, 'djunc'))
        fjunc = _win32_junction(fpath, join(tempdir, 'fjunc.txt'))
        if testing:
            _win32_junction(broken_dpath, join(tempdir, 'broken_djunc'))
            _win32_junction(broken_fpath, join(tempdir, 'broken_fjunc.txt'))
        assert _win32_is_junction(djunc)
        assert _win32_is_hardlinked(fpath, fjunc)
    except Exception:
        warnings.warn('We cannot create junctions either!')
        raise

    if testing:
        # break the links
        util_io.delete(broken_dpath)
        util_io.delete(broken_fpath)

        if verbose:
            import ubelt as ub
            test_links = ub.import_module_from_path(
                os.path.dirname(__file__) + '/tests/test_links.py')
            test_links.dirstats(tempdir)

    try:
        # Cleanup the test directory
        util_io.delete(tempdir)
    except Exception:
        print('ERROR IN DELETE')
        import ubelt as ub
        test_links = ub.import_module_from_path(
            os.path.dirname(__file__) + '/tests/test_links.py')
        test_links.dirstats(tempdir)
        raise

    can_symlink = can_symlink_directories and can_symlink_files
    __win32_can_symlink__ = can_symlink
    if not can_symlink:
        warnings.warn('Cannot make real symlink. Falling back to junction')

    if verbose:
        print('can_symlink = {!r}'.format(can_symlink))
        print('__win32_can_symlink__ = {!r}'.format(__win32_can_symlink__))
    return can_symlink


def _win32_symlink2(path, link, allow_fallback=True, verbose=0):  # nocover
    """
    Perform a real symbolic link if possible. However, on most versions of
    windows you need special privledges to create a real symlink. Therefore, we
    try to create a symlink, but if that fails we fallback to using a junction.

    AFAIK, the main difference between symlinks and junctions are that symlinks
    can reference relative or absolute paths, where as junctions always
    reference absolute paths. Not 100% on this though. Windows is weird.

    Note that junctions will not register as links via `islink`, but I
    believe real symlinks will.
    """
    if _win32_can_symlink():
        return _win32_symlink(path, link, verbose)
    else:
        return _win32_junction(path, link, verbose)


def _win32_symlink(path, link, verbose=0):  # nocover
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
    if os.path.isdir(path):
        # directory symbolic link
        command = 'mklink /D "{}" "{}"'.format(link, path)
        if verbose:
            print('... as directory symlink')
    else:
        # file symbolic link
        command = 'mklink "{}" "{}"'.format(link, path)
        if verbose:
            print('... as file symlink')
    info = util_cmd.cmd(command, shell=True)
    if info['ret'] != 0:
        from ubelt import util_format
        permission_msg = 'You do not have sufficient privledges'
        if permission_msg not in info['err']:
            print('Failed command:')
            print(info['command'])
            print(util_format.repr2(info, nl=1))
        raise OSError(str(info))
    return link


def _win32_junction(path, link, verbose=0):
    """
    On older (pre 10) versions of windows we need admin privledges to make
    symlinks, however junctions seem to work.

    For paths we do a junction (softlink) and for files we use a hard link

    TODO:

    CommandLine:
        python -m ubelt._win32_links _win32_junction

    Example:
        >>> # xdoc: +REQUIRES(WIN32)
        >>> import ubelt as ub
        >>> root = ub.ensure_app_cache_dir('ubelt', 'win32_junction')
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
    from ubelt import util_cmd
    # if platform.release() == '7':
    if os.path.isdir(path):
        # try using a junction (soft link)
        command = 'mklink /J "{}" "{}"'.format(link, path)
        if verbose:
            print('... as soft link')
    else:
        # try using a hard link
        command = 'mklink /H "{}" "{}"'.format(link, path)
        if verbose:
            print('... as hard link')
    info = util_cmd.cmd(command, shell=True)
    if info['ret'] != 0:
        from ubelt import util_format
        print('Failed command:')
        print(info['command'])
        print(util_format.repr2(info, nl=1))
        raise OSError(str(info))
    return link


def _win32_is_junction(path):
    """
    Determines if a path is a win32 junction

    CommandLine:
        python -m ubelt._win32_links _win32_is_junction

    Example:
        >>> # xdoc: +REQUIRES(WIN32)
        >>> import ubelt as ub
        >>> root = ub.ensure_app_cache_dir('ubelt', 'win32_junction')
        >>> ub.delete(root)
        >>> ub.ensuredir(root)
        >>> dpath = join(root, 'dpath')
        >>> djunc = join(root, 'djunc')
        >>> ub.ensuredir(dpath)
        >>> _win32_junction(dpath, djunc)
        >>> assert _win32_is_junction(djunc) is True
        >>> assert _win32_is_junction(dpath) is False
        >>> assert _win32_is_junction('notafile') is False
    """
    if not exists(path):
        if os.path.isdir(path):
            if not os.path.islink(path):
                return True
        return False
    return jwfs.is_reparse_point(path) and not os.path.islink(path)
    # try:
    #     return _win32_read_junction(path) is not None
    # except (ValueError, OSError):
    #     return False
    # data = WIN32_FIND_DATAW()
    # h = ctypes.windll.kernel32.FindFirstFileW(path, byref(data))
    # if (data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY and data.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT):
    #     return True
    # ctypes.windll.kernel32.FindClose(h)
    # return False


def _win32_read_junction(path):
    """
    Returns the location that the junction points, raises ValueError if path is
    not a junction.

    CommandLine:
        python -m ubelt._win32_links _win32_read_junction

    Example:
        >>> # xdoc: +REQUIRES(WIN32)
        >>> import ubelt as ub
        >>> root = ub.ensure_app_cache_dir('ubelt', 'win32_junction')
        >>> ub.delete(root)
        >>> ub.ensuredir(root)
        >>> dpath = join(root, 'dpath')
        >>> djunc = join(root, 'djunc')
        >>> ub.ensuredir(dpath)
        >>> _win32_junction(dpath, djunc)
        >>> path = djunc
        >>> pointed = _win32_read_junction(path)
        >>> print('pointed = {!r}'.format(pointed))
    """
    if not jwfs.is_reparse_point(path):
        raise ValueError('not a junction')
    # if not exists(path):
    #     if six.PY2:
    #         raise OSError('Cannot find path={}'.format(path))
    #     else:
    #         raise FileNotFoundError('Cannot find path={}'.format(path))
    # target_name = os.path.basename(path)
    # for type_or_size, name, pointed in _win32_dir(path, '*'):
    #     if type_or_size == '<JUNCTION>' and name == target_name:
    #         return pointed
    # raise ValueError('not a junction')

    handle = jwfs.api.CreateFile(
            path,
            0,
            0,
            None,
            jwfs.api.OPEN_EXISTING,
            jwfs.api.FILE_FLAG_OPEN_REPARSE_POINT | jwfs.api.FILE_FLAG_BACKUP_SEMANTICS,
            None,
    )

    if handle == jwfs.api.INVALID_HANDLE_VALUE:
        raise WindowsError()

    res = jwfs.reparse.DeviceIoControl(
            handle, jwfs.api.FSCTL_GET_REPARSE_POINT, None, 10240)

    bytes = jwfs.create_string_buffer(res)
    p_rdb = jwfs.cast(bytes, jwfs.POINTER(jwfs.api.REPARSE_DATA_BUFFER))
    rdb = p_rdb.contents

    if rdb.tag not in [2684354563, jwfs.api.IO_REPARSE_TAG_SYMLINK]:
        raise RuntimeError(
                "Expected <2684354563 or 2684354572>, but got %d" % rdb.tag)

    jwfs.handle_nonzero_success(jwfs.api.CloseHandle(handle))
    return rdb.get_substitute_name()[2:]


def _win32_rmtree(path, verbose=0):
    """
    rmtree for win32 that treats junctions like directory symlinks.
    The junction removal portion may not be safe on race conditions.

    There is a known issue that prevents shutil.rmtree from
    deleting directories with junctions.
    https://bugs.python.org/issue31226
    """
    # def _rmjunctions(root):
    #     subdirs = []
    #     for type_or_size, name, pointed in _win32_dir(root):
    #         if type_or_size == '<DIR>':
    #             subdirs.append(name)
    #         elif type_or_size == '<JUNCTION>':
    #             # remove any junctions as we encounter them
    #             # os.unlink(join(root, name))
    #             os.rmdir(join(root, name))
    #     # recurse in all real directories
    #     for name in subdirs:
    #         _rmjunctions(join(root, name))

    def _rmjunctions(root):
        subdirs = []
        for name in os.listdir(root):
            current = join(root, name)
            if os.path.isdir(current):
                if _win32_is_junction(current):
                    # remove any junctions as we encounter them
                    os.rmdir(current)
                elif not os.path.islink(current):
                    subdirs.append(current)
        # recurse in all real directories
        for subdir in subdirs:
            _rmjunctions(subdir)

    if _win32_is_junction(path):
        if verbose:
            print('Deleting <JUNCTION> directory="{}"'.format(path))
        os.rmdir(path)
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


def _win32_is_hardlinked(fpath1, fpath2):  # nocover
    """
    Test if two hard links point to the same location
    """
    # TODO: can we use jw for this?
    def get_read_handle(filename):
        if os.path.isdir(filename):
            dwFlagsAndAttributes = win32file.FILE_FLAG_BACKUP_SEMANTICS
        else:
            dwFlagsAndAttributes = 0
        return win32file.CreateFile(filename, win32file.GENERIC_READ,
                                    win32file.FILE_SHARE_READ, None,
                                    win32file.OPEN_EXISTING,
                                    dwFlagsAndAttributes, None)

    def get_unique_id(hFile):
        (attributes,
         created_at, accessed_at, written_at,
         volume,
         file_hi, file_lo,
         n_links,
         index_hi, index_lo) = win32file.GetFileInformationByHandle(hFile)
        return volume, index_hi, index_lo

    try:
        hFile1 = get_read_handle(fpath1)
        hFile2 = get_read_handle(fpath2)
        are_equal = (get_unique_id(hFile1) == get_unique_id(hFile2))
    except Exception:
        raise
    finally:
        hFile1.Close()
        hFile2.Close()
    return are_equal

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt._win32_links
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
