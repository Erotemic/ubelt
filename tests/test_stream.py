def test_capture_stream_error() -> None:
    import ubelt as ub

    class DummyException(Exception): ...

    try:
        with ub.CaptureStdout() as cap:
            print('hello there')
            raise DummyException
    except DummyException:
        ...
    assert cap.text is not None
    assert cap.text.startswith('hello there')


def test_capture_stream_stream_assign() -> None:
    import ubelt as ub

    with ub.CaptureStdout() as cap:
        print('hello there')
        assert cap.cap_stream is not None
        cap.cap_stream.flush()
    assert cap.text is not None
    assert cap.text.startswith('hello there')
    # Test backward compatibility properties
    assert cap.cap_stdout is cap.cap_stream  # type: ignore
    assert cap.orig_stdout is cap.orig_stream  # type: ignore


def test_tee_string_io_flush() -> None:
    import io

    from ubelt.util_stream import TeeStringIO

    # Test flush with redirect
    tee = TeeStringIO(redirect=io.StringIO())
    tee.write('test')
    tee.flush()  # Should call redirect.flush()
    # Test flush without redirect
    tee2 = TeeStringIO()
    tee2.flush()  # Should not call redirect.flush()
