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

Weird Behavior:
    - [ ] In many cases using the win32 API seems to result in privilege errors
          but using shell commands does not have this problem.
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
    import jaraco.windows.filesystem as jwfs


__win32_can_symlink__ = None


def _win32_can_symlink(verbose=0, force=0, testing=0):
    """
    Args:
        verbose (int, default=0): flag
        force (int, default=0): flag
        testing (int, default=0): flag

    Example:
        >>> # xdoctest: +REQUIRES(WIN32)
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

    if int(can_symlink_directories) + int(can_symlink_files) == 1:
        raise AssertionError(
            'can do one but not both. Unexpected {} {}'.format(
                can_symlink_directories, can_symlink_files))

    try:
        # test that we can create junctions, even if symlinks are disabled
        djunc = _win32_junction(dpath, join(tempdir, 'djunc'))
        fjunc = _win32_junction(fpath, join(tempdir, 'fjunc.txt'))
        if testing:
            _win32_junction(broken_dpath, join(tempdir, 'broken_djunc'))
            _win32_junction(broken_fpath, join(tempdir, 'broken_fjunc.txt'))
        if not _win32_is_junction(djunc):
            raise AssertionError('expected junction')
        if not _win32_is_hardlinked(fpath, fjunc):
            raise AssertionError('expected hardlink')
    except Exception:
        warnings.warn('We cannot create junctions either!')
        raise

    if testing:
        # break the links
        util_io.delete(broken_dpath)
        util_io.delete(broken_fpath)

        if verbose:
            from ubelt import util_links
            util_links._dirstats(tempdir)

    try:
        # Cleanup the test directory
        util_io.delete(tempdir)
    except Exception:
        print('ERROR IN DELETE')
        from ubelt import util_links
        util_links._dirstats(tempdir)
        raise

    can_symlink = can_symlink_directories and can_symlink_files
    __win32_can_symlink__ = can_symlink
    if not can_symlink:
        warnings.warn('Cannot make real symlink. Falling back to junction')

    if verbose:
        print('can_symlink = {!r}'.format(can_symlink))
        print('__win32_can_symlink__ = {!r}'.format(__win32_can_symlink__))
    return can_symlink


def _symlink(path, link, overwrite=0, verbose=0):
    """
    Windows helper for ub.symlink
    """
    if exists(link) and not os.path.islink(link):
        # On windows a broken link might still exist as a hard link or a
        # junction. Overwrite it if it is a file and we cannot symlink.
        # However, if it is a non-junction directory then do not overwrite
        if verbose:
            print('link location already exists')
        is_junc = _win32_is_junction(link)
        # NOTE:
        # in python2 broken junctions are directories and exist
        # in python3 broken junctions are directories and do not exist
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
            if _win32_is_hardlinked(link, path):
                if verbose:
                    print('...and is a hard link that points to the same place')
                return link
            else:
                if verbose:
                    print('...and is a hard link that points somewhere else')
                if _win32_can_symlink():
                    raise IOError('Cannot overwrite potentially real file if we can symlink')
        if overwrite:
            if verbose:
                print('...overwriting')
            util_io.delete(link, verbose > 1)
        else:
            if exists(link):
                raise IOError('Link already exists')

    _win32_symlink2(path, link, verbose=verbose)


def _win32_symlink2(path, link, allow_fallback=True, verbose=0):
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


def _win32_symlink(path, link, verbose=0):
    """
    Creates real symlink. This will only work in versions greater than Windows
    Vista. Creating real symlinks requires admin permissions or at least
    specially enabled symlink permissions. On Windows 10 enabling developer
    mode should give you these permissions.
    """
    from ubelt import util_cmd
    if os.path.isdir(path):
        # directory symbolic link
        if verbose:
            print('... as directory symlink')
        command = 'mklink /D "{}" "{}"'.format(link, path)
        # Using the win32 API seems to result in privilege errors
        # but using shell commands does not have this problem. Weird.
        # jwfs.symlink(path, link, target_is_directory=True)
        # TODO: what do we need to do to use the windows api instead of shell?
    else:
        # file symbolic link
        if verbose:
            print('... as file symlink')
        command = 'mklink "{}" "{}"'.format(link, path)

    if command is not None:
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
    """
    # junctions store absolute paths
    path = os.path.abspath(path)
    link = os.path.abspath(link)

    from ubelt import util_cmd
    if os.path.isdir(path):
        # try using a junction (soft link)
        if verbose:
            print('... as soft link')

        # TODO: what is the windows api for this?
        command = 'mklink /J "{}" "{}"'.format(link, path)
    else:
        # try using a hard link
        if verbose:
            print('... as hard link')
        # command = 'mklink /H "{}" "{}"'.format(link, path)
        try:
            jwfs.link(path, link)  # this seems to be allowed
        except Exception:
            print('Failed to hardlink link={} to path={}'.format(link, path))
            raise
        command = None

    if command is not None:
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


