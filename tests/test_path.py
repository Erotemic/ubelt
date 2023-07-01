from os.path import exists, join
import ubelt as ub
# DEBUG_PATH = ub.Path.home().name == 'joncrall'


def test_pathlib_compatability():
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
    import pytest
    with pytest.warns(DeprecationWarning):
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
    import pytest
    base = ub.Path.appdir('ubelt/tests').ensuredir()
    folder = join(base, 'foo')
    member = join(folder, 'bar')
    with pytest.warns(DeprecationWarning):
        ub.ensuredir(folder, recreate=True)
    ub.ensuredir(member)
    assert exists(member)
    with pytest.warns(DeprecationWarning):
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


def demo_nested_paths(dpath, nfiles=2, ndirs=1, depth=0):
    for idx in range(nfiles):
        (dpath / f'file_{idx}.txt').write_text(f'hello world idx={idx} depth={depth}')

    subdirs = []
    for idx in range(ndirs):
        subdir = (dpath / f'subdir_{idx}').ensuredir()
        subdirs.append(subdir)

    if depth > 0:
        for subdir in subdirs:
            demo_nested_paths(subdir, nfiles=nfiles, ndirs=ndirs,
                                    depth=depth - 1)


def relative_contents(dpath):
    return [p.relative_to(dpath) for p in dpath.glob('**')]


def test_copy_directory_cases():
    """
    Ignore:

        cases = [
            {'dst': '{}'},
        ]

    """
    import pytest
    import ubelt as ub
    base = ub.Path.appdir('ubelt/tests/path/copy_move').delete().ensuredir()

    root1 = (base / 'root1').ensuredir()
    root2 = (base / 'root2').ensuredir()
    paths = {
        'empty': root1 / 'empty',
        'shallow': root1 / 'shallow',
        'deep': root1 / 'deep',
    }
    for d in paths.values():
        d.ensuredir()
    demo_nested_paths(paths['shallow'])
    demo_nested_paths(paths['deep'], depth=3)

    # Instead you can always exepct <dst>/<contents> to be the same as
    # <src>/<contents>.
    for key, src in paths.items():
        for meta in ['stats', 'mode', None]:
            kwargs = {
                'meta': meta
            }
            root2.delete().ensuredir()
            # Because root2 exists we error if overwrite if False
            with pytest.raises(FileExistsError):
                src.copy(root2, **kwargs)
            # When overwrite is True,
            src.copy(root2, overwrite=True, **kwargs)
            relative_contents(root2)
            contents1 = relative_contents(src)
            contents2 = relative_contents(root2)
            assert contents1 == contents2

            # We can copy to a directory that doesn't exist
            root2.delete().ensuredir()
            new_dpath = src.copy(root2 / src.name, **kwargs)
            assert new_dpath.name == src.name
            contents2 = relative_contents(new_dpath)
            # But we can't do it again
            with pytest.raises(FileExistsError):
                src.copy(root2 / src.name, **kwargs)
            assert contents2 == relative_contents(new_dpath)
            # Unless overwrite is True
            new_dpath = src.copy(root2 / src.name, overwrite=True, **kwargs)
            # And in all cases the contents should be unchanged
            assert contents2 == relative_contents(new_dpath)

            # Test copy src into root2/sub1/sub2 when root/sub1 does not exist
            root2.delete().ensuredir()
            dst = root2 / 'sub1/sub2'
            new_dpath = src.copy(dst, **kwargs)
            assert new_dpath.name == 'sub2'
            # Unlike cp, Path.copy will create the intermediate directories
            assert contents1 == relative_contents(new_dpath)

        if 0 and ub.LINUX:
            """
            In all cases we have a folder
                <src> = <parent1>/<name>

                with members

                <parent1>/<name>/<contents>

                and

                <dst> = <parent2>/<dname>
            """
            verbose = 2
            """
            Case:
                copy ``<parent>/<name>`` into ``<dst>``
                and  ``<dst>/<name>`` does not exist,
                then cp will result in ``<dst>/<name>/<contents>``

                THEN

                copy ``<parent1>/<name>`` into ``<dst>``
                and  ``<dst>/<name>`` exists,
                then cp will result in ``<dst>/<name>/<contents>``

            CP recognizes that ``<dst>/<name>`` does not exist and makes a new
            directory <dst>/<name> to correspond to to the <src>

            THEN

            CP recognizes that ``<dst>/<name>`` does exist assumes
            that should correspond to <src>
            """
            root2.delete().ensuredir()
            dst = root2
            ub.cmd(f"cp -rv {src} {dst}", verbose=verbose)
            contents1 = relative_contents(src)
            contents2 = relative_contents(root2)
            assert len(contents1) == (len(contents2) - 1)

            ub.cmd(f"cp -rv {src} {dst}", verbose=verbose)
            contents1 = relative_contents(src)
            contents2 = relative_contents(root2)
            assert len(contents1) == (len(contents2) - 1)

            """
            Case:
                copy ``<parent1>/<name>`` into ``<parent2>/<name2>``
                and  ``<parent2>/<name2>`` does not exist,
                then cp will result in ``<dst>/<name2>/<contents>``

                THEN

                copy ``<parent1>/<name>`` into ``<parent2>/<name2>``
                and  ``<parent2>/<name2>`` does exist,
                then cp will result in ``<parent2>/<name2>/<name>/<contents>``

            Because <name2> in <parent> does not exist, it assumes you want to
            effectively *change the name* of your folder.

            THEN

            This is the weird case that Path.copy avoids by not pretending that
            you can use the directory name from the source implicitly in the
            destination.
            """
            root2.delete().ensuredir()
            name2 = f'{src.name}2'
            dst = root2 / name2
            ub.cmd(f"cp -rv {src} {dst}", verbose=verbose)
            contents1 = relative_contents(src)
            contents2 = relative_contents(root2)
            assert len(contents1) == (len(contents2) - 1)

            dst = root2 / name2
            ub.cmd(f"cp -rv {src} {dst}", verbose=verbose)
            contents1 = relative_contents(src)
            contents2 = relative_contents(root2)
            assert len(contents1) * 2 == (len(contents2) - 1)

            """
            Case:
                copy ``<parent>/<name>`` into ``<parent2>/<sub1>/<sub2>``
                and  ``<parent2>/<sub1>`` does not exist,
                then cp will error because it wont create intermediate
                directories
            """
            root2.delete().ensuredir()
            dst = root2 / 'sub1/sub2'
            info = ub.cmd(f"cp -rv {src} {dst}", verbose=verbose)
            assert info['ret'] == 1
            contents2 = relative_contents(root2)
            assert len(contents2) == 1


