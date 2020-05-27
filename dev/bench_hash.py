
def benchmark_hash_data():
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_hash.py --convert=True --show
        python ~/code/ubelt/dev/bench_hash.py --convert=False --show
    """
    import ubelt as ub
    #ITEM = 'JUST A STRING' * 100
    ITEM = [0, 1, 'a', 'b', ['JUST A STRING'] * 4]
    HASHERS = ['sha1', 'sha512', 'xxh32', 'xxh64']
    scales = list(range(5, 13))
    results = ub.AutoDict()
    # Use json is faster or at least as fast it most cases
    # xxhash is also significantly faster than sha512
    convert = ub.argval('--convert', default='True').lower() == 'True'
    print('convert = {!r}'.format(convert))
    ti = ub.Timerit(9, bestof=3, verbose=1, unit='ms')
    for s in ub.ProgIter(scales, desc='benchmark', verbose=3):
        N = 2 ** s
        print(' --- s={s}, N={N} --- '.format(s=s, N=N))
        data = [ITEM] * N
        for hasher in HASHERS:
            for timer in ti.reset(hasher):
                ub.hash_data(data, hasher=hasher, convert=convert)
            results[hasher].update({N: ti.mean()})
        col = {h: results[h][N] for h in HASHERS}
        sortx = ub.argsort(col)
        ranking = ub.dict_subset(col, sortx)
        print('walltime: ' + ub.repr2(ranking, precision=9, nl=0))
        best = next(iter(ranking))
        #pairs = list(ub.iter_window( 2))
        pairs = [(k, best) for k in ranking]
        ratios = [ranking[k1] / ranking[k2] for k1, k2 in pairs]
        nicekeys = ['{}/{}'.format(k1, k2) for k1, k2 in pairs]
        relratios = ub.odict(zip(nicekeys, ratios))
        print('speedup: ' + ub.repr2(relratios, precision=4, nl=0))
    # xdoc +REQUIRES(--show)
    # import pytest
    # pytest.skip()
    import pandas as pd
    df = pd.DataFrame.from_dict(results)
    df.columns.name = 'hasher'
    df.index.name = 'N'
    ratios = df.copy().drop(columns=df.columns)
    for k1, k2 in [('sha512', 'xxh32'), ('sha1', 'xxh32'), ('xxh64', 'xxh32')]:
        ratios['{}/{}'.format(k1, k2)] = df[k1] / df[k2]
    print()
    print('Seconds per iteration')
    print(df.to_string(float_format='%.9f'))
    print()
    print('Ratios of seconds')
    print(ratios.to_string(float_format='%.2f'))
    print()
    print('Average Ratio (over all N)')
    print('convert = {!r}'.format(convert))
    print(ratios.mean().sort_values())
    if ub.argflag('--show'):
        import netharn.util as kwel
        kwel.autompl()
        xdata = sorted(ub.peek(results.values()).keys())
        ydata = ub.map_vals(lambda d: [d[x] for x in xdata], results)
        kwel.multi_plot(xdata, ydata, xlabel='N', ylabel='seconds', title='convert = {}'.format(convert))
        kwel.show_if_requested()


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_hash.py
    """
    benchmark_hash_data()
