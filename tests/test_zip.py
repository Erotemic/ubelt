from __future__ import annotations

def test_zopen_temporary_method_lifetime_and_close(tmp_path) -> None:
    import zipfile

    import ubelt as ub

    zippath = tmp_path / 'data.zip'
    with zipfile.ZipFile(zippath, 'w') as zfile:
        zfile.writestr('folder/data.txt', 'line1\nline2\n')

    internal_path = str(zippath) + '/folder/data.txt'

    # A delegated method on a temporary zopen must keep the wrapper alive for
    # the duration of the call.
    assert ub.zopen(internal_path, 'r').read() == 'line1\nline2\n'
    assert ub.zopen(internal_path, 'r').readline() == 'line1\n'

    file = ub.zopen(internal_path, 'r')
    owned_zfile = file.zfile
    assert owned_zfile.fp is not None
    file.close()
    assert file.closed
    assert owned_zfile.fp is None
    file.close()
