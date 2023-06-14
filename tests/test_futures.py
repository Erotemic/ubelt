def test_job_pool_context_manager():
    import ubelt as ub

    def worker(data):
        return data + 1

    pool = ub.JobPool('thread', max_workers=16)
    with pool:

        for data in ub.ProgIter(range(10), desc='submit jobs'):
            pool.submit(worker, data)

        final = []
        for job in pool.as_completed(desc='collect jobs'):
            info = job.result()
            final.append(info)


def test_job_pool_as_completed_prog_args():
    import ubelt as ub

    def worker(data):
        return data + 1

    pool = ub.JobPool('thread', max_workers=1)

    for data in ub.ProgIter(range(10), desc='submit jobs'):
        pool.submit(worker, data)

    with ub.CaptureStdout() as cap:
        final = list(pool.as_completed(desc='collect jobs', progkw={'verbose': 3, 'time_thresh': 0}))

    print(f'cap.text={cap.text}')
    num_lines = len(cap.text.split('\n'))
    num_jobs = len(pool.jobs)
    assert num_lines > num_jobs

    print('final = {!r}'.format(final))
    pool.shutdown()


def test_executor_timeout():
    import pytest
    pytest.skip(
        'long test, demos that timeout does not work with SerialExecutor')

    import ubelt as ub
    import time
    from concurrent.futures import TimeoutError

    def long_job(n, t):
        for i in range(n):
            time.sleep(t)

    for mode in ['thread', 'process', 'serial']:
        executor = ub.Executor(mode=mode, max_workers=1)
        with executor:
            job = executor.submit(long_job, 10, 0.05)
            with ub.Timer() as timer:
                try:
                    job_result = job.result(timeout=0.01)
                except TimeoutError as ex:
                    ex_ = ex
                else:
                    print('job_result = {!r}'.format(job_result))
            print('timer.elapsed = {!r}'.format(timer.elapsed))
            print('ex_ = {!r}'.format(ex_))


def test_job_pool_clear_completed():
    import weakref
    import gc
    import ubelt as ub
    is_deleted = {}
    weak_futures = {}

    jobs = ub.JobPool(mode='process', max_workers=4)

    def make_finalizer(jobid):
        def _finalizer():
            is_deleted[jobid] = True
        return _finalizer

    def debug_referers():
        if 0:
            referers = ub.udict({})
            for jobid, ref in weak_futures.items():
                fs = ref()
                referers[jobid] = 0 if fs is None else len(gc.get_referrers(fs))
            print('is_deleted = {}'.format(ub.urepr(is_deleted, nl=1)))
            print('referers = {}'.format(ub.urepr(referers, nl=1)))

    for jobid in range(10):
        fs = jobs.submit(simple_worker, jobid)
        weak_futures[jobid] = weakref.ref(fs)
        is_deleted[jobid] = False
        weakref.finalize(fs, make_finalizer(jobid))
        del fs

    debug_referers()
    assert not any(is_deleted.values())

    for fs in jobs.as_completed():
        fs.result()

    debug_referers()
    assert not any(is_deleted.values())

    jobs._clear_completed()

    debug_referers()

    import platform
    if 'pypy' not in platform.python_implementation().lower():
        if not any(is_deleted.values()):
            raise AssertionError

    fs = None

    if 'pypy' not in platform.python_implementation().lower():
        if not all(is_deleted.values()):
            raise AssertionError


def simple_worker(jobid):
    return jobid


def test_job_pool_transient():
    import weakref
    import ubelt as ub
    is_deleted = {}
    weak_futures = {}

    jobs = ub.JobPool(mode='process', max_workers=4, transient=True)

    def make_finalizer(jobid):
        def _finalizer():
            is_deleted[jobid] = True
        return _finalizer

    for jobid in range(10):
        fs = jobs.submit(simple_worker, jobid)
        weak_futures[jobid] = weakref.ref(fs)
        is_deleted[jobid] = False
        weakref.finalize(fs, make_finalizer(jobid))

    if any(is_deleted.values()):
        raise AssertionError

    for fs in jobs.as_completed():
        fs.result()

    # For 3.6, pytest has an AST issue if and assert statements are used.
    # raising regular AssertionErrors to handle that.
    import platform
    if 'pypy' not in platform.python_implementation().lower():
        if not any(is_deleted.values()):
            raise AssertionError

    fs = None

    if 'pypy' not in platform.python_implementation().lower():
        if not all(is_deleted.values()):
            raise AssertionError


