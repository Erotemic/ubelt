"""
Introduces the :class:`Executor` class that wraps the standard
ThreadPoolExecutor, ProcessPoolExecutor, and the new SerialExecutor with a
common interface and a configurable backend. This makes is easy to test if your
code benefits from parallelism, how much it benefits, and gives you the ability
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

from __future__ import annotations

import concurrent.futures
import threading
import typing
from concurrent.futures import as_completed
from typing import Protocol, cast

__all__ = ['Executor', 'JobPool']

T = typing.TypeVar('T')

if typing.TYPE_CHECKING:
    from concurrent.futures import (
        Future,
    )
    from types import TracebackType
    from typing import (
        Any,
        Callable,
        Generator,
        Iterable,
        Iterator,
        Type,
        cast,
    )

    class _ExecutorBackend(Protocol):
        def __enter__(self) -> Any: ...
        def __exit__(
            self,
            ex_type: Type[BaseException] | None,
            ex_value: BaseException | None,
            ex_traceback: TracebackType | None,
        ) -> bool | None: ...
        def submit(
            self,
            func: Callable[..., T],
            *args: Any,
            **kw: Any,
        ) -> concurrent.futures.Future[T]: ...
        def shutdown(self) -> None: ...
        def map(
            self,
            fn: Callable[..., T],
            *iterables: Iterable[Any],
            **kwargs: Any,
        ) -> Iterator[T]: ...
else:
    _ExecutorBackend = typing.Any


class SerialFuture(concurrent.futures.Future, typing.Generic[T]):
    """
    Non-threading / multiprocessing version of future for drop in compatibility
    with concurrent.futures.

    The callable is evaluated lazily the first time its result or exception is
    requested. Internally this future advertises a finished state so it remains
    compatible with :func:`concurrent.futures.as_completed`; the public future
    methods track whether the callable has actually been evaluated.

    Note:
        This remains a compatibility compromise, not a fully standard Future:
        ``concurrent.futures.wait()`` reads the internal finished state and
        can report a serial job as finished before ``done()`` returns True.
        The lazy behavior is retained for existing SerialExecutor callers;
        adopting eager evaluation would allow use of an ordinary Future. Initial
        evaluation is serialized when multiple threads request the same result.

    Example:
        >>> from ubelt.util_futures import SerialFuture
        >>> calls = []
        >>> future = SerialFuture(lambda: calls.append('run') or 5)
        >>> future.add_done_callback(lambda f: calls.append('callback'))
        >>> assert calls == []
        >>> assert future.result() == 5
        >>> assert future.result() == 5
        >>> assert calls == ['run', 'callback']
        >>> # An explicitly supplied result must not evaluate the callable.
        >>> future = SerialFuture(lambda: calls.append('unused'))
        >>> future.set_result(10)
        >>> assert future.result() == 10
        >>> assert 'unused' not in calls
        >>> # The old doctest attempted to overwrite the result; that is now
        >>> # rejected, matching Future's one-shot completion contract.
        >>> import concurrent.futures
        >>> import pytest
        >>> with pytest.raises(concurrent.futures.InvalidStateError):
        ...     future.set_result(11)

    TODO:
        warn if the user specifies timeout as we cannot handle it without
        threads

    Attributes:
        func (Callable): function to be called
        args (Tuple): positional arguments to call the function with
        kw (Dict): keyword arguments to call the function with
    """

    func: typing.Callable[..., T]
    args: tuple[typing.Any, ...]
    kw: dict[str, typing.Any]
    # Future initializes this list, but typeshed does not expose the attribute.
    _done_callbacks: list[
        typing.Callable[[concurrent.futures.Future[T]], typing.Any]
    ]

    def __init__(
        self, func: typing.Callable[..., T], *args: typing.Any, **kw: typing.Any
    ) -> None:
        super(SerialFuture, self).__init__()
        self.func = func
        self.args = args
        self.kw = kw
        self._run_count = 0
        # Keep the callable one-shot even if different threads request
        # result() and exception() simultaneously. Do not use _condition here:
        # callbacks may themselves inspect this future or involve other threads.
        self._evaluation_lock = threading.Lock()
        # as_completed() inspects Future._state rather than calling result().
        # Retain the legacy lazy executor behavior for 1.5, but document the
        # resulting wait()/done() mismatch above instead of claiming full
        # concurrent.futures compatibility.
        self._state = concurrent.futures._base.FINISHED

    def _run(self) -> None:
        if self._run_count:
            return
        with self._evaluation_lock:
            if self._run_count:
                return
            try:
                result = self.func(*self.args, **self.kw)
            except BaseException as ex:
                self.set_exception(ex)
            else:
                self.set_result(result)

    def result(self, timeout: float | None = None) -> T:
        """Evaluate the callable once, then return its result or raise."""
        # Evaluate outside Future.result's condition lock; the old private
        # _Future__get_result override ran user code while that lock was held.
        self._run()
        return super().result(timeout)

    def done(self) -> bool:
        """Return True once the serial callable has actually been evaluated."""
        with self._condition:
            return bool(self._run_count)

    def add_done_callback(
        self,
        fn: typing.Callable[[concurrent.futures.Future[T]], typing.Any],
    ) -> None:
        """Attach a callback that runs after actual serial evaluation."""
        with self._condition:
            if not self._run_count:
                self._done_callbacks.append(fn)
                return
        try:
            fn(self)
        except Exception:
            concurrent.futures._base.LOGGER.exception(
                'exception calling callback for %r', self
            )

    def exception(self, timeout: float | None = None) -> BaseException | None:
        """Evaluate the serial callable once and return its exception, if any."""
        self._run()
        return super().exception(timeout)

    def set_result(self, result: T) -> None:
        """
        Mark this serial future complete with ``result``.

        The original doctest exercised both call orders. Under the old
        implementation, calling ``set_result`` after ``result`` could
        overwrite the computed value and run callbacks again. Completion is
        now one-shot, consistent with ``concurrent.futures.Future``. The
        examples retain both orderings and check the updated contract.

        Example:
            >>> from ubelt.util_futures import SerialFuture
            >>> import concurrent.futures
            >>> # result() before set_result(): execute the pending callable.
            >>> events = []
            >>> self = SerialFuture(lambda: events.append('run') or 5)
            >>> self.add_done_callback(lambda f: events.append('callback'))
            >>> ret = self.result()
            >>> assert ret == 5
            >>> assert events == ['run', 'callback']
            >>> try:
            ...     self.set_result(1)
            ... except concurrent.futures.InvalidStateError:
            ...     pass
            ... else:
            ...     raise AssertionError('completed result was overwritten')
            >>> assert self.result() == 5
            >>> assert events == ['run', 'callback']
            >>> # set_result() before result(): bypass the pending callable.
            >>> events = []
            >>> self = SerialFuture(lambda: events.append('should not run'))
            >>> self.add_done_callback(lambda f: events.append('callback'))
            >>> self.set_result(1)
            >>> ret = self.result()
            >>> assert ret == 1
            >>> assert events == ['callback']
        """
        with self._condition:
            if self._run_count:
                raise concurrent.futures.InvalidStateError(
                    '{}: {!r}'.format(self._state, self)
                )
            self._result = result
            self._exception = None
            self._run_count = 1
            # I'm cheating a little by not covering this.
            # Lets call it, cheating in good faith. *shifty eyes*
            # I don't know how to test it, and its not a critical pieces of the
            # library. Consider it a bug.  help wanted.
            #
            # 1.5.0 review: this exception has NOT been resolved by the
            # SerialFuture refactor. The lazy future advertises FINISHED so
            # as_completed() normally won't attach private _waiters. Keep the
            # notification path, but revisit its coverage when redesigning
            # this Future's compatibility with wait()/as_completed().
            for waiter in self._waiters:  # nocover
                waiter.add_result(self)
            self._condition.notify_all()
        self._invoke_callbacks()  # type: ignore

    def set_exception(self, exception: BaseException | None) -> None:
        """Mark this serial future complete with ``exception``."""
        with self._condition:
            if self._run_count:
                raise concurrent.futures.InvalidStateError(
                    '{}: {!r}'.format(self._state, self)
                )
            self._exception = exception
            self._result = None
            self._run_count = 1
            # Same untested private-waiter path as set_result above.
            for waiter in self._waiters:  # nocover
                waiter.add_exception(self)
            self._condition.notify_all()
        self._invoke_callbacks()  # type: ignore


# Rename to SerialPoolExecutor?
class SerialExecutor:
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

    max_workers: int

    def __enter__(self) -> SerialExecutor:
        self.max_workers = 0
        return self

    def __exit__(
        self,
        ex_type: Type[BaseException] | None,
        ex_value: BaseException | None,
        ex_traceback: TracebackType | None,
    ) -> None:
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        return None

    def submit(
        self,
        func: Callable[..., T],
        *args: Any,
        **kw: Any,
    ) -> SerialFuture[T]:
        """
        Submit a job to be executed later

        Returns:
            concurrent.futures.Future:
                a future representing the job
        """
        return SerialFuture(func, *args, **kw)

    def shutdown(self) -> None:
        """
        Ignored for the serial executor
        """
        pass

    def map(
        self,
        fn: Callable[..., T],
        *iterables: Iterable[Any],
        **kwargs: Any,
    ) -> Generator[T, None, None]:
        """Returns an iterator equivalent to map(fn, iter).

        Args:
            fn (Callable[..., T]): Function to apply to items from `iterables`.

            *iterables (Iterable[Any]):
                One or more iterables supplying arguments to `fn`.

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


