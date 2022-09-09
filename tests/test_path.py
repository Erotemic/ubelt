from os.path import exists, join
import ubelt as ub


DEBUG_PATH = ub.Path.home().name == 'joncrall'


def test_pathlib():
    import pathlib
    base = pathlib.Path(ub.Path.appdir('ubelt').ensuredir())
    dpath = base.joinpath('test_pathlib_mkdir')

    # ensuredir
    ub.delete(dpath)
    assert not dpath.exists()
    got = ub.ensuredir(dpath)
    assert got.exists()

    # shrinkuser
    assert ub.shrinkuser(base).startswith('~')

    assert ub.augpath(base, prefix='foo').endswith('fooubelt')
    assert not ub.expandpath(base).startswith('~')


def test_tempdir():
    temp = ub.TempDir()
    assert temp.dpath is None
    temp.ensure()
    assert exists(temp.dpath)
    # Double ensure for coverage
    temp.ensure()
    assert exists(temp.dpath)

    dpath = temp.dpath
    temp.cleanup()
    assert not exists(dpath)
    assert temp.dpath is None


def test_augpath_identity():
    assert ub.augpath('foo') == 'foo'
    assert ub.augpath('foo/bar') == join('foo', 'bar')
    assert ub.augpath('') == ''


def test_augpath_dpath():
    assert ub.augpath('foo', dpath='bar') == join('bar', 'foo')
    assert ub.augpath('foo/bar', dpath='baz') == join('baz', 'bar')
    assert ub.augpath('', dpath='bar').startswith('bar')


def test_ensuredir_recreate():
    base = ub.Path.appdir('ubelt/tests').ensuredir()
    folder = join(base, 'foo')
    member = join(folder, 'bar')
    ub.ensuredir(folder, recreate=True)
    ub.ensuredir(member)
    assert exists(member)
    ub.ensuredir(folder, recreate=True)
    assert not exists(member)


def test_ensuredir_verbosity():
    base = ub.Path.appdir('ubelt/tests').ensuredir()

    with ub.CaptureStdout() as cap:
        ub.ensuredir(join(base, 'foo'), verbose=0)
    assert cap.text == ''
    # None defaults to verbose=0
    with ub.CaptureStdout() as cap:
        ub.ensuredir((base, 'foo'), verbose=None)
    assert cap.text == ''

    ub.delete(join(base, 'foo'))
    with ub.CaptureStdout() as cap:
        ub.ensuredir(join(base, 'foo'), verbose=1)
    assert 'creating' in cap.text
    with ub.CaptureStdout() as cap:
        ub.ensuredir(join(base, 'foo'), verbose=1)
    assert 'existing' in cap.text


def _demo_directory_structure():
    import ubelt as ub
    import uuid

    level = 0

    suffix = ub.hash_data(uuid.uuid4())[0:8]
    dpath = ub.Path.appdir('ubelt', 'tests', 'test_path')
    base = (dpath / suffix).delete().ensuredir()

    (base / 'root' / 'dir_L0_X0_A').ensuredir()

    if level > 2:
        (base / 'root' / 'dir_L0_X0_A' / 'dir_L1_X0_B').ensuredir()

    if level > 1:
        (base / 'root' / 'dir_L0_X1_C').ensuredir()

    (base / 'root' / 'inside_dir').ensuredir()
    (base / 'root' / 'links').ensuredir()
    (base / 'outside_dir').ensuredir()

    (base / 'root' / 'file_L0_X0_a.txt').touch()

    if level > 1:
        (base / 'root' / 'dir_L0_X0_A' / 'file_L1_X0_b.txt').touch()

    if level > 1:
        (base / 'root' / 'dir_L0_X1_C' / 'file_L1_X0_c.txt').touch()

    (base / 'root' / 'inside_dir' / 'inside_file.txt').touch()
    (base / 'outside_dir' / 'outside_file.txt').touch()

    # Create links inside and outside the root
    to_abs_symlink = []
    to_abs_symlink.append((base / 'root/inside_dir/inside_file.txt' , base / 'root/links/inside_flink.txt'))
    to_abs_symlink.append((base / 'outside_dir/outside_file.txt'    , base / 'root/links/outside_flink.txt'))
    to_abs_symlink.append((base / 'outside_dir'                     , base / 'root/links/outside_dlink'))
    to_abs_symlink.append((base / 'root/inside_dir'                 , base / 'root/links/inside_dlink'))
    to_abs_symlink.append((base / 'root/links/cyclic'                , (base / 'root/links/cyclic/n1/n2').ensuredir() / 'loop'))

    to_rel_symlink = []
    to_rel_symlink.append((base / 'root/inside_dir/inside_file.txt' , base / 'root/links/rel_inside_flink.txt'))
    to_rel_symlink.append((base / 'outside_dir/outside_file.txt'    , base / 'root/links/rel_outside_flink.txt'))
    to_rel_symlink.append((base / 'outside_dir'                     , base / 'root/links/rel_outside_dlink'))
    to_rel_symlink.append((base / 'root/inside_dir'                 , base / 'root/links/rel_inside_dlink'))
    to_rel_symlink.append((base / 'root/links/rel_cyclic'           , (base / 'root/links/rel_cyclic/n1/n2/').ensuredir() / 'rel_loop'))

    import os
    for real, link in to_abs_symlink:
        link.symlink_to(real)

    for real, link in to_rel_symlink:
        rel_real = os.path.relpath(real, link.parent)
        link.symlink_to(rel_real)
    return base


