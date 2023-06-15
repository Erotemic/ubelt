"""
TODO: test _can_symlink=False variants on systems that can symlink.
"""
from os.path import isdir
from os.path import isfile
from os.path import islink
from os.path import join, exists, relpath, dirname
import ubelt as ub
import pytest
import os
from ubelt import util_links


def test_rel_dir_link():
    """
    xdoctest ~/code/ubelt/tests/test_links.py test_rel_dir_link
    """
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_rel_dir_link').ensuredir()
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    real_dpath = join((dpath / 'dir1').ensuredir(), 'real')
    link_dpath = join((dpath / 'dir2').ensuredir(), 'link')
    ub.ensuredir(real_dpath)

    orig = os.getcwd()
    try:
        os.chdir(dpath)
        real_path = relpath(real_dpath, dpath)
        link_path = relpath(link_dpath, dpath)
        link = ub.symlink(real_path, link_path)
        # Note: on windows this is hacked.
        pointed = ub.util_links._readlink(link)
        resolved = os.path.realpath(ub.expandpath(join(dirname(link), pointed)))

        final_real_dpath = os.path.realpath(ub.expandpath(real_dpath))
        if final_real_dpath != resolved:
            raise AssertionError(f'{final_real_dpath} != {resolved}')
        # assert os.path.realpath(ub.expandpath(real_dpath)) == resolved
    except Exception:
        util_links._dirstats(dpath)
        util_links._dirstats(join(dpath, 'dir1'))
        util_links._dirstats(join(dpath, 'dir2'))
        print('TEST FAILED: test_rel_link')
        print('real_dpath = {!r}'.format(real_dpath))
        print('link_dpath = {!r}'.format(link_dpath))
        print('real_path = {!r}'.format(real_path))
        print('link_path = {!r}'.format(link_path))
        try:
            if 'link' in vars():
                print('link = {!r}'.format(link))
            if 'pointed' in vars():
                print('pointed = {!r}'.format(pointed))
            if 'resolved' in vars():
                print('resolved = {!r}'.format(resolved))
        except Exception:
            print('...rest of the names are not available')
        raise
    finally:
        util_links._dirstats(dpath)
        util_links._dirstats(join(dpath, 'dir1'))
        util_links._dirstats(join(dpath, 'dir2'))
        os.chdir(orig)


def test_rel_file_link():
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_rel_file_link').ensuredir()
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    real_fpath = join(ub.ensuredir((dpath, 'dir1')), 'real')
    link_fpath = join(ub.ensuredir((dpath, 'dir2')), 'link')
    ub.touch(real_fpath)

    orig = os.getcwd()
    try:
        os.chdir(dpath)
        real_path = relpath(real_fpath, dpath)
        link_path = relpath(link_fpath, dpath)
        link = ub.symlink(real_path, link_path)
        import sys
        if sys.platform.startswith('win32') and isfile(link):
            # Note: if windows hard links the file there is no way we can
            # tell that it was a symlink. Just verify it exists.
            from ubelt import _win32_links
            assert _win32_links._win32_is_hardlinked(real_fpath, link_fpath)
        else:
            pointed = ub.util_links._readlink(link)
            resolved = os.path.realpath(ub.expandpath(join(dirname(link), pointed)))
            assert os.path.realpath(ub.expandpath(real_fpath)) == resolved
    except Exception:
        util_links._dirstats(dpath)
        util_links._dirstats(join(dpath, 'dir1'))
        util_links._dirstats(join(dpath, 'dir2'))
        print('TEST FAILED: test_rel_link')
        print('real_fpath = {!r}'.format(real_fpath))
        print('link_fpath = {!r}'.format(link_fpath))
        print('real_path = {!r}'.format(real_path))
        print('link_path = {!r}'.format(link_path))
        try:
            if 'link' in vars():
                print('link = {!r}'.format(link))
            if 'pointed' in vars():
                print('pointed = {!r}'.format(pointed))
            if 'resolved' in vars():
                print('resolved = {!r}'.format(resolved))
        except Exception:
            print('...rest of the names are not available')
        raise
    finally:
        util_links._dirstats(dpath)
        util_links._dirstats(join(dpath, 'dir1'))
        util_links._dirstats(join(dpath, 'dir2'))
        os.chdir(orig)