def _win32_read_junction(path):
    """
    Returns the location that the junction points, raises ValueError if path is
    not a junction.

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

    # --- Older version based on using shell commands ---
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

    # new version using the windows api
    handle = jwfs.api.CreateFile(
            path, 0, 0, None, jwfs.api.OPEN_EXISTING,
            jwfs.api.FILE_FLAG_OPEN_REPARSE_POINT |
            jwfs.api.FILE_FLAG_BACKUP_SEMANTICS,
            None)

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
    subname = rdb.get_substitute_name()
    # probably has something to do with long paths, not sure
    if subname.startswith('?\\'):
        subname = subname[2:]
    return subname


def _win32_rmtree(path, verbose=0):
    """
    rmtree for win32 that treats junctions like directory symlinks.
    The junction removal portion may not be safe on race conditions.

    There is a known issue that prevents shutil.rmtree from
    deleting directories with junctions.
    https://bugs.python.org/issue31226
    """

    # --- old version using the shell ---
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


def _win32_is_hardlinked(fpath1, fpath2):
    """
    Test if two hard links point to the same location

    Example:
        >>> # xdoc: +REQUIRES(WIN32)
        >>> import ubelt as ub
        >>> root = ub.ensure_app_cache_dir('ubelt', 'win32_hardlink')
        >>> ub.delete(root)
        >>> ub.ensuredir(root)
        >>> fpath1 = join(root, 'fpath1')
        >>> fpath2 = join(root, 'fpath2')
        >>> ub.touch(fpath1)
        >>> ub.touch(fpath2)
        >>> fjunc1 = _win32_junction(fpath1, join(root, 'fjunc1'))
        >>> fjunc2 = _win32_junction(fpath2, join(root, 'fjunc2'))
        >>> assert _win32_is_hardlinked(fjunc1, fpath1)
        >>> assert _win32_is_hardlinked(fjunc2, fpath2)
        >>> assert not _win32_is_hardlinked(fjunc2, fpath1)
        >>> assert not _win32_is_hardlinked(fjunc1, fpath2)
    """
    # NOTE: jwf.samefile(fpath1, fpath2) seems to behave differently
    def get_read_handle(fpath):
        if os.path.isdir(fpath):
            dwFlagsAndAttributes = jwfs.api.FILE_FLAG_BACKUP_SEMANTICS
        else:
            dwFlagsAndAttributes = 0
        hFile = jwfs.api.CreateFile(fpath, jwfs.api.GENERIC_READ,
                                    jwfs.api.FILE_SHARE_READ, None,
                                    jwfs.api.OPEN_EXISTING,
                                    dwFlagsAndAttributes, None)
        return hFile

    def get_unique_id(hFile):
        info = jwfs.api.BY_HANDLE_FILE_INFORMATION()
        res = jwfs.api.GetFileInformationByHandle(hFile, info)
        jwfs.handle_nonzero_success(res)
        unique_id = (info.volume_serial_number, info.file_index_high,
                     info.file_index_low)
        return unique_id

    hFile1 = get_read_handle(fpath1)
    hFile2 = get_read_handle(fpath2)
    try:
        are_equal = (get_unique_id(hFile1) == get_unique_id(hFile2))
    except Exception:
        raise
    finally:
        jwfs.api.CloseHandle(hFile1)
        jwfs.api.CloseHandle(hFile2)
    return are_equal


def _win32_dir(path, star=''):
    """
    Using the windows cmd shell to get information about a directory
    """
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