# See ../dev/experimental/async_executor_poc.py for
# work ona potential AsyncIOExecutor class


class Executor:
    """
    A concrete asynchronous executor with a configurable backend.

    The type of parallelism (or lack thereof) is configured via the ``mode``
    parameter, which can be: "process", "thread", or "serial".  This allows the
    user to easily enable / disable parallelism or switch between processes and
    threads without modifying the surrounding logic.

    SeeAlso:
        * :class:`concurrent.futures.ThreadPoolExecutor`
        * :class:`concurrent.futures.ProcessPoolExecutor`
        * :class:`concurrent.futures.InterpreterPoolExecutor`
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
        >>> executor = ub.Executor(mode='process', max_workers=2)
        >>> jobs = [executor.submit(sum, [i + 1, i]) for i in range(10)]
        >>> print([job.result() for job in jobs])
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

        >>> # In 3.14 the interpreter backend is available
        >>> import sys
        >>> if sys.version_info[0:2] >= (3, 14):
        >>>     executor = ub.Executor(mode='interpreter', max_workers=2)
        >>>     jobs = [executor.submit(sum, [i + 1, i]) for i in range(10)]
        >>>     results = [job.result() for job in jobs]
        >>>     assert results == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    """

    backend: _ExecutorBackend

    def __init__(self, mode: str = 'thread', max_workers: int = 0) -> None:
        """
        Args:
            mode (str):
                The backend parallelism mechanism.  Can be either thread, serial,
                or process. Defaults to 'thread'.

            max_workers (int):
                number of workers. If 0, serial is forced. Defaults to 0.
        """
        from concurrent import futures

        backend: _ExecutorBackend
        if mode == 'serial' or max_workers == 0:
            backend = SerialExecutor()
        elif mode == 'thread':
            backend = cast(
                _ExecutorBackend,
                futures.ThreadPoolExecutor(max_workers=max_workers),
            )
        elif mode == 'process':
            backend = cast(
                _ExecutorBackend,
                futures.ProcessPoolExecutor(max_workers=max_workers),
            )
        elif mode == 'interpreter':  # nocover
            # Requires 3.14+
            InterpreterPoolExecutor = getattr(
                futures, 'InterpreterPoolExecutor', None
            )
            if InterpreterPoolExecutor is None:
                raise RuntimeError(
                    "Executor(mode='interpreter') requires Python 3.14+"
                )
            backend = InterpreterPoolExecutor(max_workers=max_workers)
        # elif mode == 'asyncio':
        #     # Experimental
        #     backend = AsyncIOExecutor()
        else:
            raise KeyError(mode)
        self.backend = backend

    def __enter__(self) -> Executor:
        self.backend.__enter__()
        return self

    def __exit__(
        self,
        ex_type: Type[BaseException] | None,
        ex_value: BaseException | None,
        ex_traceback: TracebackType | None,
    ) -> bool | None:
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

    def submit(
        self,
        func: Callable[..., T],
        *args: Any,
        **kw: Any,
    ) -> concurrent.futures.Future[T]:
        """
        Calls the submit function of the underlying backend.

        Returns:
            concurrent.futures.Future:
                a future representing the job
        """
        return self.backend.submit(func, *args, **kw)

    def shutdown(self) -> None:
        """
        Calls the shutdown function of the underlying backend.
        """
        return self.backend.shutdown()

    def map(
        self,
        fn: Callable[..., T],
        *iterables: Iterable[Any],
        **kwargs: Any,
    ) -> Iterator[T]:
        """
        Calls the map function of the underlying backend.

        Args:
            fn (Callable[..., T]): Function to apply to items from `iterables`.
            *iterables (Iterable[Any]): One or more iterables supplying arguments to `fn`.
            **kwargs (Any): Supports:
                - chunksize (int): Chunk size hint for process-based backends.
                - timeout (float | None): Optional timeout in seconds.

        Returns:
            Iterator[T]: Iterator yielding results from applying `fn`.

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
        return self.backend.map(
            fn, *iterables, timeout=timeout, chunksize=chunksize
        )


class JobPool(typing.Generic[T]):
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

    executor: Executor
    jobs: list[Future[T]]
    transient: bool

    def __init__(
        self,
        mode: str = 'thread',
        max_workers: int = 0,
        transient: bool = False,
    ) -> None:
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

    def __len__(self) -> int:
        return len(self.jobs)

    def submit(
        self, func: Callable[..., T], *args: Any, **kwargs: Any
    ) -> concurrent.futures.Future[T]:
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

    def shutdown(self) -> None:
        self.jobs = []
        return self.executor.shutdown()

    def __enter__(self) -> JobPool[T]:
        self.executor.__enter__()
        return self

    def __exit__(
        self,
        ex_type: Type[BaseException] | None,
        ex_value: BaseException | None,
        ex_traceback: TracebackType | None,
    ) -> bool | None:
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        return self.executor.__exit__(ex_type, ex_value, ex_traceback)

    def _clear_completed(self) -> None:
        active_jobs = [job for job in self.jobs if job.running()]
        self.jobs = active_jobs

    def as_completed(
        self,
        timeout: float | None = None,
        desc: str | None = None,
        progkw: dict | None = None,
    ) -> Generator[concurrent.futures.Future[T], None, None]:
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

        job_iter: Iterable[concurrent.futures.Future[T]] = as_completed(
            self.jobs, timeout=timeout
        )
        if desc is not None:
            if progkw is None:
                progkw = {}
            job_iter = ProgIter(
                job_iter, desc=desc, total=len(self.jobs), **progkw
            )
            # adding types to ProgIter should make this not a problem
            self._prog = job_iter
        for job in job_iter:
            if self.transient:
                # Maybe keep a reference to the job index and then null it out
                # in our job list? Should probably think about a good
                # implementation. See kwcoco.CocoDataset._load_multiple
                self.jobs.remove(job)
            yield job

    def join(self, **kwargs: Any) -> list[T]:
        """
        Like :func:`JobPool.as_completed`, but executes the `result` method
        of each future and returns only after all processes are complete.
        This allows for lower-boilerplate prototyping.

        Args:
            **kwargs: passed to :func:`JobPool.as_completed`

        Returns:
            list[Any]: list of results

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

    def __iter__(self) -> Iterator[concurrent.futures.Future[T]]:
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
