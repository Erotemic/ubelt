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


def test_zopen_delegated_callable_lookup_occurs_once(tmp_path) -> None:
    """Accessing a descriptor must not evaluate it multiple times."""
    import ubelt as ub

    path = tmp_path / 'data.txt'
    path.write_text('hello')
    with ub.zopen(path, 'r') as file:
        class CountingHandle:
            def __init__(self, inner):
                self.inner = inner
                self.lookups = 0

            @property
            def read(self):
                self.lookups += 1
                return self.inner.read

            @property
            def closed(self):
                return self.inner.closed

            def close(self):
                return self.inner.close()

        proxy = CountingHandle(file._handle)
        file._handle = proxy
        method = file.read
        assert proxy.lookups == 1
        assert method() == 'hello'
        assert proxy.lookups == 1
