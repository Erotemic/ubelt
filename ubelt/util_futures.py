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

    Attributes:
        func (Callable): function to be called
        args (Tuple): positional arguments to call the function with
        kw (Dict): keyword arguments to call the function with
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


# Rename to SerialPoolExecutor?
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

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        return False

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
#     def __exit__(self, ex_type, ex_value, ex_traceback):
#         ...
#     def submit(self, func, *args, **kw):
#         ...
#     def shutdown(self):
#         ...
#     def map(self, fn, *iterables, **kwargs):
#         ...


class Executor(object):
    """
    A concrete asynchronous executor with a configurable backend.

    The type of parallelism (or lack thereof) is configured via the ``mode``
    parameter, which can be: "process", "thread", or "serial".  This allows the
    user to easily enable / disable parallelism or switch between processes and
    threads without modifying the surrounding logic.

    SeeAlso:
        * :class:`concurrent.futures.ThreadPoolExecutor`
        * :class:`concurrent.futures.ProcessPoolExecutor`
        * :class:`SerialExecutor`
        * :class:`JobPool`

    In the case where you cant or dont want to use ubelt.Executor you can get
    similar behavior with the following pure-python snippet:

    .. code:: python

        def Executor(max_workers):
            # Stdlib-only "ubelt.Executor"-like behavior
            if max_workers == 1:
                import contextlib
                def submit_partial(func, *args, **kwargs):
                    def wrapper():
                        return func(*args, **kwargs)
                    wrapper.result = wrapper
                    return wrapper
                executor = contextlib.nullcontext()
                executor.submit = submit_partial
            else:
                from concurrent.futures import ThreadPoolExecutor
                executor = ThreadPoolExecutor(max_workers=max_workers)
            return executor

        executor = Executor(0)
        with executor:
            jobs = []

            for arg in range(1000):
                job = executor.submit(chr, arg)
                jobs.append(job)

            results = []
            for job in jobs:
                result = job.result()
                results.append(result)

        print('results = {}'.format(ub.urepr(results, nl=1)))


    Attributes:
        backend (SerialExecutor | ThreadPoolExecutor | ProcessPoolExecutor):

    Example:
        >>> import ubelt as ub
        >>> # Prototype code using simple serial processing
        >>> executor = ub.Executor(mode='serial', max_workers=0)
        >>> jobs = [executor.submit(sum, [i + 1, i]) for i in range(10)]
        >>> print([job.result() for job in jobs])
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

        >>> # Enable parallelism by only changing one parameter
        >>> executor = ub.Executor(mode='process', max_workers=0)
        >>> jobs = [executor.submit(sum, [i + 1, i]) for i in range(10)]
        >>> print([job.result() for job in jobs])
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    """

    def __init__(self, mode='thread', max_workers=0):
        """
        Args:
            mode (str):
                The backend parallelism mechanism.  Can be either thread, serial,
                or process. Defaults to 'thread'.

            max_workers (int):
                number of workers. If 0, serial is forced. Defaults to 0.
        """
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

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        # Note: the following call will block
        return self.backend.__exit__(ex_type, ex_value, ex_traceback)

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
    simplifies the most basic case by 1. keeping track of references to
    submitted futures for you and 2. providing an as_completed method to
    consume those futures as they are ready.

    Attributes:
        executor (Executor): internal executor object
        jobs (List[Future]): internal job list. Note: do not rely on this attribute, it
            may change in the future.

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
    def __init__(self, mode='thread', max_workers=0, transient=False):
        """
        Args:
            mode (str):
                The backend parallelism mechanism.  Can be either thread, serial,
                or process. Defaults to 'thread'.

            max_workers (int):
                number of workers. If 0, serial is forced. Defaults to 0.

            transient (bool):
                if True, references to jobs will be discarded as they are
                returned by :func:`as_completed`. Otherwise the ``jobs`` attribute
                holds a reference to all jobs ever submitted. Default to False.
        """
        self.executor = Executor(mode=mode, max_workers=max_workers)
        self.transient = transient
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

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        return self.executor.__exit__(ex_type, ex_value, ex_traceback)

    def _clear_completed(self):
        active_jobs = [job for job in self.jobs if job.running()]
        self.jobs = active_jobs

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
        from ubelt.progiter import ProgIter
        job_iter = as_completed(self.jobs, timeout=timeout)
        if desc is not None:
            if progkw is None:
                progkw = {}
            job_iter = ProgIter(
                job_iter, desc=desc, total=len(self.jobs), **progkw)
            self._prog = job_iter
        for job in job_iter:
            if self.transient:
                # Maybe keep a reference to the job index and then null it out
                # in our job list? Should probably think about a good
                # implementation. See kwcoco.CocoDataset._load_multiple
                self.jobs.remove(job)
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
            >>> # with the embarrassingly parallel version
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
        An alternative to as completed.

        NOTE:
            The order of iteration may be changed in the future to be the
            submission order instead.

        Yields:
            concurrent.futures.Future:
                The completed future object containing the results of a job.

        Example:
            >>> import ubelt as ub
            >>> pool = ub.JobPool('serial')
            >>> assert len(list(iter(pool))) == 0
            >>> pool.submit(print, 'hi')
            >>> assert len(list(iter(pool))) == 1
        """
        for job in self.as_completed():
            yield job
