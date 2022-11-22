"""
Introduces the :class:`Executor` class that wraps the standard
ThreadPoolExecutor, ProcessPoolExecutor, and the new SerialExecutor with a
common interface and a configurable backend. This makes is easy to test if your
code benefits from parallism, how much it benefits, and gives you the ability
to disable if if you need to.


The :class:`Executor` class lets you choose the right level of concurrency
(which might be no concurrency). An excellent blog post on when to use
threads, processes, or asyncio [ChooseTheRightConcurrency]_.

Note that executor does not currently support asyncio, but this might be a
feature added in the future, but its unclear how interoperable this would be.

References:
    .. [ChooseTheRightConcurrency] https://superfastpython.com/python-concurrency-choose-api/


Example:
    >>> # xdoctest: +SKIP
    >>> # Note: while this works in IPython, this does not work when running
    >>> # in xdoctest. https://github.com/Erotemic/xdoctest/issues/101
    >>> # xdoctest: +REQUIRES(module:timerit)
    >>> # Does my function benefit from parallelism?
    >>> def my_function(arg1, arg2):
    ...     return (arg1 + arg2) * 3
    >>> #
    >>> def run_process(inputs, mode='serial', max_workers=0):
    ...     from concurrent.futures import as_completed
    ...     import ubelt as ub
    ...     # The executor interface is the same regardless of modes
    ...     executor = ub.Executor(mode=mode, max_workers=max_workers)
    ...     # submit returns a Future object
    ...     jobs = [executor.submit(my_function, *args) for args in inputs]
    ...     # future objects will contain results when they are done
    ...     results = [job.result() for job in as_completed(jobs)]
    ...     return results
    >>> # The same code tests our method in serial, thread, or process mode
    >>> import timerit
    >>> ti = timerit.Timerit(100, bestof=10, verbose=2)
    >>> # Setup test data
    >>> import random
    >>> rng = random.Random(0)
    >>> max_workers = 4
    >>> inputs = [(rng.random(), rng.random()) for _ in range(100)]
    >>> for mode in ['serial', 'process', 'thread']:
    >>>     for timer in ti.reset('mode={} max_workers={}'.format(mode, max_workers)):
    >>>         with timer:
    >>>             run_process(inputs, mode=mode, max_workers=max_workers)
    >>> print(ub.repr2(ti))

"""
import concurrent.futures
from concurrent.futures import as_completed

__all__ = ['Executor', 'JobPool']


class SerialFuture(concurrent.futures.Future):
    """
    Non-threading / multiprocessing version of future for drop in compatibility
    with concurrent.futures.
    """
    def __init__(self, func, *args, **kw):
        super(SerialFuture, self).__init__()
        self.func = func
        self.args = args
        self.kw = kw
        # self._condition = FakeCondition()
        self._run_count = 0
        # fake being finished to cause __get_result to be called
        self._state = concurrent.futures._base.FINISHED

    def _run(self):
        result = self.func(*self.args, **self.kw)
        self.set_result(result)
        self._run_count += 1

    def set_result(self, result):
        """
        Overrides the implementation to revert to pre python3.8 behavior

        Example:
            >>> # Just for coverage
            >>> from ubelt.util_futures import SerialFuture  # NOQA
            >>> self = SerialFuture(print, 'arg1', 'arg2')
            >>> self.add_done_callback(lambda x: print('done callback got x = {}'.format(x)))
            >>> print('result() before set_result()')
            >>> ret = self.result()
            >>> print('ret = {!r}'.format(ret))
            >>> self.set_result(1)
            >>> ret = self.result()
            >>> print('ret = {!r}'.format(ret))
            >>> #
            >>> print('set_result() before result()')
            >>> self = SerialFuture(print, 'arg1', 'arg2')
            >>> self.add_done_callback(lambda x: print('done callback got x = {}'.format(x)))
            >>> self.set_result(1)
            >>> ret = self.result()
            >>> print('ret = {!r}'.format(ret))
        """
        with self._condition:
            self._result = result
            self._state = concurrent.futures._base.FINISHED
            # I'm cheating a little by not covering this.
            # Lets call it, cheating in good faith. *shifty eyes*
            # I don't know how to test it, and its not a critical pieces of the
            # library. Consider it a bug.  help wanted.
            for waiter in self._waiters:  # nocover
                waiter.add_result(self)
            self._condition.notify_all()
        self._invoke_callbacks()

    def _Future__get_result(self):
        # overrides private __getresult method
        if not self._run_count:
            self._run()
        return self._result


