

def main():
    import ubelt as ub
    from ubelt import util_list
    from ubelt.util_list import take
    import random
    from math import e

    # # Data
    N = 100
    array = [random.random() for _ in range(N)]
    indices = [random.randint(0, N - 1) for _ in range(int(N // e))]

    ti = ub.Timerit(2 ** 11, bestof=2 ** 8, verbose=1)

    for timer in ti.reset('take'):
        with timer:
            list(take(array, indices))

    for timer in ti.reset('util_list.take'):
        with timer:
            list(util_list.take(array, indices))

    for timer in ti.reset('ub.take'):
        with timer:
            list(ub.take(array, indices))

    print('---')

    # import pandas as pd
    # df = pd.DataFrame(rankings)
    # print('df =\n{}'.format(df))

    print('rankings = {}'.format(ub.repr2(ti.rankings, precision=9, nl=2)))
    print('consistency = {}'.format(ub.repr2(ti.consistency, precision=9, nl=2)))

    positions = ub.ddict(list)
    for m1, v1 in ti.rankings.items():
        for pos, label in enumerate(ub.argsort(v1), start=0):
            positions[label].append(pos)
    average_position = ub.map_vals(lambda x: sum(x) / len(x), positions)
    print('average_position = {}'.format(ub.repr2(average_position)))


if __name__ == '__main__':
    """
    CommandLine:
        xdoctest -m ~/code/ubelt/dev/bench_modaccess_overhead.py main
    """
    main()
