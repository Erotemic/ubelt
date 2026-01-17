

def test_capture_stream_error():
    import ubelt as ub
    class DummyException(Exception):
        ...
    try:
        with ub.CaptureStdout() as cap:
            print('hello there')
            raise DummyException
    except DummyException:
        ...
    assert cap.text.startswith('hello there')


def test_tee_stringio_flush_and_aliases():
    import io
    import ubelt as ub
    redirect = io.StringIO()
    tee = ub.TeeStringIO(redirect)
    tee.write('data')
    tee.flush()
    assert redirect.getvalue() == 'data'

    cap = ub.CaptureStdout(suppress=True, enabled=False)
    assert cap.cap_stdout is None
    assert cap.orig_stdout is None
