
def bench_notnot_vs_bool():
    """
    References:
        https://www.youtube.com/watch?v=9gEX7jesV34
    """
    x = 42

    import timerit
    ti = timerit.Timerit(1000000, bestof=10, verbose=3, unit='ns')

    for timer in ti.reset('not not'):
        with timer:
            result1 = not not x

    for timer in ti.reset('bool'):
        with timer:
            result2 = bool(x)

    print('result1 = {!r}'.format(result1))
    print('result2 = {!r}'.format(result2))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_notnot.py
    """
    import dis
    dis.dis('not not x')
    dis.dis('bool(x)')
    bench_notnot_vs_bool()
