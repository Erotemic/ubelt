# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
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
        """
        with self._condition:
            self._result = result
            self._state = concurrent.futures._base.FINISHED
            for waiter in self._waiters:
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

    Example:
        >>> from ubelt.util_futures import *  # NOQA
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
        return SerialFuture(func, *args, **kw)

    def shutdown(self):
        pass


class Executor(object):
    """
    Wrapper around a specific executor.

    Abstracts Serial, Thread, and Process Executor via arguments.

    Args:
        mode (str, default='thread'): either thread, serial, or process
        max_workers (int, default=0): number of workers. If 0, serial is forced.
    """

    def __init__(self, mode='thread', max_workers=0):
        from concurrent import futures
        if mode == 'serial' or max_workers == 0:
            backend = SerialExecutor()
        elif mode == 'thread':
            backend = futures.ThreadPoolExecutor(max_workers=max_workers)
        elif mode == 'process':
            backend = futures.ProcessPoolExecutor(max_workers=max_workers)
        else:
            raise KeyError(mode)
        self.backend = backend

    def __enter__(self):
        return self.backend.__enter__()

    def __exit__(self, ex_type, ex_value, tb):
        return self.backend.__exit__(ex_type, ex_value, tb)

    def submit(self, func, *args, **kw):
        return self.backend.submit(func, *args, **kw)

    def shutdown(self):
        return self.backend.shutdown()


class JobPool(object):
    """
    Abstracts away boilerplate of submitting and collecting jobs

    Example:
        >>> import ubelt as ub
        >>> def worker(data):
        >>>     return data + 1
        >>> pool = ub.JobPool('thread', max_workers=16)
        >>> with pool:
        >>>     for data in ub.ProgIter(range(10), desc='submit jobs'):
        >>>         job = pool.submit(worker, data)
        >>>     final = []
        >>>     for job in ub.ProgIter(pool.as_completed(), total=len(pool), desc='collect jobs'):
        >>>         info = job.result()
        >>>         final.append(info)
        >>> print('final = {!r}'.format(final))
    """
    def __init__(self, mode='thread', max_workers=0):
        self.executor = Executor(mode=mode, max_workers=max_workers)
        self.jobs = []

    def __len__(self):
        return len(self.jobs)

    def submit(self, func, *args, **kwargs):
        job = self.executor.submit(func, *args, **kwargs)
        self.jobs.append(job)
        return job

    def __enter__(self):
        self.executor.__enter__()
        return self

    def __exit__(self, a, b, c):
        self.executor.__exit__(a, b, c)

    def as_completed(self):
        for job in as_completed(self.jobs):
            yield job

    def __iter__(self):
        for job in self.as_completed():
            yield job
