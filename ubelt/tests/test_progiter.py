# -*- coding: utf-8 -*-


def test_progiter():
    from six.moves import cStringIO
    from ubelt.progiter import ProgIter
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

    length = 1000
    N = 5000
    N0 = N - length
    print('N = %r' % (N,))
    print('N0 = %r' % (N0,))

    print('\n-----')
    print('Demo #0: progress can be disabled and incur essentially 0 overhead')
    print('However, the overhead of enabled progress is minimal and typically '
          'insignificant')
    print('this is verbosity mode verbose=0')
    iterable = (is_prime(n) for n in range(N0, N))
    with Timer('demo0'):
        piterable = ProgIter(iterable, length=length, label='demo0',
                             enabled=False)
        list(piterable)

    print('\n-----')
    print('Demo #1: progress is shown by default in the same line')
    print('this is verbosity mode verbose=1')
    iterable = (is_prime(n) for n in range(N0, N))
    with Timer('demo1'):
        piterable = ProgIter(iterable, length=length, label='demo1')
        list(piterable)

    # Default behavior adjusts frequency of progress reporting so
    # the performance of the loop is minimally impacted
    print('\n-----')
    print('Demo #2: clearline=False prints multiple lines.')
    print('Progress is only printed as needed')
    print('Notice the adjustment behavior of the print frequency')
    print('this is verbosity mode verbose=2')
    with Timer('demo2'):
        iterable = (is_prime(n) for n in range(N0, N))
        piterable = ProgIter(iterable, length=length, clearline=False,
                             label='demo2')
        list(piterable)
        # import utool as ut
        # print(ut.repr4(piterable.__dict__))

    print('\n-----')
    print('Demo #3: Adjustments can be turned off to give constant feedback')
    print('this is verbosity mode verbose=3')
    iterable = (is_prime(n) for n in range(N0, N))
    with Timer('demo3'):
        piterable = ProgIter(iterable, length=length, adjust=False,
                             clearline=False, freq=100, label='demo3')
        list(piterable)


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

        def minimal_wraper1(iterable):
            for item in iterable:
                yield item

        def minimal_wraper2(iterable):
            for count, item in enumerate(iterable, start=1):
                yield item

        def minimal_wraper3(iterable):
            count = 0
            for item in iterable:
                yield item
                count += 1

        def minwrap4(iterable):
            for count, item in enumerate(iterable, start=1):
                yield item
                if count % 100:
                    pass

        def minwrap5(iterable):
            for count, item in enumerate(iterable, start=1):
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
