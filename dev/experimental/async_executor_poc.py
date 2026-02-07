"""
Attempt to allow ubelt.Executor to use Pythons builtin async / await


Goal:
    be able to put ub.Executor in asyncio mode, which lets it coorporative
    scheduling.
"""

import asyncio
import concurrent.futures
import types

# async def _async_worker(executor_reference, work_queue, initializer=None, initargs=None):
#     if initializer is not None:
#         try:
#             initializer(*initargs)
#         except BaseException:
#             _base.LOGGER.critical('Exception in initializer:', exc_info=True)
#             executor = executor_reference()
#             if executor is not None:
#                 executor._initializer_failed()
#             return
#     try:
#         while True:
#             work_item = work_queue.get(block=True)
#             if work_item is not None:
#                 work_item.run()
#                 # Delete references to object. See issue16284
#                 del work_item

#                 # attempt to increment idle count
#                 executor = executor_reference()
#                 if executor is not None:
#                     executor._idle_semaphore.release()
#                 del executor
#                 continue

#             executor = executor_reference()
#             # Exit if:
#             #   - The interpreter is shutting down OR
#             #   - The executor that owns the worker has been collected OR
#             #   - The executor that owns the worker has been shutdown.
#             if _shutdown or executor is None or executor._shutdown:
#                 # Flag the executor as shutting down as early as possible if it
#                 # is not gc-ed yet.
#                 if executor is not None:
#                     executor._shutdown = True
#                 # Notice other workers
#                 work_queue.put(None)
#                 return
#             del executor
#     except BaseException:
#         _base.LOGGER.critical('Exception in worker', exc_info=True)


async def _async_call(func, *args, **kwargs):
    return func(*args, **kwargs)


class AsyncIOExecutor:
    """
    Mimic concurrent.futures with asyncio
    This might not be possible. Defer...
    """

    def __init__(self):
        self.max_workers = 0
        self.loop = None
        self._work_queue = asyncio.Queue()
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loop = asyncio.get_event_loop()

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback): ...

    def submit(self, fn, /, *args, **kwargs):
        coroutine = _async_call(fn, *args, **kwargs)
        task = self.loop.create_task(coroutine)
        return FakeFuture(task, self)

        # with self._shutdown_lock, _global_shutdown_lock:
        # if self._broken:
        #     raise BrokenThreadPool(self._broken)

        # if self._shutdown:
        #     raise RuntimeError('cannot schedule new futures after shutdown')
        # if _shutdown:
        #     raise RuntimeError('cannot schedule new futures after '
        #                        'interpreter shutdown')
        # f = _AsyncFuture()
        # w = _AsyncWorkItem(f, fn, args, kwargs)
        # self._work_queue.put(w)
        # self._adjust_thread_count()
        # return f
        # return task

    def shutdown(self): ...

    def map(self, fn, *iterables, **kwargs):
        kwargs.pop('chunksize', None)
        kwargs.pop('timeout', None)
        if len(kwargs) != 0:  # nocover
            raise ValueError('Unknown arguments {}'.format(kwargs))
        fs = [self.submit(fn, *args) for args in zip(*iterables)]
        for f in fs:
            yield f.result()


class FakeFuture:
    def __init__(self, task, executor):
        self.task = task
        self.executor = executor

    def result(self):
        return self.executor.loop.run_until_complete(self.task)


class _AsyncWorkItem:
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            self.future.set_exception(exc)
            # Break a reference cycle with the exception 'exc'
            self = None
        else:
            self.future.set_result(result)

    __class_getitem__ = classmethod(types.GenericAlias)


class _AsyncFuture(concurrent.futures.Future):
    """
    Non-threading / multiprocessing version of future for drop in compatibility
    with concurrent.futures.

    Attributes:
        func (Callable): function to be called
        args (Tuple): positional arguments to call the function with
        kw (Dict): keyword arguments to call the function with
    """

    def __init__(self, func, *args, **kw):
        super(_AsyncFuture, self).__init__()
        # self.func = func
        # self.args = args
        # self.kw = kw
        # # self._condition = FakeCondition()
        # self._run_count = 0
        # # fake being finished to cause __get_result to be called
        # self._state = concurrent.futures._base.FINISHED

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


async def expensive_async_call():
    import asyncio
    import random

    time = random.randint(0, 10)
    sleep_coroutine = asyncio.sleep(time)
    return await sleep_coroutine


GLOBAL_COUNTER = 0


def my_function(arg):
    import asyncio
    import random
    import time

    import kwutil

    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1

    duration = random.random() * 1
    time.sleep(duration)

    now = kwutil.datetime.now()
    snapshot = int(GLOBAL_COUNTER)
    result = {'arg': arg, 'rank': snapshot, 'time': now, 'duration': duration}
    return result


def devcheck():
    import ubelt as ub

    self = ub.Executor(mode='thread', max_workers=10)
    self = AsyncIOExecutor()

    futures = []
    for i in ub.ProgIter(range(10), desc='submit'):
        future = self.submit(my_function, i)
        futures.append(future)

    self.loop.run_until_complete()

    with ub.Timer(label='collecting'):
        total = 0
        for future in futures:
            result = future.result()
            print(result)
            total += result['duration']
    print(f'total={total}')

    # future = async_call(func, *args)
    # import asyncio
    # loop = asyncio.get_event_loop()

    # self.loop.run_in_executor(func, *args)
    # future = self.loop.run_in_executor(None, func, *args)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/experimental/async_executor_poc.py
    """
    devcheck()
