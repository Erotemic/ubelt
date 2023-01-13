"""
pytest tests/test_progiter.py
"""
import sys
from contextlib import contextmanager
from io import StringIO
from unittest.mock import patch

from xdoctest.utils import CaptureStdout
from xdoctest.utils import strip_ansi

from ubelt import ProgIter


def test_rate_format_string():
    # Less of a test than a demo
    rates = [1 * 10 ** i for i in range(-10, 10)]

    texts = []
    for rate in rates:
        rate_format = '4.2f' if rate > .001 else 'g'
        # Really cool: you can embed format strings inside format strings
        msg = '{rate:{rate_format}}'.format(rate=rate, rate_format=rate_format)
        texts.append(msg)
    assert texts == ['1e-10',
                     '1e-09',
                     '1e-08',
                     '1e-07',
                     '1e-06',
                     '1e-05',
                     '0.0001',
                     '0.001',
                     '0.01',
                     '0.10',
                     '1.00',
                     '10.00',
                     '100.00',
                     '1000.00',
                     '10000.00',
                     '100000.00',
                     '1000000.00',
                     '10000000.00',
                     '100000000.00',
                     '1000000000.00']


def test_rate_format():
    # Define a function that takes some time
    file = StringIO()
    prog = ProgIter(file=file)
    prog.begin()

    prog._iters_per_second = .000001
    msg = prog.format_message()
    rate_part = msg.split('rate=')[1].split(' Hz')[0]
    assert rate_part == '1e-06'

    prog._iters_per_second = .1
    msg = prog.format_message()
    rate_part = msg.split('rate=')[1].split(' Hz')[0]
    assert rate_part == '0.10'

    prog._iters_per_second = 10000
    msg = prog.format_message()
    rate_part = msg.split('rate=')[1].split(' Hz')[0]
    assert rate_part == '10000.00'


def test_progiter():
    # Define a function that takes some time
    def is_prime(n):
        return n >= 2 and not any(n % i == 0 for i in range(2, n))
    N = 500

    if False:
        file = StringIO()
        prog = ProgIter(range(N), clearline=False, file=file, freq=N // 10,
                        adjust=False)
        file.seek(0)
        print(file.read())

        prog = ProgIter(range(N), clearline=False)
        for n in prog:
            was_prime = is_prime(n)
            prog.set_extra('n=%r, was_prime=%r' % (n, was_prime,))
            if (n + 1) % 128 == 0 and was_prime:
                prog.set_extra('n=%r, was_prime=%r EXTRA' % (n, was_prime,))
        file.seek(0)
        print(file.read())

    total = 200
    N = 5000
    N0 = N - total
    print('N = %r' % (N,))
    print('N0 = %r' % (N0,))

    print('\n-----')
    print('Demo #0: progress can be disabled and incur essentially 0 overhead')
    print('However, the overhead of enabled progress is minimal and typically '
          'insignificant')
    print('this is verbosity mode verbose=0')
    sequence = (is_prime(n) for n in range(N0, N))
    if True:
        psequence = ProgIter(sequence, total=total, desc='demo0',
                             enabled=False)
        list(psequence)

    print('\n-----')
    print('Demo #1: progress is shown by default in the same line')
    print('this is verbosity mode verbose=1')
    sequence = (is_prime(n) for n in range(N0, N))
    if True:
        psequence = ProgIter(sequence, total=total, desc='demo1')
        list(psequence)

    # Default behavior adjusts frequency of progress reporting so
    # the performance of the loop is minimally impacted
    print('\n-----')
    print('Demo #2: clearline=False prints multiple lines.')
    print('Progress is only printed as needed')
    print('Notice the adjustment behavior of the print frequency')
    print('this is verbosity mode verbose=2')
    if True:
        sequence = (is_prime(n) for n in range(N0, N))
        psequence = ProgIter(sequence, total=total, clearline=False,
                             desc='demo2')
        list(psequence)
        # import utool as ut
        # print(ut.repr4(psequence.__dict__))

    print('\n-----')
    print('Demo #3: Adjustments can be turned off to give constant feedback')
    print('this is verbosity mode verbose=3')
    sequence = (is_prime(n) for n in range(N0, N))
    if True:
        psequence = ProgIter(sequence, total=total, adjust=False,
                             clearline=False, freq=100, desc='demo3')
        list(psequence)