def test_delete_symlinks():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_delete_symlinks
    """
    # TODO: test that we handle broken links
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_delete_links').ensuredir()

    happy_dpath = join(dpath, 'happy_dpath')
    happy_dlink = join(dpath, 'happy_dlink')
    happy_fpath = join(dpath, 'happy_fpath.txt')
    happy_flink = join(dpath, 'happy_flink.txt')
    broken_dpath = join(dpath, 'broken_dpath')
    broken_dlink = join(dpath, 'broken_dlink')
    broken_fpath = join(dpath, 'broken_fpath.txt')
    broken_flink = join(dpath, 'broken_flink.txt')

    def check_path_condition(path, positive, want, msg):
        if not want:
            positive = not positive
            msg = 'not ' + msg

        if not positive:
            util_links._dirstats(dpath)
            print('About to raise error: {}'.format(msg))
            print('path = {!r}'.format(path))
            print('exists(path) = {!r}'.format(exists(path)))
            print('islink(path) = {!r}'.format(islink(path)))
            print('isdir(path) = {!r}'.format(isdir(path)))
            print('isfile(path) = {!r}'.format(isfile(path)))
            raise AssertionError('path={} {}'.format(path, msg))

    def assert_sometrace(path, want=True):
        # Either exists or is a broken link
        positive = exists(path) or islink(path)
        check_path_condition(path, positive, want, 'has trace')

    def assert_broken_link(path, want=True):
        if util_links._can_symlink():
            print('path={} should{} be a broken link'.format(
                path, ' ' if want else ' not'))
            positive = not exists(path) and islink(path)
            check_path_condition(path, positive, want, 'broken link')
        else:
            # TODO: we can test this
            # positive = util_links._win32_is_junction(path)
            print('path={} should{} be a broken link (junction)'.format(
                path, ' ' if want else ' not'))
            print('cannot check this yet')
            # We wont be able to differentiate links and nonlinks for junctions
            # positive = exists(path)
            # check_path_condition(path, positive, want, 'broken link')

    util_links._dirstats(dpath)
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)
    util_links._dirstats(dpath)

    ub.ensuredir(happy_dpath, verbose=2)
    ub.ensuredir(broken_dpath, verbose=2)
    ub.touch(happy_fpath, verbose=2)
    ub.touch(broken_fpath, verbose=2)
    util_links._dirstats(dpath)

    ub.symlink(broken_fpath, broken_flink, verbose=2)
    ub.symlink(broken_dpath, broken_dlink, verbose=2)
    ub.symlink(happy_fpath, happy_flink, verbose=2)
    ub.symlink(happy_dpath, happy_dlink, verbose=2)
    util_links._dirstats(dpath)

    # Deleting the files should not delete the symlinks (windows)
    ub.delete(broken_fpath, verbose=2)
    util_links._dirstats(dpath)

    ub.delete(broken_dpath, verbose=2)
    util_links._dirstats(dpath)

    assert_broken_link(broken_flink, 1)
    assert_broken_link(broken_dlink, 1)
    assert_sometrace(broken_fpath, 0)
    assert_sometrace(broken_dpath, 0)

    assert_broken_link(happy_flink, 0)
    assert_broken_link(happy_dlink, 0)
    assert_sometrace(happy_fpath, 1)
    assert_sometrace(happy_dpath, 1)

    # broken symlinks no longer exist after they are deleted
    ub.delete(broken_dlink, verbose=2)
    util_links._dirstats(dpath)
    assert_sometrace(broken_dlink, 0)

    ub.delete(broken_flink, verbose=2)
    util_links._dirstats(dpath)
    assert_sometrace(broken_flink, 0)

    # real symlinks no longer exist after they are deleted
    # but the original data is fine
    ub.delete(happy_dlink, verbose=2)
    util_links._dirstats(dpath)
    assert_sometrace(happy_dlink, 0)
    assert_sometrace(happy_dpath, 1)

    ub.delete(happy_flink, verbose=2)
    util_links._dirstats(dpath)
    assert_sometrace(happy_flink, 0)
    assert_sometrace(happy_fpath, 1)


def test_modify_directory_symlinks():
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_modify_symlinks').ensuredir()
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    happy_dpath = dpath / 'happy_dpath'
    happy_dlink = dpath / 'happy_dlink'
    ub.ensuredir(happy_dpath, verbose=2)

    ub.symlink(happy_dpath, happy_dlink, verbose=2)

    # Test file inside directory symlink
    file_path1 = happy_dpath / 'file.txt'
    file_path2 = happy_dlink / 'file.txt'

    ub.touch(file_path1, verbose=2)
    assert file_path1.exists()
    assert file_path2.exists()

    file_path1.write_text('foo')
    assert file_path1.read_text() == 'foo'
    assert file_path2.read_text() == 'foo'

    file_path2.write_text('bar')
    assert file_path1.read_text() == 'bar'
    assert file_path2.read_text() == 'bar'

    ub.delete(file_path2, verbose=2)
    assert not file_path1.exists()
    assert not file_path2.exists()

    # Test directory inside directory symlink
    dir_path1 = happy_dpath / 'dir'
    dir_path2 = happy_dlink / 'dir'

    ub.ensuredir(dir_path1, verbose=2)
    assert dir_path1.exists()
    assert dir_path2.exists()

    subfile_path1 = dir_path1 / 'subfile.txt'
    subfile_path2 = dir_path2 / 'subfile.txt'

    subfile_path1.write_text('foo')
    assert subfile_path1.read_text() == 'foo'
    assert subfile_path2.read_text() == 'foo'

    subfile_path1.write_text('bar')
    assert subfile_path1.read_text() == 'bar'
    assert subfile_path2.read_text() == 'bar'

    ub.delete(dir_path1, verbose=2)
    assert not dir_path1.exists()
    assert not dir_path2.exists()


def test_modify_file_symlinks():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_modify_symlinks
    """
    # TODO: test that we handle broken links
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_modify_symlinks').ensuredir()
    happy_fpath = dpath / 'happy_fpath.txt'
    happy_flink = dpath / 'happy_flink.txt'
    ub.touch(happy_fpath, verbose=2)

    ub.symlink(happy_fpath, happy_flink, verbose=2)

    # Test file symlink
    happy_fpath.write_text('foo')
    assert happy_fpath.read_text() == 'foo'
    assert happy_flink.read_text() == 'foo'

    happy_flink.write_text('bar')
    assert happy_fpath.read_text() == 'bar'
    assert happy_flink.read_text() == 'bar'


