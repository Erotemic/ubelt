
def bench_platform_test():
    """
    This is textbook premature optimization, but I was curious

    Results:
        Timed best=477.768 ns, mean=709.491 ± 128.4 ns for == win32
        Timed best=585.802 ns, mean=864.347 ± 191.0 ns for startswith(win32)
        Timed best=494.998 ns, mean=771.782 ± 135.9 ns for == linux
        Timed best=592.787 ns, mean=933.651 ± 177.2 ns for startswith(linux)
    """
    import ubelt as ub
    import sys
    ti = ub.Timerit(10000, bestof=100, verbose=1, unit='ns')

    for timer in ti.reset('== win32'):
        with timer:
            sys.platform == 'win32'

    for timer in ti.reset('startswith(win32)'):
        with timer:
            sys.platform.startswith('win32')

    for timer in ti.reset('== linux'):
        with timer:
            sys.platform == 'linux'

    for timer in ti.reset('startswith(linux)'):
        with timer:
            sys.platform.startswith('linux')
