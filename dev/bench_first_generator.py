"""
References:
    https://github.com/willmcgugan/rich/blob/master/rich/_loop.py
    https://twitter.com/graingert/status/1432827783357607937
"""
from typing import Iterable, Tuple, TypeVar
import itertools as it

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


def loop_first2(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for first value."""
    iter_values = iter(values)
    try:
        value = next(iter_values)
    except StopIteration:
        return
    rest_iter = zip(it.repeat(False), iter_values)
    return it.chain([(True, value)], rest_iter)


def method_loop_first(items):
    x = 0
    for is_first, item in loop_first(items):
        if is_first:
            x += 1
        x += 2


def method_loop_first2(items):
    x = 0
    for is_first, item in loop_first2(items):
        if is_first:
            x += 1
        x += 2


def method_enumerate(items):
    x = 0
    for idx, item in enumerate(items):
        if idx == 0:
            x += 1
        x += 2


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

        method_name = 'loop_first2'
        for timer in ti.reset(method_name):
            with timer:
                method_loop_first2(items)
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
    import ubelt as ub
    dis_results = [
        dis2(loop_first),
        ' | ',
        dis2(loop_first2),
    ]
    print(ub.hzcat(dis_results))

    rows = benchmark_loop_first_variants()
    import pandas as pd
    df = pd.DataFrame(rows)

    import kwplot
    plt = kwplot.autoplt()
    # import matplotlib as mpl
    # mpl.use('Qt5Agg')
    # from matplotlib import pyplot as plt

    import seaborn as sns
    sns.set()

    sns.lineplot(data=df, x='num_items', y='mean', hue='method_name',
                 markers='method_name')

    plt.show()


def dis2(func):
    import io
    import dis
    file = io.StringIO()
    dis.dis(func, file=file)
    file.seek(0)
    return file.read()


def compare_dis():
    """
    Look at the disasembly of the methods in question to gain insight

     46           0 LOAD_CONST               1 (0)          |  54           0 LOAD_CONST               1 (0)
                  2 STORE_FAST               1 (x)                          2 STORE_FAST               1 (x)

     47           4 LOAD_GLOBAL              0 (loop_first)    55           4 LOAD_GLOBAL              0 (enumerate)
                  6 LOAD_FAST                0 (items)                      6 LOAD_FAST                0 (items)
                  8 CALL_FUNCTION            1                              8 CALL_FUNCTION            1
                 10 GET_ITER                                               10 GET_ITER
            >>   12 FOR_ITER                28 (to 42)                >>   12 FOR_ITER                32 (to 46)
                 14 UNPACK_SEQUENCE          2                             14 UNPACK_SEQUENCE          2
                 16 STORE_FAST               2 (is_first)                  16 STORE_FAST               2 (idx)
                 18 STORE_FAST               3 (item)                      18 STORE_FAST               3 (item)

     48          20 LOAD_FAST                2 (is_first)      56          20 LOAD_FAST                2 (idx)
                 22 POP_JUMP_IF_FALSE       32                             22 LOAD_CONST               1 (0)
                                                                           24 COMPARE_OP               2 (==)
     49          24 LOAD_FAST                1 (x)                         26 POP_JUMP_IF_FALSE       36
                 26 LOAD_CONST               2 (1)
                 28 INPLACE_ADD                                57          28 LOAD_FAST                1 (x)
                 30 STORE_FAST               1 (x)                         30 LOAD_CONST               2 (1)
                                                                           32 INPLACE_ADD
     50     >>   32 LOAD_FAST                1 (x)                         34 STORE_FAST               1 (x)
                 34 LOAD_CONST               3 (2)
                 36 INPLACE_ADD                                58     >>   36 LOAD_FAST                1 (x)
                 38 STORE_FAST               1 (x)                         38 LOAD_CONST               3 (2)
                 40 JUMP_ABSOLUTE           12                             40 INPLACE_ADD
            >>   42 LOAD_CONST               0 (None)                      42 STORE_FAST               1 (x)
                 44 RETURN_VALUE                                           44 JUMP_ABSOLUTE           12
                                                                      >>   46 LOAD_CONST               0 (None)
                                                                           48 RETURN_VALUE
    """
    import ubelt as ub
    dis_results = [
        dis2(method_loop_first),
        ' | ',
        dis2(method_enumerate),
    ]
    print(ub.hzcat(dis_results))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_first_generator.py
    """
    main()