### MOVE TESTS


def test_move_dir_to_non_existing():
    base = _demo_directory_structure()
    root = base / 'root'

    if ub.POSIX:
        root2 = root.copy(root.augment(tail='2'))
        root3 = root.copy(root.augment(tail='3'))

    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)

    dst = root.move(base / 'our_move')

    if ub.POSIX:
        ub.cmd(f'mv {root2} {base}/posix_move', verbose=2, check=1)
        ub.cmd(f'mv -T {root3} {base}/posix_moveT', verbose=2, check=1)

    print(f'dst={dst}')
    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)

    if ub.POSIX:
        # We behave like POSIX mv here in both cases here
        case1 = _comparable_walk(base / 'posix_move')
        case2 = _comparable_walk(base / 'posix_moveT')
        case3 = _comparable_walk(base / 'our_move')
        assert case1 == case2 == case3

    base.delete()


def test_move_to_nested_non_existing():
    base = _demo_directory_structure()
    root = base / 'root'

    if ub.POSIX:
        root2 = root.copy(root.augment(tail='2'))
        root3 = root.copy(root.augment(tail='3'))

    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)

    # shutil move will make the parent directory if it doesn't exist.
    root.move(base / 'our/move')

    if ub.POSIX:
        # Posix fails unless the parent exists
        (base / 'posix').ensuredir()
        ub.cmd(f'mv -v {root2} {base}/posix/move', verbose=2, check=1)
        ub.cmd(f'mv -Tv {root3} {base}/posix/moveT', verbose=2, check=1)
    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)

    if ub.POSIX:
        # We behave like POSIX mv here in both cases here
        # up to the fact that we will always create the dir, whereas mv wont
        case1 = _comparable_walk(base / 'posix/move')
        case2 = _comparable_walk(base / 'posix/moveT')
        case3 = _comparable_walk(base / 'our/move')
        assert case1 == case2 == case3

    base.delete()


def test_move_dir_to_existing_dir_noconflict():
    base = _demo_directory_structure()
    root = base / 'root'

    (base / 'our_move').ensuredir()

    if ub.POSIX:
        root2 = root.copy(root.augment(tail='2'))
        root3 = root.copy(root.augment(tail='3'))
        (base / 'posix_move').ensuredir()
        (base / 'posix_moveT').ensuredir()

    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)

    import pytest
    with pytest.raises(IOError):
        # shutil.move behaves similar to posix with -T
        # We are just going to disallow this case
        root.move(base / 'our_move')

    if ub.POSIX:
        ub.cmd(f'mv {root2} {base}/posix_move', verbose=2, check=1)
        ub.cmd(f'mv -T {root3} {base}/posix_moveT', verbose=2, check=1)

    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)

    base.delete()


