"""
References:
    https://github.com/willmcgugan/rich/blob/master/rich/_loop.py
    https://twitter.com/graingert/status/1432827783357607937
"""
from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")


def loop_first(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for first value."""
    iter_values = iter(values)
    try:
        value = next(iter_values)
    except StopIteration:
        return
    yield True, value
    for value in iter_values:
        yield False, value


def method_loop_first(items):
    """
    Ignore:
        import dis
        dis.dis(method_loop_first)

    Dis:
          2           0 LOAD_GLOBAL              0 (loop_first)
                      2 LOAD_FAST                0 (items)
                      4 CALL_FUNCTION            1
                      6 GET_ITER
                >>    8 FOR_ITER                12 (to 22)
                     10 UNPACK_SEQUENCE          2
                     12 STORE_FAST               1 (is_first)
                     14 STORE_FAST               2 (item)

          3          16 LOAD_FAST                1 (is_first)
                     18 POP_JUMP_IF_FALSE        8

          5          20 JUMP_ABSOLUTE            8
                >>   22 LOAD_CONST               0 (None)
                     24 RETURN_VALUE


    """
    for is_first, item in loop_first(items):
        if is_first:
            pass
        pass


def method_enumerate(items):
    """
    Ignore:
        import dis
        dis.dis(method_enumerate)

    Dis:
          9           0 LOAD_GLOBAL              0 (enumerate)
                      2 LOAD_FAST                0 (items)
                      4 CALL_FUNCTION            1
                      6 GET_ITER
                >>    8 FOR_ITER                16 (to 26)
                     10 UNPACK_SEQUENCE          2
                     12 STORE_FAST               1 (idx)
                     14 STORE_FAST               2 (item)

         10          16 LOAD_FAST                1 (idx)
                     18 LOAD_CONST               1 (0)
                     20 COMPARE_OP               2 (==)
                     22 POP_JUMP_IF_FALSE        8

         12          24 JUMP_ABSOLUTE            8
                >>   26 LOAD_CONST               0 (None)
                     28 RETURN_VALUE

    """
    for idx, item in enumerate(items):
        if idx == 0:
            pass
        pass


def benchmark_loop_first_variants():

    import ubelt as ub
    basis = {
        'num_items': [10, 100, 1000, 10000, 100000],
    }
    data_grid = ub.named_product(**basis)

    rows = []

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=2)

    for data_kw in data_grid:
        items = list(range(data_kw['num_items']))

        method_name = 'loop_first'
        for timer in ti.reset(method_name):
            with timer:
                method_loop_first(items)

        rows.append({
            'num_items': data_kw['num_items'],
            'method_name': method_name,
            'mean': ti.mean()
        })

        method_name = 'enumerate'
        for timer in ti.reset(method_name):
            with timer:
                method_enumerate(items)

        rows.append({
            'num_items': data_kw['num_items'],
            'method_name': method_name,
            'mean': ti.mean()
        })

    print('ti.rankings = {}'.format(ub.repr2(ti.rankings, nl=2, align=':')))
    return rows


def main():
    rows = benchmark_loop_first_variants()
    import pandas as pd
    df = pd.DataFrame(rows)

    # import kwplot
    # plt = kwplot.autoplt()
    import matplotlib as mpl
    mpl.use('Qt5Agg')
    from matplotlib import pyplot as plt

    import seaborn as sns
    sns.set()

    sns.lineplot(data=df, x='num_items', y='mean', hue='method_name',
                 markers='method_name')

    plt.show()


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_first_generator.py
    """
    main()
