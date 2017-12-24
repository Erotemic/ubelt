# -*- coding: utf-8 -*-
"""
pytest ubelt/tests/test_progiter.py
"""
from six.moves import cStringIO
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
    stream = cStringIO()
    prog = ub.ProgIter(stream=stream)
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
        stream = cStringIO()
        prog = ProgIter(range(N), clearline=False, stream=stream, freq=N // 10,
                        adjust=False)
        stream.seek(0)
        print(stream.read())

        prog = ProgIter(range(N), clearline=False)
        for n in prog:
            was_prime = is_prime(n)
            prog.set_extra('n=%r, was_prime=%r' % (n, was_prime,))
            if (n + 1) % 128 == 0 and was_prime:
                prog.set_extra('n=%r, was_prime=%r EXTRA' % (n, was_prime,))
        stream.seek(0)
        print(stream.read())

    length = 200
    N = 5000
    N0 = N - length
    print('N = %r' % (N,))
    print('N0 = %r' % (N0,))

    print('\n-----')
    print('Demo #0: progress can be disabled and incur essentially 0 overhead')
    print('However, the overhead of enabled progress is minimal and typically '
          'insignificant')
    print('this is verbosity mode verbose=0')
    sequence = (is_prime(n) for n in range(N0, N))
    with Timer('demo0'):
        psequence = ProgIter(sequence, length=length, label='demo0',
                             enabled=False)
        list(psequence)

    print('\n-----')
    print('Demo #1: progress is shown by default in the same line')
    print('this is verbosity mode verbose=1')
    sequence = (is_prime(n) for n in range(N0, N))
    with Timer('demo1'):
        psequence = ProgIter(sequence, length=length, label='demo1')
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
        psequence = ProgIter(sequence, length=length, clearline=False,
                             label='demo2')
        list(psequence)
        # import utool as ut
        # print(ut.repr4(psequence.__dict__))

    print('\n-----')
    print('Demo #3: Adjustments can be turned off to give constant feedback')
    print('this is verbosity mode verbose=3')
    sequence = (is_prime(n) for n in range(N0, N))
    with Timer('demo3'):
        psequence = ProgIter(sequence, length=length, adjust=False,
                             clearline=False, freq=100, label='demo3')
        list(psequence)


def test_progiter_offset_10():
    """
    pytest -s  ~/code/ubelt/ubelt/tests/test_progiter.py::test_progiter_offset_10
    """
    # Define a function that takes some time
    stream = cStringIO()
    list(ProgIter(range(10), length=20, verbose=3, start=10, stream=stream,
                  freq=5, show_times=False))
    stream.seek(0)
    want = ['10/20...', '15/20...', '20/20...']
    got = [line.strip() for line in stream.readlines()]
    if sys.platform.startswith('win32'): # nocover
        # on windows \r seems to be mixed up with ansi sequences
        from xdoctest.utils import strip_ansi
        got = [strip_ansi(line).strip() for line in got]
    assert got == want


def test_progiter_offset_0():
    """
    pytest -s  ~/code/ubelt/ubelt/tests/test_progiter.py::test_progiter_offset_0
    """
    # Define a function that takes some time
    stream = cStringIO()
    for _ in ProgIter(range(10), length=20, verbose=3, start=0, stream=stream,
                      freq=5, show_times=False):
        pass
    stream.seek(0)
    want = ['0/20...', '5/20...', '10/20...']
    got = [line.strip() for line in stream.readlines()]
    if sys.platform.startswith('win32'): # nocover
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
        stream = cStringIO()
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
        '(sk-disabled)'  : '[{work} for n in ProgIter(range(N), enabled=False, stream=stream)]',  # NOQA
        '(sk-plain)'     : '[{work} for n in ProgIter(range(N), stream=stream)]',  # NOQA
        '(sk-freq)'      : '[{work} for n in ProgIter(range(N), stream=stream, freq=100)]',  # NOQA
        '(sk-no-adjust)' : '[{work} for n in ProgIter(range(N), stream=stream, adjust=False, freq=200)]',  # NOQA
        '(sk-high-freq)' : '[{work} for n in ProgIter(range(N), stream=stream, adjust=False, freq=200)]',  # NOQA

        # '(ut-disabled)'  : '[{work} for n in ut.ProgIter(range(N), enabled=False, stream=stream)]',    # NOQA
        # '(ut-plain)'     : '[{work} for n in ut.ProgIter(range(N), stream=stream)]',  # NOQA
        # '(ut-freq)'      : '[{work} for n in ut.ProgIter(range(N), freq=100, stream=stream)]',  # NOQA
        # '(ut-no-adjust)' : '[{work} for n in ut.ProgIter(range(N), freq=200, adjust=False, stream=stream)]',  # NOQA
        # '(ut-high-freq)' : '[{work} for n in ut.ProgIter(range(N), stream=stream, adjust=False, freq=200)]',  # NOQA
    }
    # statements = {
    #     'calc_baseline': '[vec1.dot(vec2.T) for n in range(M)]',  # NOQA
    #     'calc_plain': '[vec1.dot(vec2.T) for n in ProgIter(range(M), stream=stream)]',  # NOQA
    #     'calc_plain_ut': '[vec1.dot(vec2.T) for n in ut.ProgIter(range(M), stream=stream)]',  # NOQA
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
    prog = ub.ProgIter(label='timing', adjust=True)
    for key, stmt in prog(statements.items()):
        prog.set_extra(key)
        secs = timeit.timeit(stmt.format(work=work), setup, number=number)
        timeings[key] = secs / number

    # import utool as ut
    # print(ut.align(ut.repr4(timeings, precision=8), ':'))