def test_move_dir_to_existing_dir_withconflict():
    base = _demo_directory_structure()

    root = base / 'root'
    bluntobject = (root / 'will_they_wont_they.txt')
    bluntobject.write_text('smash!')

    if ub.POSIX:
        root2 = root.copy(root.augment(tail='2'))
        root3 = root.copy(root.augment(tail='3'))  # NOQA

    dst1 = (base / 'our_move').ensuredir()
    dst2 = (base / 'posix_move').ensuredir()
    dst3 = (base / 'posix_move_T').ensuredir()

    toclobber1 = (dst1 / 'will_they_wont_they.txt')
    toclobber1.write_text('I hope nobody clobbers me!')
    disjoint1 = (dst1 / 'disjoint.txt')
    disjoint1.write_text('I should be disjoint!')

    toclobber2 = (dst2 / 'will_they_wont_they.txt')
    toclobber2.write_text('I hope nobody clobbers me!')
    disjoint2 = (dst2 / 'disjoint.txt')
    disjoint2.write_text('I should be disjoint!')

    toclobber3 = (dst3 / 'will_they_wont_they.txt')
    toclobber3.write_text('I hope nobody clobbers me!')
    disjoint3 = (dst3 / 'disjoint.txt')
    disjoint3.write_text('I should be disjoint!')

    if DEBUG_PATH:
        import xdev
        print('BEFORE MOVE')
        xdev.tree_repr(base)

    # This case is weird, dont let the user do it.
    # they can use shutil if they want
    import pytest
    with pytest.raises(IOError):
        root.move(dst1)

    if 0:
        if ub.POSIX:
            ub.cmd(f'mv -v {root2} {dst2}', verbose=2, check=1)
            # The mv command wont move a non-empty directory!
            # Maybe we shouldn't either.
            # ub.cmd(f'mv -T -u -f -v {root3} {dst3}', verbose=3, check=1)

        if DEBUG_PATH:
            import xdev
            print('AFTER MOVE')
            xdev.tree_repr(base)

        got = toclobber1.read_text()
        # THIS IS VERY SURPRISING, the file being moved is clobbered, but the file
        # in the dst is safe!
        assert got != 'smash!'
        assert not bluntobject.exists()

        if ub.POSIX:
            got2 = toclobber3.read_text()
            assert got2 == 'smash!'

        assert toclobber1.exists()
        assert bluntobject.exists()
        assert disjoint1.exists()
        assert disjoint1.read_text() == 'I should be disjoint!'

        if ub.POSIX:
            assert disjoint2.exists()
            assert disjoint2.read_text() == 'I should be disjoint!'
            assert disjoint3.exists()
            assert disjoint3.read_text() == 'I should be disjoint!'

    base.delete()

### Simple Copy Tests


def test_copy_basic():
    dpath = ub.Path.appdir('ubelt', 'tests', 'test_path', 'test_copy_basic')
    dpath.delete().ensuredir()
    fpath = (dpath / 'file.txt')
    fpath.write_text('foobar')
    empty_dpath = (dpath / 'empty_dir').ensuredir()
    full_dpath = (dpath / 'full_dir').ensuredir()
    (full_dpath / 'nested_file.txt').touch()

    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(dpath)

    fpath.copy(fpath.augment(prefix='copied_'))
    empty_dpath.copy(empty_dpath.augment(prefix='copied_'))
    full_dpath.copy(full_dpath.augment(prefix='copied_'))

    # Doing it again will fail
    import pytest
    with pytest.raises(IOError):
        fpath.copy(fpath.augment(prefix='copied_'))
    with pytest.raises(IOError):
        empty_dpath.copy(empty_dpath.augment(prefix='copied_'))
    with pytest.raises(IOError):
        full_dpath.copy(full_dpath.augment(prefix='copied_'))

    # But with overwrite=True it is ok
    fpath.copy(fpath.augment(prefix='copied_'), overwrite=True)
    empty_dpath.copy(empty_dpath.augment(prefix='copied_'), overwrite=True)
    full_dpath.copy(full_dpath.augment(prefix='copied_'), overwrite=True)

    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(dpath)