def test_progiter_offset_10():
    """
    pytest -s  tests/test_progiter.py::test_progiter_offset_10
    """
    # Define a function that takes some time
    file = StringIO()
    list(ProgIter(range(10), total=20, verbose=3, start=10, file=file,
                  freq=5, show_times=False))
    file.seek(0)
    want = ['10/20...', '15/20...', '20/20...']
    got = [line.strip() for line in file.readlines()]
    if sys.platform.startswith('win32'):  # nocover
        # on windows \r seems to be mixed up with ansi sequences
        from xdoctest.utils import strip_ansi
        got = [strip_ansi(line).strip() for line in got]
    assert got == want


def test_progiter_offset_0():
    """
    pytest -s  tests/test_progiter.py::test_progiter_offset_0
    """
    # Define a function that takes some time
    file = StringIO()
    for _ in ProgIter(range(10), total=20, verbose=3, start=0, file=file,
                      freq=5, show_times=False):
        pass
    file.seek(0)
    want = ['0/20...', '5/20...', '10/20...']
    got = [line.strip() for line in file.readlines()]
    if sys.platform.startswith('win32'):  # nocover
        # on windows \r seems to be mixed up with ansi sequences
        from xdoctest.utils import strip_ansi
        got = [strip_ansi(line).strip() for line in got]
    assert got == want


def test_unknown_total():
    """
    Make sure a question mark is printed if the total is unknown
    """
    iterable = (_ for _ in range(0, 10))
    file = StringIO()
    prog = ProgIter(iterable, desc='unknown seq', file=file,
                    show_times=False, verbose=1)
    for n in prog:
        pass
    file.seek(0)
    got = [line.strip() for line in file.readlines()]
    # prints an eroteme if total is unknown
    assert len(got) > 0, 'should have gotten something'
    assert all('?' in line for line in got), 'all lines should have an eroteme'


def test_initial():
    """
    Make sure a question mark is printed if the total is unknown
    """
    file = StringIO()
    prog = ProgIter(initial=9001, file=file, show_times=False, clearline=False)
    message = prog.format_message_parts()[1]
    assert strip_ansi(message) == ' 9001/?... '


def test_clearline():
    """
    Make sure a question mark is printed if the total is unknown

    pytest tests/test_progiter.py::test_clearline
    """
    file = StringIO()
    # Clearline=False version should simply have a newline at the end.
    prog = ProgIter(file=file, show_times=False, clearline=False)
    before, message, after = prog.format_message_parts()
    assert before == ''
    assert strip_ansi(message).strip(' ') == '0/?...'
    # Clearline=True version should carrage return at the begining and have no
    # newline at the end.
    prog = ProgIter(file=file, show_times=False, clearline=True)
    before, message, after = prog.format_message_parts()
    assert before == '\r'
    assert strip_ansi(message).strip(' ') == '0/?...'


def test_disabled():
    prog = ProgIter(range(20), enabled=True)
    prog.begin()
    assert prog.started

    prog = ProgIter(range(20), enabled=False)
    prog.begin()
    prog.step()
    assert not prog.started


def test_eta_window_None():
    # nothing to check (that I can think of) run test for coverage
    prog = ProgIter(range(20), enabled=True, eta_window=None)
    for _ in prog:
        pass


def test_adjust_freq():
    # nothing to check (that I can think of) run test for coverage
    prog = ProgIter(range(20), enabled=True, eta_window=None, rel_adjust_limit=4.0)

    # Adjust frequency up to have each update happen every 1sec or so
    prog.freq = 1
    prog.time_thresh = 1.0
    prog._max_between_count = -1.0
    prog._max_between_time = -1.0
    prog._between_time = 1
    prog._between_count = 1000
    prog._adjust_frequency()
    assert prog.freq == 4

    # Adjust frequency down to have each update happen every 1sec or so
    prog.freq = 1000
    prog.time_thresh = 1.0
    prog._max_between_count = -1.0
    prog._max_between_time = -1.0
    prog._between_time = 1
    prog._between_count = 1
    prog._adjust_frequency()
    assert prog.freq == 250

    # No need to adjust frequency to have each update happen every 1sec or so
    prog.freq = 1
    prog.time_thresh = 1.0
    prog._max_between_count = -1.0
    prog._max_between_time = -1.0
    prog._between_time = 1
    prog._between_count = 1
    prog._adjust_frequency()
    assert prog.freq == 1