def test_broken_link():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_broken_link
    """
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_broken_link').ensuredir()

    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)
    util_links._dirstats(dpath)

    broken_fpath = join(dpath, 'broken_fpath.txt')
    broken_flink = join(dpath, 'broken_flink.txt')

    ub.touch(broken_fpath, verbose=2)
    util_links._dirstats(dpath)
    ub.symlink(real_path=broken_fpath, link_path=broken_flink, verbose=2)

    util_links._dirstats(dpath)
    ub.delete(broken_fpath, verbose=2)

    util_links._dirstats(dpath)

    # make sure I am sane that this is the correct check.
    can_symlink = util_links._can_symlink()
    print('can_symlink = {!r}'.format(can_symlink))
    if can_symlink:
        # normal behavior
        assert islink(broken_flink)
        assert not exists(broken_flink)
    else:
        # on windows hard links are essentially the same file.
        # there is no trace that it was actually a link.
        assert exists(broken_flink)


def test_cant_overwrite_file_with_symlink():
    if ub.WIN32:
        # Can't distinguish this case on windows
        pytest.skip()

    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_cant_overwrite_file_with_symlink').ensuredir()
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    happy_fpath = join(dpath, 'happy_fpath.txt')
    happy_flink = join(dpath, 'happy_flink.txt')

    for verbose in [2, 1, 0]:
        print('=======')
        print('verbose = {!r}'.format(verbose))
        ub.delete(dpath, verbose=verbose)
        ub.ensuredir(dpath, verbose=verbose)
        ub.touch(happy_fpath, verbose=verbose)
        ub.touch(happy_flink)  # create a file where a link should be

        util_links._dirstats(dpath)
        with pytest.raises(FileExistsError):  # file exists error
            ub.symlink(happy_fpath, happy_flink, overwrite=False, verbose=verbose)

        with pytest.raises(FileExistsError):  # file exists error
            ub.symlink(happy_fpath, happy_flink, overwrite=True, verbose=verbose)


def test_overwrite_symlink():
    """
    CommandLine:
        python ~/code/ubelt/tests/test_links.py test_overwrite_symlink
    """

    # TODO: test that we handle broken links
    dpath = ub.Path.appdir('ubelt/tests/test_links', 'test_overwrite_symlink').ensuredir()
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    happy_fpath = join(dpath, 'happy_fpath.txt')
    other_fpath = join(dpath, 'other_fpath.txt')
    happy_flink = join(dpath, 'happy_flink.txt')

    for verbose in [2, 1, 0]:
        print('@==========@')
        print('verbose = {!r}'.format(verbose))

        print('[test] Setup')
        ub.delete(dpath, verbose=verbose)
        ub.ensuredir(dpath, verbose=verbose)
        ub.touch(happy_fpath, verbose=verbose)
        ub.touch(other_fpath, verbose=verbose)

        print('[test] Dirstats dpath')
        util_links._dirstats(dpath)

        print('[test] Create initial link (to happy)')
        ub.symlink(happy_fpath, happy_flink, verbose=verbose)

        print('[test] Dirstats dpath')
        util_links._dirstats(dpath)

        # Creating a duplicate link
        print('[test] Create a duplicate link (to happy)')
        ub.symlink(happy_fpath, happy_flink, verbose=verbose)

        print('[test] Dirstats dpath')
        util_links._dirstats(dpath)

        print('[test] Create an unauthorized overwrite link (to other)')
        with pytest.raises(Exception) as exc_info:  # file exists error
            ub.symlink(other_fpath, happy_flink, verbose=verbose)
        print(' * exc_info = {!r}'.format(exc_info))

        print('[test] Create an authorized overwrite link (to other)')
        ub.symlink(other_fpath, happy_flink, verbose=verbose, overwrite=True)

        print('[test] Dirstats dpath')
        ub.delete(other_fpath, verbose=verbose)

        print('[test] Create an unauthorized overwrite link (back to happy)')
        with pytest.raises(Exception) as exc_info:  # file exists error
            ub.symlink(happy_fpath, happy_flink, verbose=verbose)
        print(' * exc_info = {!r}'.format(exc_info))

        print('[test] Create an authorized overwrite link (back to happy)')
        ub.symlink(happy_fpath, happy_flink, verbose=verbose, overwrite=True)


def _force_junction(func):
    from functools import wraps
    @wraps(func)
    def _wrap(*args):
        if not ub.WIN32:
            pytest.skip()
        from ubelt import _win32_links
        _win32_links.__win32_can_symlink__ = False
        func(*args)
        _win32_links.__win32_can_symlink__ = None
    return _wrap


def test_symlink_to_rel_symlink():
    """
    Test a case with a absolute link to a relative link to a real path.
    """
    import ubelt as ub
    if ub.WIN32:
        import pytest
        pytest.skip('dont try on windows')

    dpath = ub.Path.appdir('ubelt/tests/links/sym-to-relsym')
    dpath.delete().ensuredir()

    level1 = (dpath / 'level1').ensuredir()

    real = dpath / 'real'
    link1 = level1 / 'link1'

    real.touch()

    print('Should create')

    # rel_link1_to_real = os.path.relpath(real, link1.parent)
    # FIXME: This ub.symlink behavior seems broken

    link1.symlink_to(os.path.relpath(real, link1.parent))
    # ub.symlink(real_path=rel_link1_to_real, link_path=link1, verbose=3)

    # ub.symlink(real_path=rel_link1_to_real, link_path=link2, verbose=3)
    """
    At this point we have:

    ├── level1
    │   ├── level2
    │   │   └── link2 -> /home/joncrall/.cache/ubelt/tests/links/sym-to-relsym/level1/link1
    │   └── link1 -> ../real
    └── real
    """
    # _ = ub.cmd(f'tree {dpath}', verbose=3)

    import pytest
    with pytest.raises(FileExistsError):
        ub.symlink(real_path=real, link_path=link1, verbose=3)

    # ub.symlink(real_path=link1, link_path=link2, verbose=1)


# class TestSymlinksForceJunction(object):
fj_test_delete_symlinks = _force_junction(test_delete_symlinks)
fj_test_modify_directory_symlinks = _force_junction(test_modify_directory_symlinks)
fj_test_modify_file_symlinks = _force_junction(test_modify_file_symlinks)
fj_test_broken_link = _force_junction(test_broken_link)
fj_test_overwrite_symlink = _force_junction(test_overwrite_symlink)


if __name__ == '__main__':
    r"""
    CommandLine:
        set PYTHONPATH=%PYTHONPATH%;C:/Users/erote/code/ubelt/ubelt/tests
        pytest ubelt/tests/test_links.py
        pytest ubelt/tests/test_links.py -s
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