def test_copy_meta():
    dpath = ub.Path.appdir('ubelt', 'tests', 'test_path', 'test_copy_basic')
    dpath.delete().ensuredir()
    fpath = (dpath / 'file.txt')
    fpath.write_text('foobar')
    empty_dpath = (dpath / 'empty_dir').ensuredir()
    full_dpath = (dpath / 'full_dir').ensuredir()
    (full_dpath / 'nested_file.txt').touch()

    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(dpath)

    for meta in ['stats', 'mode', None]:
        prefix = 'copied_' + str(meta) + '_'
        fpath.copy(fpath.augment(prefix=prefix), meta=meta)
        empty_dpath.copy(empty_dpath.augment(prefix=prefix))
        full_dpath.copy(full_dpath.augment(prefix=prefix))

    # TODO: verify that the metadata really did copy as intended
    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(dpath)

### Simple Move Tests


def test_move_basic():
    dpath = ub.Path.appdir('ubelt', 'tests', 'test_path', 'test_move_basic')
    dpath.delete().ensuredir()
    fpath = (dpath / 'file.txt')
    fpath.write_text('foobar')
    empty_dpath = (dpath / 'empty_dir').ensuredir()
    full_dpath = (dpath / 'full_dir').ensuredir()
    (full_dpath / 'nested_file.txt').touch()

    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(dpath)

    fpath.move(fpath.augment(prefix='moved_'))
    empty_dpath.move(empty_dpath.augment(prefix='moved_'))
    full_dpath.move(full_dpath.augment(prefix='moved_'))

    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(dpath)


def test_move_meta():
    base_dpath = ub.Path.appdir('ubelt', 'tests', 'test_path', 'test_move_basic')
    base_dpath.delete().ensuredir()

    for meta in ['stats', 'mode', None]:
        prefix = 'copied_' + str(meta) + '_'
        dpath = (base_dpath / prefix).ensuredir()
        fpath = (dpath / 'file.txt')
        fpath.write_text('foobar')
        empty_dpath = (dpath / 'empty_dir').ensuredir()
        full_dpath = (dpath / 'full_dir').ensuredir()
        (full_dpath / 'nested_file.txt').touch()

        fpath.move(fpath.augment(prefix=prefix), meta=meta)
        empty_dpath.move(empty_dpath.augment(prefix=prefix))
        full_dpath.move(full_dpath.augment(prefix=prefix))

    # TODO: test that the metadata really did move as intended

    if DEBUG_PATH:
        print('AFTER MOVE')
        import xdev
        xdev.tree_repr(base_dpath)


### COPY TESTS


def test_copy_dir_to_non_existing():
    base = _demo_directory_structure()
    root = base / 'root'
    if DEBUG_PATH:
        print('BEFORE COPY')
        import xdev
        xdev.tree_repr(base)

    dst = root.copy(base / 'our_copy')

    if ub.POSIX:
        ub.cmd(f'cp -r {root} {base}/posix_copy', verbose=2)

    print(f'dst={dst}')
    if DEBUG_PATH:
        print('AFTER COPY')
        import xdev
        xdev.tree_repr(base)

    if ub.POSIX:
        # Our copy should behave like the posix copy
        case1 = _comparable_walk(base / 'our_copy')
        case2 = _comparable_walk(base / 'posix_copy')
        print('case1 = {}'.format(ub.repr2(case1, nl=1)))
        print('case2 = {}'.format(ub.repr2(case2, nl=1)))
        assert case1 == case2

    base.delete()


def test_copy_to_nested_non_existing_with_different_symlink_flags():
    base = _demo_directory_structure()
    root = base / 'root'
    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)
    root.copy(base / 'new_subdir' / 'new_root_FD0_FF1', follow_dir_symlinks=False, follow_file_symlinks=True)
    root.copy(base / 'new_subdir' / 'new_root_FD0_FF0', follow_dir_symlinks=False, follow_file_symlinks=False)
    (root / 'links' / 'cyclic').delete()
    (root / 'links' / 'rel_cyclic').delete()
    root.copy(base / 'new_subdir' / 'new_root_FD1_FF1', follow_dir_symlinks=True, follow_file_symlinks=True)
    root.copy(base / 'new_subdir' / 'new_root_FD1_FF0', follow_dir_symlinks=True, follow_file_symlinks=False)
    if DEBUG_PATH:
        import xdev
        xdev.tree_repr(base)
    base.delete()