def test_move_directory_cases():
    """
    Ignore:

        cases = [
            {'dst': '{}'},
        ]

    """
    import pytest
    import ubelt as ub
    base = ub.Path.appdir('ubelt/tests/path/move').delete().ensuredir()

    root1 = (base / 'root1').ensuredir()
    root2 = (base / 'root2').ensuredir()
    paths = {
        'empty': root1 / 'empty',
        'shallow': root1 / 'shallow',
        'deep': root1 / 'deep',
    }
    for d in paths.values():
        d.ensuredir()

    # Instead you can always exepct <dst>/<contents> to be the same as
    # <src>/<contents>.
    for key, src in paths.items():
        for meta in ['stats', 'mode', None]:

            # Reset original dires
            for d in paths.values():
                d.ensuredir()
            demo_nested_paths(paths['shallow'])
            demo_nested_paths(paths['deep'], depth=3)

            kwargs = {
                'meta': meta
            }
            root2.delete().ensuredir()
            # We cannot move to a file that exists
            with pytest.raises(FileExistsError):
                src.move(root2, **kwargs)

            contents1 = relative_contents(src)
            # We can move to a directory that doesn't exist
            root2.delete().ensuredir()
            new_dpath = src.move(root2 / src.name, **kwargs)
            assert new_dpath.name == src.name
            contents2 = relative_contents(new_dpath)
            assert not src.exists()
            assert contents1 == contents2

            with pytest.raises(FileExistsError):
                src.move(root2 / src.name, **kwargs)

            # Test move src into root2/sub1/sub2 when root/sub1 does not exist
            # Reset original dires
            for d in paths.values():
                d.ensuredir()
            demo_nested_paths(paths['shallow'])
            demo_nested_paths(paths['deep'], depth=3)
            root2.delete().ensuredir()
            dst = root2 / 'sub1/sub2'
            new_dpath = src.move(dst, **kwargs)
            assert new_dpath.name == 'sub2'
            # Unlike cp, Path.move will create the intermediate directories
            assert contents1 == relative_contents(new_dpath)