class SerialExecutor(object):
    """
    Implements the concurrent.futures API around a single-threaded backend

    Notes:
        When using the SerialExecutor, any timeout specified to the result will
        be ignored.

    Example:
        >>> from ubelt.util_futures import SerialExecutor  # NOQA
        >>> import concurrent.futures
        >>> with SerialExecutor() as executor:
        >>>     futures = []
        >>>     for i in range(100):
        >>>         f = executor.submit(lambda x: x + 1, i)
        >>>         futures.append(f)
        >>>     for f in concurrent.futures.as_completed(futures):
        >>>         assert f.result() > 0
        >>>     for i, f in enumerate(futures):
        >>>         assert i + 1 == f.result()
    """
    def __enter__(self):
        self.max_workers = 0
        return self

    def __exit__(self, ex_type, ex_value, tb):
        pass

    def submit(self, func, *args, **kw):
        """
        Submit a job to be executed later

        Returns:
            concurrent.futures.Future:
                a future representing the job
        """
        return SerialFuture(func, *args, **kw)

    def shutdown(self):
        """
        Ignored for the serial executor
        """
        pass

    def map(self, fn, *iterables, **kwargs):
        """Returns an iterator equivalent to map(fn, iter).

        Args:
            fn (Callable[..., Any]):
                A callable that will take as many arguments as there are passed
                iterables.

            timeout:
                This argument is ignored for SerialExecutor

            chunksize:
                This argument is ignored for SerialExecutor

        Yields:
            Any:
                equivalent to: map(func, *iterables) but the calls may be
                evaluated out-of-order.

        Raises:
            Exception: If fn(*args) raises for any values.

        Example:
            >>> from ubelt.util_futures import SerialExecutor  # NOQA
            >>> import concurrent.futures
            >>> import string
            >>> with SerialExecutor() as executor:
            ...     result_iter = executor.map(int, string.digits)
            ...     results = list(result_iter)
            >>> print('results = {!r}'.format(results))
            results = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        """
        kwargs.pop('chunksize', None)
        kwargs.pop('timeout', None)
        if len(kwargs) != 0:  # nocover
            raise ValueError('Unknown arguments {}'.format(kwargs))

        fs = [self.submit(fn, *args) for args in zip(*iterables)]
        for f in fs:
            yield f.result()


# class AsyncIOExecutor:
#     """
#     Mimic concurrent.futures with asyncio
#     This might not be possible. Defer...
#     Example:
#         from ubelt.util_futures import AsyncIOExecutor
#         self = executor = AsyncIOExecutor()
#         func = int
#         args = ('1',)
#         self.loop.run_in_executor(func, *args)
#         future = self.loop.run_in_executor(None, func, *args)
#     """
#     def __init__(self):
#         self.max_workers = 0
#         self.loop = None
#         import asyncio
#         try:
#             self.loop = asyncio.get_event_loop()
#         except RuntimeError:
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             self.loop = asyncio.get_event_loop()
#     def __enter__(self):
#         return self
#     def __exit__(self, ex_type, ex_value, tb):
#         pass
#     def submit(self, func, *args, **kw):
#         ...
#     def shutdown(self):
#         ...
#     def map(self, fn, *iterables, **kwargs):
#         ...


