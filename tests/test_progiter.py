# -*- coding: utf-8 -*-
"""
pytest ubelt/tests/test_progiter.py
"""
from six.moves import cStringIO
from xdoctest.utils import strip_ansi
from ubelt.progiter import ProgIter
import sys


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
    import ubelt as ub
    file = cStringIO()
    prog = ub.ProgIter(file=file)
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
    from ubelt import Timer
    # Define a function that takes some time
    def is_prime(n):
        return n >= 2 and not any(n % i == 0 for i in range(2, n))
    N = 500

    if False:
        file = cStringIO()
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
    # N = 5000
    N = 500
    N0 = N - total
    print('N = %r' % (N,))
    print('N0 = %r' % (N0,))

    print('\n-----')
    print('Demo #0: progress can be disabled and incur essentially 0 overhead')
    print('However, the overhead of enabled progress is minimal and typically '
          'insignificant')
    print('this is verbosity mode verbose=0')
    sequence = (is_prime(n) for n in range(N0, N))
    with Timer('demo0'):
        psequence = ProgIter(sequence, total=total, desc='demo0',
                             enabled=False)
        list(psequence)

    print('\n-----')
    print('Demo #1: progress is shown by default in the same line')
    print('this is verbosity mode verbose=1')
    sequence = (is_prime(n) for n in range(N0, N))
    with Timer('demo1'):
        psequence = ProgIter(sequence, total=total, desc='demo1')
        list(psequence)

    # Default behavior adjusts frequency of progress reporting so
    # the performance of the loop is minimally impacted
    print('\n-----')
    print('Demo #2: clearline=False prints multiple lines.')
    print('Progress is only printed as needed')
    print('Notice the adjustment behavior of the print frequency')
    print('this is verbosity mode verbose=2')
    with Timer('demo2'):
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
    with Timer('demo3'):
        psequence = ProgIter(sequence, total=total, adjust=False,
                             clearline=False, freq=100, desc='demo3')
        list(psequence)


def test_progiter_offset_10():
    """
    pytest -s  ~/code/ubelt/ubelt/tests/test_progiter.py::test_progiter_offset_10
    xdoctest ~/code/ubelt/tests/test_progiter.py test_progiter_offset_10
    """
    # Define a function that takes some time
    file = cStringIO()
    list(ProgIter(range(10), total=20, verbose=3, start=10, file=file,
                  freq=5, show_times=False))
    file.seek(0)
    want = ['10/20...', '15/20...', '20/20...']
    got = [line.strip() for line in file.readlines()]
    if sys.platform.startswith('win32'):  # nocover
        # on windows \r seems to be mixed up with ansi sequences
        from xdoctest.utils import strip_ansi
        got = [strip_ansi(line).strip() for line in got]
    print('want = {!r}'.format(want))
    print('got = {!r}'.format(got))
    assert got == want


def test_progiter_offset_0():
    """
    pytest -s  ~/code/ubelt/ubelt/tests/test_progiter.py::test_progiter_offset_0
    """
    # Define a function that takes some time
    file = cStringIO()
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


