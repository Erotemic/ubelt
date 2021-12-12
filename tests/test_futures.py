
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
