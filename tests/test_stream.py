

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
