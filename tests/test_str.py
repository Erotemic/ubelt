import ubelt as ub


def test_capture_stdout_enabled() -> None:
    with ub.CaptureStdout(enabled=False) as cap:
        print('foobar')
    assert cap.text is None

    with ub.CaptureStdout(enabled=True) as cap:
        print('foobar')
    assert cap.text is not None
    assert cap.text.strip() == 'foobar'


def test_capture_stdout_exception() -> None:
    """
    CommandLine:
        pytest ubelt/tests/test_str.py::test_capture_stdout_exception -s
    """
    try:
        with ub.CaptureStdout(enabled=True) as cap:
            raise Exception('foobar')
    except Exception:
        pass
    assert cap.text is not None
    assert cap.text.strip() == ''