def test_tqdm_compatibility():
    prog = ProgIter(range(20), total=20, miniters=17, show_times=False)
    assert prog.pos == 0
    assert prog.freq == 17
    for _ in prog:
        pass

    with CaptureStdout() as cap:
        ProgIter.write('foo')
    assert cap.text.strip() == 'foo'

    with CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_description('new desc', refresh=False)
        prog.begin()
        prog.refresh()
        prog.close()
    assert prog.label == 'new desc'
    assert 'new desc' in cap.text.strip()

    with CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_description('new desc', refresh=True)
        prog.close()
    assert prog.label == 'new desc'
    assert 'new desc' in cap.text.strip()

    with CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_description_str('new desc')
        prog.begin()
        prog.refresh()
        prog.close()
    assert prog.label == 'new desc'
    assert 'new desc' in cap.text.strip()

    with CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_postfix({'foo': 'bar'}, baz='biz', x=object(), y=2)
        prog.begin()
    assert prog.length is None
    assert 'foo=bar' in cap.text.strip()
    assert 'baz=biz' in cap.text.strip()
    assert 'y=2' in cap.text.strip()
    assert 'x=<object' in cap.text.strip()

    with CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_postfix_str('bar baz', refresh=False)
    assert 'bar baz' not in cap.text.strip()


class IntObject:
    def __init__(self):
        self.n = 0

    def inc(self, *args, **kwargs):
        self.n += 1


@contextmanager
def _fake_time():
    t = IntObject()  # fake time in seconds
    with patch('ubelt.progiter.default_timer', side_effect=lambda: t.n):
        yield t


@contextmanager
def _message_count_only():
    cnt = IntObject()
    with patch.object(ProgIter, 'display_message', side_effect=cnt.inc):
        yield cnt


def test_adjust_binds_updates_to_time_thresh():
    with _fake_time() as t, _message_count_only() as cnt:
        prog = ProgIter(range(1000), enabled=True, adjust=True, time_thresh=1.0,
                        rel_adjust_limit=1000000.0, homogeneous=False)
        it = iter(prog)
        # Few fast updates at the beginning
        for i in range(10):
            next(it)
            t.n += 0.1
        # Followed by some extremely slow updates
        for i in range(10):
            next(it)
            t.n += 1000
        # Outputs should not get stuck at the few fast updates
        assert cnt.n > 8

    with _fake_time() as t, _message_count_only() as cnt:
        prog = ProgIter(range(1000), enabled=True, adjust=True, time_thresh=1.0,
                        rel_adjust_limit=1000000.0, homogeneous=False)
        it = iter(prog)
        # Few slow updates at the beginning
        for i in range(10):
            next(it)
            t.n += 100
        # Followed by a ton of extremely fast updates
        for i in range(990):
            next(it)
            t.n += 0.00001
        # Outputs should not spam the screen with messages
        assert cnt.n < 20


def test_homogeneous_heuristic_with_iter_lengths():
    for size in range(0, 10):
        list(ProgIter(range(size), homogeneous='auto'))


def test_mixed_iteration_and_step():
    # Check to ensure nothing breaks
    for adjust in [0, 1]:
        for homogeneous in [0, 1] if adjust else [0]:
            for size in range(0, 10):
                for n_inner_steps in range(size):
                    prog = ProgIter(range(size), adjust=adjust,
                                    homogeneous=homogeneous)
                    iprog = iter(prog)
                    try:
                        while True:
                            next(iprog)
                            for k in range(n_inner_steps):
                                prog.step()
                    except StopIteration:
                        ...


def test_end_message_is_displayed():
    """
    Older versions of progiter had a bug where the end step would not trigger
    if calculations were updated without a display
    """
    import io
    stream = io.StringIO()
    prog = ProgIter(range(1000), stream=stream)
    for i in prog:
        prog._update_all_calculations()
    stream.seek(0)
    text = stream.read()
    assert '1000/1000' in text, 'end message should have printed'


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