class Executor(object):
    """
    Wrapper around a specific executor.

    Abstracts Serial, Thread, and Process Executor via arguments.

    Args:
        mode (str, default='thread'): either thread, serial, or process
        max_workers (int, default=0): number of workers. If 0, serial is forced.

    Example:
        >>> import platform
        >>> import sys
        >>> # The process backend breaks pyp3 when using coverage
        >>> if 'pypy' in platform.python_implementation().lower():
        ...     import pytest
        ...     pytest.skip('not testing process on pypy')
        >>> if sys.platform.startswith('win32'):
        ...     import pytest
        ...     pytest.skip('not running this test on win32 for now')
        >>> import ubelt as ub
        >>> # Fork before threading!
        >>> # https://pybay.com/site_media/slides/raymond2017-keynote/combo.html
        >>> self1 = ub.Executor(mode='serial', max_workers=0)
        >>> self1.__enter__()
        >>> self2 = ub.Executor(mode='process', max_workers=2)
        >>> self2.__enter__()
        >>> self3 = ub.Executor(mode='thread', max_workers=2)
        >>> self3.__enter__()
        >>> jobs = []
        >>> jobs.append(self1.submit(sum, [1, 2, 3]))
        >>> jobs.append(self1.submit(sum, [1, 2, 3]))
        >>> jobs.append(self2.submit(sum, [10, 20, 30]))
        >>> jobs.append(self2.submit(sum, [10, 20, 30]))
        >>> jobs.append(self3.submit(sum, [4, 5, 5]))
        >>> jobs.append(self3.submit(sum, [4, 5, 5]))
        >>> for job in jobs:
        >>>     result = job.result()
        >>>     print('result = {!r}'.format(result))
        >>> self1.__exit__(None, None, None)
        >>> self2.__exit__(None, None, None)
        >>> self3.__exit__(None, None, None)

    Example:
        >>> import ubelt as ub
        >>> self1 = ub.Executor(mode='serial', max_workers=0)
        >>> with self1:
        >>>     jobs = []
        >>>     for i in range(10):
        >>>         jobs.append(self1.submit(sum, [i + 1, i]))
        >>>     for job in jobs:
        >>>         job.add_done_callback(lambda x: print('done callback got x = {}'.format(x)))
        >>>         result = job.result()
        >>>         print('result = {!r}'.format(result))
    """

    def __init__(self, mode='thread', max_workers=0):
        from concurrent import futures
        if mode == 'serial' or max_workers == 0:
            backend = SerialExecutor()
        elif mode == 'thread':
            backend = futures.ThreadPoolExecutor(max_workers=max_workers)
        elif mode == 'process':
            backend = futures.ProcessPoolExecutor(max_workers=max_workers)
        # elif mode == 'asyncio':
        #     # Experimental
        #     backend = AsyncIOExecutor()
        else:
            raise KeyError(mode)
        self.backend = backend

    def __enter__(self):
        self.backend.__enter__()
        return self

    def __exit__(self, ex_type, ex_value, tb):
        return self.backend.__exit__(ex_type, ex_value, tb)

    def submit(self, func, *args, **kw):
        """
        Calls the submit function of the underlying backend.

        Returns:
            concurrent.futures.Future:
                a future representing the job
        """
        return self.backend.submit(func, *args, **kw)

    def shutdown(self):
        """
        Calls the shutdown function of the underlying backend.
        """
        return self.backend.shutdown()

    def map(self, fn, *iterables, **kwargs):
        """
        Calls the map function of the underlying backend.

        CommandLine:
            xdoctest -m ubelt.util_futures Executor.map

        Example:
            >>> import ubelt as ub
            >>> import concurrent.futures
            >>> import string
            >>> with ub.Executor(mode='serial') as executor:
            ...     result_iter = executor.map(int, string.digits)
            ...     results = list(result_iter)
            >>> print('results = {!r}'.format(results))
            results = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            >>> with ub.Executor(mode='thread', max_workers=2) as executor:
            ...     result_iter = executor.map(int, string.digits)
            ...     results = list(result_iter)
            >>> # xdoctest: +IGNORE_WANT
            >>> print('results = {!r}'.format(results))
            results = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        """
        # Hack for python2
        chunksize = kwargs.pop('chunksize', 1)
        timeout = kwargs.pop('timeout', None)
        if len(kwargs) != 0:  # nocover
            raise ValueError('Unknown arguments {}'.format(kwargs))
        return self.backend.map(fn, *iterables, timeout=timeout,
                                chunksize=chunksize)