def test_copy_dir_to_existing_dir_noconflict():
    base = _demo_directory_structure()
    root = base / 'root'
    (root / 'links' / 'cyclic').delete()
    (root / 'links' / 'rel_cyclic').delete()

    dst1 = (base / 'our_copy').ensuredir()
    dst2 = (base / 'posix_copy').ensuredir()
    dst3 = (base / 'posix_copyT').ensuredir()

    if DEBUG_PATH:
        import xdev
        print('BEFORE MOVE')
        xdev.tree_repr(base)

    root.copy(dst1, overwrite=True)

    if ub.POSIX:
        # We behave like posix copy with T here.
        ub.cmd(f'cp -r {root} {dst2}', verbose=2)
        ub.cmd(f'cp -r -T {root} {dst3}', verbose=2)

    if DEBUG_PATH:
        import xdev
        print('AFTER MOVE')
        xdev.tree_repr(base)

    if ub.POSIX:
        # Our copy should behave like the posix copy
        case1 = _comparable_walk(base / 'our_copy')
        case2 = _comparable_walk(base / 'posix_copy')
        case3 = _comparable_walk(base / 'posix_copyT')
        assert case1 == case3
        assert case1 != case2
    base.delete()


def test_copy_dir_to_existing_dir_withconflict():
    base = _demo_directory_structure()

    root = base / 'root'
    bluntobject = (root / 'will_they_wont_they.txt')
    bluntobject.write_text('smash!')

    dst1 = (base / 'our_copy').ensuredir()
    dst2 = (base / 'posix_copy').ensuredir()
    dst3 = (base / 'posix_copyT').ensuredir()

    toclobber1 = (dst1 / 'will_they_wont_they.txt')
    toclobber1.write_text('I hope nobody clobbers me!')
    disjoint1 = (dst1 / 'disjoint.txt')
    disjoint1.write_text('I should be disjoint!')

    toclobber2 = (dst2 / 'will_they_wont_they.txt')
    toclobber2.write_text('I hope nobody clobbers me!')
    disjoint2 = (dst2 / 'disjoint.txt')
    disjoint2.write_text('I should be disjoint!')

    toclobber3 = (dst3 / 'will_they_wont_they.txt')
    toclobber3.write_text('I hope nobody clobbers me!')
    disjoint3 = (dst3 / 'disjoint.txt')
    disjoint3.write_text('I should be disjoint!')

    if DEBUG_PATH:
        import xdev
        print('BEFORE MOVE')
        xdev.tree_repr(base)

    root.copy(dst1, overwrite=True)

    if ub.POSIX:
        ub.cmd(f'cp -r {root} {dst2}', verbose=2, check=1)
        ub.cmd(f'cp -r -T {root} {dst3}', verbose=2, check=1)

    if DEBUG_PATH:
        import xdev
        print('AFTER MOVE')
        xdev.tree_repr(base)

    # This behavior makes more sense to me
    got = toclobber1.read_text()
    assert got == 'smash!'

    if ub.POSIX:
        got2 = toclobber3.read_text()
        assert got2 == 'smash!'

    assert toclobber1.exists()
    assert bluntobject.exists()
    assert disjoint1.exists()
    assert disjoint1.read_text() == 'I should be disjoint!'

    if ub.POSIX:
        assert disjoint2.exists()
        assert disjoint2.read_text() == 'I should be disjoint!'
        assert disjoint3.exists()
        assert disjoint3.read_text() == 'I should be disjoint!'

    if ub.POSIX:
        # Our copy should behave like the posix copy
        case1 = _comparable_walk(base / 'our_copy')
        case2 = _comparable_walk(base / 'posix_copy')
        case3 = _comparable_walk(base / 'posix_copyT')
        print('case1 = {}'.format(ub.repr2(case1, nl=1)))
        print('case3 = {}'.format(ub.repr2(case3, nl=1)))
        print('case2 = {}'.format(ub.repr2(case2, nl=1)))
        assert case1 == case3
        assert case1 != case2
    base.delete()


def _comparable_walk(p):
    return sorted([(tuple(sorted(f)), tuple(sorted(d))) for (r, f, d) in (p).walk()])
