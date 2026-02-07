"""
This code is based on a template that lives in:
    https://github.com/Erotemic/timerit/blob/main/examples/benchmark_template.py

    Or typically on a dev machine in

    ~/code/timerit/examples/benchmark_template.py

SeeAlso:
    ~/code/ubelt/dev/bench/bench_dict_hist.py

CommandLine:
    python ~/code/ubelt/dev/bench/bench_defaultdict.py
"""


def benchmark_template():
    from collections import defaultdict

    import pandas as pd
    import timerit

    import ubelt as ub

    plot_labels = {
        'x': 'Input Size',
        'y': 'Time',
        'title': 'Dict[Any, List] Accumulation Benchmark',
    }

    # Some bookkeeping needs to be done to build a dictionary that maps the
    # method names to the functions themselves.
    method_lut = {}
    def register_method(func):
        method_lut[func.__name__] = func
        return func

    # Define the methods you want to benchmark. The arguments should be
    # parameters that you want to vary in the test.

    import benedict
    @register_method
    def accumulate_benedict_tryexcept(input_data):
        d = benedict.BeneDict()
        for item in input_data:
            try:
                d[item].append(item)
            except KeyError:
                d[item] = []
                d[item].append(item)
        return d

    @register_method
    def accumulate_udict_tryexcept(input_data):
        d = ub.udict()
        for item in input_data:
            try:
                d[item].append(item)
            except KeyError:
                d[item] = []
                d[item].append(item)
        return d

    # @register_method
    # def accum_defaultdict(input_data):
    #     d = defaultdict(list)
    #     for item in input_data:
    #         d[item].append(item)
    #     return d

    # @register_method
    # def accumulate_dict_setdefault(input_data):
    #     d = dict()
    #     for item in input_data:
    #         d.setdefault(item, [])
    #         d[item].append(item)
    #     return d

    # @register_method
    # def accumulate_dict_ifcontains(input_data):
    #     d = dict()
    #     for item in input_data:
    #         if item not in d:
    #             d[item] = []
    #         d[item].append(item)
    #     return d

    @register_method
    def accumulate_dict_tryexcept(input_data):
        d = dict()
        for item in input_data:
            try:
                d[item].append(item)
            except KeyError:
                d[item] = []
                d[item].append(item)
        return d

    # @register_method
    # def accumulate_dict_tryexcept_v3(input_data):
    #     d = dict()
    #     for item in input_data:
    #         try:
    #             d[item].append(item)
    #         except KeyError:
    #             d[item] = [item]
    #     return d

    # @register_method
    # def accumulate_dict_tryexcept_v2(input_data):
    #     d = dict()
    #     for item in input_data:
    #         try:
    #             arr = d[item]
    #         except KeyError:
    #             arr = d[item] = []
    #         arr.append(item)
    #     return d

    def generate_input(input_size, num_unique_items):
        import random
        rng = random.Random()
        pool = range(num_unique_items)
        input_data = rng.choices(pool, k=input_size)
        return input_data

    # Change params here to modify number of trials
    ti = timerit.Timerit(1000, bestof=100, verbose=1)

    # if True, record every trail run and show variance in seaborn
    # if False, use the standard timerit min/mean measures
    RECORD_ALL = True

    # These are the parameters that we benchmark over
    basis = {
        'method': list(method_lut),  # i.e. ['method1', 'method2']
        'input_size': [10, 100, 500, 1000, 2500, 5000, 7500, 10_000, 20_000],
        'num_unique_items': [
            # 1, 10, 100
            100,
        ],
        # 'zparam': [2, 3]
        # 'param_name': [param values],
    }
    xlabel = 'input_size'
    group_labels = {
        'style': ['num_unique_items'],
        # 'size': ['zparam'],
    }
    group_labels['hue'] = list(
        (ub.oset(basis) - {xlabel}) - set.union(*map(set, group_labels.values())))
    grid_iter = list(ub.named_product(basis))

    # For each variation of your experiment, create a row.
    rows = []
    for params in grid_iter:
        params = ub.udict(params)
        group_keys = {}
        for gname, labels in group_labels.items():
            group_keys[gname + '_key'] = ub.urepr(
                params & labels, compact=1, si=1)
        key = ub.urepr(params, compact=1, si=1)
        method = method_lut[params['method']]
        # Timerit will run some user-specified number of loops.
        # and compute time stats with similar methodology to timeit
        for timer in ti.reset(key):
            # Put any setup logic you dont want to time here.
            # ...
            input_size = params['input_size']
            num_unique_items = params['num_unique_items']
            input_data = generate_input(input_size, num_unique_items)
            with timer:
                # Put the logic you want to time here
                method(input_data)

        if RECORD_ALL:
            # Seaborn will show the variance if this is enabled, otherwise
            # use the robust timerit mean / min times
            # chunk_iter = ub.chunks(ti.times, ti.bestof)
            # times = list(map(min, chunk_iter))  # TODO: timerit method for this
            times = ti.robust_times()
            for time in times:
                row = {
                    # 'mean': ti.mean(),
                    'time': time,
                    'key': key,
                    **group_keys,
                    **params,
                }
                rows.append(row)
        else:
            row = {
                'mean': ti.mean(),
                'min': ti.min(),
                'key': key,
                **group_keys,
                **params,
            }
            rows.append(row)

    time_key = 'time' if RECORD_ALL else 'min'

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    data = data.sort_values(time_key)

    if RECORD_ALL:
        # Show the min / mean if we record all
        min_times = data.groupby('key').min().rename({'time': 'min'}, axis=1)
        mean_times = data.groupby('key')[['time']].mean().rename({'time': 'mean'}, axis=1)
        stats_data = pd.concat([min_times, mean_times], axis=1)
        stats_data = stats_data.sort_values('min')
    else:
        stats_data = data

    USE_OPENSKILL = 0
    if USE_OPENSKILL:
        # Lets try a real ranking method
        # https://github.com/OpenDebates/openskill.py
        import openskill
        method_ratings = {m: openskill.Rating() for m in basis['method']}

    other_keys = sorted(set(stats_data.columns) - {'key', 'method', 'min', 'mean', 'hue_key', 'size_key', 'style_key'})
    for params, variants in stats_data.groupby(other_keys):
        variants = variants.sort_values('mean')
        ranking = variants['method'].reset_index(drop=True)

        mean_speedup = variants['mean'].max() / variants['mean']
        stats_data.loc[mean_speedup.index, 'mean_speedup'] = mean_speedup
        min_speedup = variants['min'].max() / variants['min']
        stats_data.loc[min_speedup.index, 'min_speedup'] = min_speedup

        if USE_OPENSKILL:
            # The idea is that each setting of parameters is a game, and each
            # "method" is a player. We rank the players by which is fastest,
            # and update their ranking according to the Weng-Lin Bayes ranking
            # model. This does not take the fact that some "games" (i.e.
            # parameter settings) are more important than others, but it should
            # be fairly robust on average.
            old_ratings = [[r] for r in ub.take(method_ratings, ranking)]
            new_values = openskill.rate(old_ratings)  # Not inplace
            new_ratings = [openskill.Rating(*new[0]) for new in new_values]
            method_ratings.update(ub.dzip(ranking, new_ratings))

    print('Statistics:')
    print(stats_data)

    if USE_OPENSKILL:
        from openskill import predict_win
        win_prob = predict_win([[r] for r in method_ratings.values()])
        skill_agg = pd.Series(ub.dzip(method_ratings.keys(), win_prob)).sort_values(ascending=False)
        print('Aggregated Rankings =\n{}'.format(skill_agg))

    plot = True
    if plot:
        # import seaborn as sns
        # kwplot autosns works well for IPython and script execution.
        # not sure about notebooks.
        import kwplot
        sns = kwplot.autosns()
        plt = kwplot.autoplt()

        plotkw = {}
        for gname, labels in group_labels.items():
            if labels:
                plotkw[gname] = gname + '_key'

        # Your variables may change
        ax = kwplot.figure(fnum=1, doclf=True).gca()
        sns.lineplot(data=data, x=xlabel, y=time_key, marker='o', ax=ax, **plotkw)
        ax.set_title(plot_labels['title'])
        ax.set_xlabel(plot_labels['x'])
        ax.set_ylabel(plot_labels['y'])
        ax.set_xscale('log')
        ax.set_yscale('log')

        try:
            __IPYTHON__
        except NameError:
            plt.show()


if __name__ == '__main__':
    benchmark_template()
