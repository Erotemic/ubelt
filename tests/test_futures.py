
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
        final = list(pool.as_completed(desc='collect jobs', progkw={'verbose': 3}))

    assert len(cap.text.split('\n')) > len(pool.jobs)

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