def test_backends():
    import platform
    import sys
    # The process backend breaks pyp3 when using coverage
    if 'pypy' in platform.python_implementation().lower():
        import pytest
        pytest.skip('not testing process on pypy')
    if sys.platform.startswith('win32'):
        import pytest
        pytest.skip('not running this test on win32 for now')
    import ubelt as ub
    # Fork before threading!
    # https://pybay.com/site_media/slides/raymond2017-keynote/combo.html
    self1 = ub.Executor(mode='serial', max_workers=0)
    self1.__enter__()
    self2 = ub.Executor(mode='process', max_workers=2)
    self2.__enter__()
    self3 = ub.Executor(mode='thread', max_workers=2)
    self3.__enter__()
    jobs = []
    jobs.append(self1.submit(sum, [1, 2, 3]))
    jobs.append(self1.submit(sum, [1, 2, 3]))
    jobs.append(self2.submit(sum, [10, 20, 30]))
    jobs.append(self2.submit(sum, [10, 20, 30]))
    jobs.append(self3.submit(sum, [4, 5, 5]))
    jobs.append(self3.submit(sum, [4, 5, 5]))
    for job in jobs:
        result = job.result()
        print('result = {!r}'.format(result))
    self1.__exit__(None, None, None)
    self2.__exit__(None, None, None)
    self3.__exit__(None, None, None)


def test_done_callback():
    import ubelt as ub
    self1 = ub.Executor(mode='serial', max_workers=0)
    with self1:
        jobs = []
        for i in range(10):
            jobs.append(self1.submit(sum, [i + 1, i]))
        for job in jobs:
            job.add_done_callback(lambda x: print('done callback got x = {}'.format(x)))
            result = job.result()
            print('result = {!r}'.format(result))


def _killable_worker(kill_fpath):
    """
    An infinite loop that we can kill by writing a sentinel value to disk
    """
    import ubelt as ub
    timer = ub.Timer().tic()
    while True:
        # Don't want for too long
        if timer.toc() > 10:
            return
        if kill_fpath.exists():
            return


def _sleepy_worker(seconds, loops=100):
    """
    An infinite loop that we can kill by writing a sentinel value to disk
    """
    import time
    start_time = time.monotonic()
    while True:
        time.sleep(seconds / loops)
        elapsed = time.monotonic() - start_time
        if elapsed > seconds:
            return elapsed


def test_as_completed_timeout():
    """
    xdoctest ~/code/ubelt/tests/test_futures.py test_as_completed_timeout
    """
    from concurrent.futures import TimeoutError

    import ubelt as ub
    import uuid
    kill_fname = str(uuid.uuid4()) + '.signal'

    # modes = ['thread', 'process', 'serial']
    modes = ['thread', 'process']

    timeout = 0.1
    dpath = ub.Path.appdir('ubelt', 'tests', 'futures', 'timeout').ensuredir()
    kill_fpath = dpath / kill_fname

    for mode in modes:
        jobs = ub.JobPool(mode=mode, max_workers=2)
        with jobs:
            print('Submitting')
            timer = ub.Timer().tic()

            jobs.submit(_sleepy_worker, seconds=1e-1)
            print('Submit job: ' + str(timer.toc()))
            jobs.submit(_sleepy_worker, seconds=2e-1)
            print('Submit job: ' + str(timer.toc()))
            jobs.submit(_sleepy_worker, seconds=3e-1)
            print('Submit job: ' + str(timer.toc()))
            jobs.submit(_killable_worker, kill_fpath)
            print('Submit job: ' + str(timer.toc()))
            jobs.submit(_killable_worker, kill_fpath)
            print('Submit job: ' + str(timer.toc()))
            jobs.submit(_killable_worker, kill_fpath)
            print('Submit job: ' + str(timer.toc()))
            jobs.submit(_killable_worker, kill_fpath)
            print('Submit job: ' + str(timer.toc()))

            print('Finished submit')
            timer.tic()
            try:
                completed_iter = jobs.as_completed(timeout=timeout)
                timer.tic()
                for job in completed_iter:
                    print('Collect job: ' + str(timer.toc()))
                    try:
                        job.result()
                    except Exception as ex:
                        print(f'ex={ex}')
                        ...
                    # print('job = {}'.format(ub.urepr(job, nl=1)))
                    timer.tic()
                    ...
            except TimeoutError as ex:
                print(f'We got a timeout ex={ex}')

            print('Handled timeout: ' + str(timer.toc()))
            print('We cant escape this context until the jobs finish')
            print([j._state for j in jobs.jobs])
            kill_fpath.touch()
            print([j._state for j in jobs.jobs])
        print([j._state for j in jobs.jobs])

        print('Cleanup')
        kill_fpath.delete()
        print('End of function')


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/tests/test_futures.py
    """
    test_as_completed_timeout()
    # import xdoctest
    # xdoctest.doctest_module(__file__)