def time_progiter_overhead():
    # Time the overhead of this function
    import timeit
    import textwrap
    import ubelt as ub
    setup = textwrap.dedent(
        '''
        from sklearn.externals.progiter import ProgIter
        import numpy as np
        import time
        from six.moves import cStringIO, range
        import utool as ut
        N = 500
        file = cStringIO()
        rng = np.random.RandomState(42)
        ndims = 2
        vec1 = rng.rand(113, ndims)
        vec2 = rng.rand(71, ndims)

        def minimal_wraper1(sequence):
            for item in sequence:
                yield item

        def minimal_wraper2(sequence):
            for count, item in enumerate(sequence, start=1):
                yield item

        def minimal_wraper3(sequence):
            count = 0
            for item in sequence:
                yield item
                count += 1

        def minwrap4(sequence):
            for count, item in enumerate(sequence, start=1):
                yield item
                if count % 100:
                    pass

        def minwrap5(sequence):
            for count, item in enumerate(sequence, start=1):
                yield item
                if time.time() < 100:
                    pass
        '''
    )
    statements = {
        'baseline'       : '[{work} for n in range(N)]',
        'creation'       : 'ProgIter(range(N))',
        'minwrap1'       : '[{work} for n in minimal_wraper1(range(N))]',
        'minwrap2'       : '[{work} for n in minimal_wraper2(range(N))]',
        'minwrap3'       : '[{work} for n in minimal_wraper3(range(N))]',
        'minwrap4'       : '[{work} for n in minwrap4(range(N))]',
        'minwrap5'       : '[{work} for n in minwrap5(range(N))]',
        '(sk-disabled)'  : '[{work} for n in ProgIter(range(N), enabled=False, file=file)]',  # NOQA
        '(sk-plain)'     : '[{work} for n in ProgIter(range(N), file=file)]',  # NOQA
        '(sk-freq)'      : '[{work} for n in ProgIter(range(N), file=file, freq=100)]',  # NOQA
        '(sk-no-adjust)' : '[{work} for n in ProgIter(range(N), file=file, adjust=False, freq=200)]',  # NOQA
        '(sk-high-freq)' : '[{work} for n in ProgIter(range(N), file=file, adjust=False, freq=200)]',  # NOQA

        # '(ut-disabled)'  : '[{work} for n in ut.ProgIter(range(N), enabled=False, file=file)]',    # NOQA
        # '(ut-plain)'     : '[{work} for n in ut.ProgIter(range(N), file=file)]',  # NOQA
        # '(ut-freq)'      : '[{work} for n in ut.ProgIter(range(N), freq=100, file=file)]',  # NOQA
        # '(ut-no-adjust)' : '[{work} for n in ut.ProgIter(range(N), freq=200, adjust=False, file=file)]',  # NOQA
        # '(ut-high-freq)' : '[{work} for n in ut.ProgIter(range(N), file=file, adjust=False, freq=200)]',  # NOQA
    }
    # statements = {
    #     'calc_baseline': '[vec1.dot(vec2.T) for n in range(M)]',  # NOQA
    #     'calc_plain': '[vec1.dot(vec2.T) for n in ProgIter(range(M), file=file)]',  # NOQA
    #     'calc_plain_ut': '[vec1.dot(vec2.T) for n in ut.ProgIter(range(M), file=file)]',  # NOQA
    # }
    timeings = {}

    work_strs = [
        'None',
        'vec1.dot(vec2.T)',
        'n % 10 == 0',
    ]
    work = work_strs[0]
    # work = work_strs[1]

    number = 10000
    prog = ub.ProgIter(desc='timing', adjust=True)
    for key, stmt in prog(statements.items()):
        prog.set_extra(key)
        secs = timeit.timeit(stmt.format(work=work), setup, number=number)
        timeings[key] = secs / number

    # import utool as ut
    # print(ut.align(ut.repr4(timeings, precision=8), ':'))


def test_unknown_total():
    """
    Make sure a question mark is printed if the total is unknown
    """
    iterable = (_ for _ in range(0, 10))
    file = cStringIO()
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
    file = cStringIO()
    prog = ProgIter(initial=9001, file=file, show_times=False, clearline=False)
    message = prog.format_message()
    assert strip_ansi(message) == ' 9001/?... \n'


def test_clearline():
    """
    Make sure a question mark is printed if the total is unknown

    pytest ubelt/tests/test_progiter.py::test_clearline
    """
    file = cStringIO()
    # Clearline=False version should simply have a newline at the end.
    prog = ProgIter(file=file, show_times=False, clearline=False)
    message = prog.format_message()
    assert strip_ansi(message).strip(' ') == '0/?... \n'
    # Clearline=True version should carrage return at the begining and have no
    # newline at the end.
    prog = ProgIter(file=file, show_times=False, clearline=True)
    message = prog.format_message()
    assert strip_ansi(message).strip(' ') == '\r    0/?...'


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
    prog = ProgIter(range(20), enabled=True, eta_window=None)

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
    assert prog.freq == 1

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

    import ubelt as ub
    with ub.CaptureStdout() as cap:
        ProgIter.write('foo')
    assert cap.text.strip() == 'foo'

    with ub.CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_description('new desc', refresh=False)
        prog.begin()
        prog.refresh()
        prog.close()
    assert prog.label == 'new desc'
    assert 'new desc' in cap.text.strip()

    with ub.CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_description('new desc', refresh=True)
        prog.close()
    assert prog.label == 'new desc'
    assert 'new desc' in cap.text.strip()

    with ub.CaptureStdout() as cap:
        prog = ProgIter(show_times=False)
        prog.set_description_str('new desc')
        prog.begin()
        prog.refresh()
        prog.close()
    assert prog.label == 'new desc'
    assert 'new desc' in cap.text.strip()

    import ubelt as ub
    with ub.CaptureStdout() as cap:
        prog = ub.ProgIter(show_times=False)
        prog.set_postfix({'foo': 'bar'}, baz='biz', x=object(), y=2)
        prog.begin()
    assert prog.length is None
    assert 'foo=bar' in cap.text.strip()
    assert 'baz=biz' in cap.text.strip()
    assert 'y=2' in cap.text.strip()
    assert 'x=<object' in cap.text.strip()

    import ubelt as ub
    with ub.CaptureStdout() as cap:
        prog = ub.ProgIter(show_times=False)
        prog.set_postfix_str('bar baz', refresh=False)
    assert 'bar baz' not in cap.text.strip()


if __name__ == '__main__':
    r"""
    CommandLine:
        pytest ubelt/tests/test_progiter.py
    """
    import pytest
    pytest.main([__file__])