class JobPool(object):
    """
    Abstracts away boilerplate of submitting and collecting jobs

    This is a basic wrapper around :class:`ubelt.util_futures.Executor` that
    simplifies the most basic case.

    Example:
        >>> import ubelt as ub
        >>> def worker(data):
        >>>     return data + 1
        >>> pool = ub.JobPool('thread', max_workers=16)
        >>> for data in ub.ProgIter(range(10), desc='submit jobs'):
        >>>     pool.submit(worker, data)
        >>> final = []
        >>> for job in pool.as_completed(desc='collect jobs'):
        >>>     info = job.result()
        >>>     final.append(info)
        >>> print('final = {!r}'.format(final))
    """
    def __init__(self, mode='thread', max_workers=0):
        self.executor = Executor(mode=mode, max_workers=max_workers)
        self.jobs = []

    def __len__(self):
        return len(self.jobs)

    def submit(self, func, *args, **kwargs):
        """
        Submit a job managed by the pool

        Args:
            func (Callable[..., Any]):
                A callable that will take as many arguments as there are passed
                iterables.

            *args : positional arguments to pass to the function

            *kwargs : keyword arguments to pass to the function

        Returns:
            concurrent.futures.Future:
                a future representing the job
        """
        job = self.executor.submit(func, *args, **kwargs)
        self.jobs.append(job)
        return job

    def shutdown(self):
        self.jobs = None
        return self.executor.shutdown()

    def __enter__(self):
        self.executor.__enter__()
        return self

    def __exit__(self, a, b, c):
        self.executor.__exit__(a, b, c)

    # TODO: add some way to clear completed jobs?
    # def clear_completed

    def as_completed(self, timeout=None, desc=None, progkw=None):
        """
        Generates completed jobs in an arbitrary order

        Args:
            timeout (float | None):
                Specify the the maximum number of seconds to wait for a job.
                Note: this is ignored in serial mode.

            desc (str | None):
                if specified, reports progress with a
                :class:`ubelt.progiter.ProgIter` object.

            progkw (dict | None):
                extra keyword arguments to :class:`ubelt.progiter.ProgIter`.

        Yields:
            concurrent.futures.Future:
                The completed future object containing the results of a job.

        CommandLine:
            xdoctest -m ubelt.util_futures JobPool.as_completed

        Example:
            >>> import ubelt as ub
            >>> pool = ub.JobPool('thread', max_workers=8)
            >>> text = ub.paragraph(
            ...     '''
            ...     UDP is a cool protocol, check out the wiki:
            ...
            ...     UDP-based Data Transfer Protocol (UDT), is a high-performance
            ...     data transfer protocol designed for transferring large
            ...     volumetric datasets over high-speed wide area networks. Such
            ...     settings are typically disadvantageous for the more common TCP
            ...     protocol.
            ...     ''')
            >>> for word in text.split(' '):
            ...     pool.submit(print, word)
            >>> for _ in pool.as_completed():
            ...     pass
            >>> pool.shutdown()
        """
        import ubelt as ub
        job_iter = as_completed(self.jobs, timeout=timeout)
        if desc is not None:
            if progkw is None:
                progkw = {}
            job_iter = ub.ProgIter(
                job_iter, desc=desc, total=len(self.jobs), **progkw)
            self._prog = job_iter
        for job in job_iter:
            yield job

    def join(self, **kwargs):
        """
        Like :func:`JobPool.as_completed`, but executes the `result` method
        of each future and returns only after all processes are complete.
        This allows for lower-boilerplate prototyping.

        Args:
            **kwargs: passed to :func:`JobPool.as_completed`

        Returns:
            List[Any]: list of results

        Example:
            >>> import ubelt as ub
            >>> # We just want to try replacing our simple iterative algorithm
            >>> # with the embarassingly parallel version
            >>> arglist = list(zip(range(1000), range(1000)))
            >>> func = ub.identity
            >>> #
            >>> # Original version
            >>> for args in arglist:
            >>>     func(*args)
            >>> #
            >>> # Potentially parallel version
            >>> jobs = ub.JobPool(max_workers=0)
            >>> for args in arglist:
            >>>     jobs.submit(func, *args)
            >>> _ = jobs.join(desc='running')
        """
        results = []
        for job in self.as_completed(**kwargs):
            result = job.result()
            results.append(result)
        return results

    def __iter__(self):
        """
        An alternative to as completed

        Example:
            >>> import ubelt as ub
            >>> pool = ub.JobPool('serial')
            >>> assert len(list(iter(pool))) == 0
            >>> pool.submit(print, 'hi')
            >>> assert len(list(iter(pool))) == 1
        """
        for job in self.as_completed():
            yield job
