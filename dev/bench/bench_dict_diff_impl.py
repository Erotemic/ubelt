

def variant():
    import random
    import ubelt as ub
    num_items = 100
    num_other = 1
    first_keys = [random.randint(0, 1000) for _ in range(num_items)]
    remove_sets = [list(ub.unique(random.choices(first_keys, k=10) + [random.randint(0, 1000) for _ in range(num_items)])) for _ in range(num_other)]
    first_dict = {k: k for k in first_keys}
    args = [first_dict] + [{k: k for k in ks} for ks in remove_sets]
    dictclass = dict

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=2)
    for timer in ti.reset('orig'):
        with timer:
            keys = set(first_dict)
            keys.difference_update(*map(set, args[1:]))
            new0 = dictclass((k, first_dict[k]) for k in keys)

    for timer in ti.reset('alt1'):
        with timer:
            remove_keys = {k for ks in args[1:] for k in ks}
            new1 = dictclass((k, v) for k, v in first_dict.items() if k not in remove_keys)

    for timer in ti.reset('alt2'):
        with timer:
            remove_keys = set.union(*map(set, args[1:]))
            new2 = dictclass((k, v) for k, v in first_dict.items() if k not in remove_keys)

    for timer in ti.reset('alt3'):
        with timer:
            remove_keys = set.union(*map(set, args[1:]))
            new3 = dictclass((k, first_dict[k]) for k in first_dict.keys() if k not in remove_keys)

    # Cannot use until 3.6 is dropped (it is faster)
    for timer in ti.reset('alt4'):
        with timer:
            remove_keys = set.union(*map(set, args[1:]))
            new4 = {k: v for k, v in first_dict.items() if k not in remove_keys}

    assert new1 == new0
    assert new2 == new0
    assert new3 == new0
    assert new4 == new0


def benchmark_dict_diff_impl():
    import ubelt as ub
    import pandas as pd
    import timerit
    import random

    def method_diffkeys(*args):
        first_dict = args[0]
        keys = set(first_dict)
        keys.difference_update(*map(set, args[1:]))
        new0 = dict((k, first_dict[k]) for k in keys)
        return new0

    def method_diffkeys_list(*args):
        first_dict = args[0]
        remove_keys = set.union(*map(set, args[1:]))
        keep_keys = [k for k in first_dict.keys() if k not in remove_keys]
        new = dict((k, first_dict[k]) for k in keep_keys)
        return new

    def method_diffkeys_oset(*args):
        first_dict = args[0]
        keys = ub.oset(first_dict)
        keys.difference_update(*map(set, args[1:]))
        new0 = dict((k, first_dict[k]) for k in keys)
        return new0

    def method_ifkeys_setcomp(*args):
        first_dict = args[0]
        remove_keys = {k for ks in args[1:] for k in ks}
        new1 = dict((k, v) for k, v in first_dict.items() if k not in remove_keys)
        return new1

    def method_ifkeys_setunion(*args):
        first_dict = args[0]
        remove_keys = set.union(*map(set, args[1:]))
        new2 = dict((k, v) for k, v in first_dict.items() if k not in remove_keys)
        return new2

    def method_ifkeys_getitem(*args):
        first_dict = args[0]
        remove_keys = set.union(*map(set, args[1:]))
        new3 = dict((k, first_dict[k]) for k in first_dict.keys() if k not in remove_keys)
        return new3

    def method_ifkeys_dictcomp(*args):
        # Cannot use until 3.6 is dropped (it is faster)
        first_dict = args[0]
        remove_keys = set.union(*map(set, args[1:]))
        new4 = {k: v for k, v in first_dict.items() if k not in remove_keys}
        return new4

    def method_ifkeys_dictcomp_getitem(*args):
        # Cannot use until 3.6 is dropped (it is faster)
        first_dict = args[0]
        remove_keys = set.union(*map(set, args[1:]))
        new4 = {k: first_dict[k] for k in first_dict.keys() if k not in remove_keys}
        return new4

    method_lut = locals()  # can populate this some other way

    def make_data(num_items, num_other, remove_fraction, keytype):
        if keytype == 'str':
            keytype = str
        if keytype == 'int':
            keytype = int
        first_keys = [random.randint(0, 1000) for _ in range(num_items)]
        k = int(remove_fraction * len(first_keys))
        remove_sets = [list(ub.unique(random.choices(first_keys, k=k) + [random.randint(0, 1000) for _ in range(num_items)])) for _ in range(num_other)]
        first_dict = {keytype(k): k for k in first_keys}
        args = [first_dict] + [{keytype(k): k for k in ks} for ks in remove_sets]
        return args

    ti = timerit.Timerit(200, bestof=1, verbose=2)

    basis = {
        'method': [
            # Cant use because unordered
            # 'method_diffkeys',

            # Cant use because python 3.6
            'method_ifkeys_dictcomp',
            'method_ifkeys_dictcomp_getitem',

            'method_ifkeys_setunion',
            'method_ifkeys_getitem',
            'method_diffkeys_list',

            # Probably not good
            # 'method_ifkeys_setcomp',
            # 'method_diffkeys_oset',
        ],
        'num_items': [10, 100, 1000],
        'num_other': [1, 3, 5],
        # 'num_other': [1],
        'remove_fraction': [0, 0.2, 0.5, 0.7, 1.0],
        # 'remove_fraction': [0.2, 0.8],
        'keytype': ['str', 'int'],
        # 'keytype': ['str'],
        # 'param_name': [param values],
    }
    xlabel = 'num_items'
    kw_labels = ['num_items', 'num_other', 'remove_fraction', 'keytype']
    group_labels = {
        'style': ['num_other', 'keytype'],
        'size': ['remove_fraction'],
    }
    group_labels['hue'] = list(
        (ub.oset(basis) - {xlabel}) - set.union(*map(set, group_labels.values())))
    grid_iter = list(ub.named_product(basis))

    # For each variation of your experiment, create a row.
    rows = []
    for params in grid_iter:
        group_keys = {}
        for gname, labels in group_labels.items():
            group_keys[gname + '_key'] = ub.repr2(
                ub.dict_isect(params, labels), compact=1, si=1)
        key = ub.repr2(params, compact=1, si=1)
        kwargs = ub.dict_isect(params.copy(),  kw_labels)
        args = make_data(**kwargs)
        method = method_lut[params['method']]
        # Timerit will run some user-specified number of loops.
        # and compute time stats with similar methodology to timeit
        for timer in ti.reset(key):
            # Put any setup logic you dont want to time here.
            # ...
            with timer:
                # Put the logic you want to time here
                method(*args)
        row = {
            'mean': ti.mean(),
            'min': ti.min(),
            'key': key,
            **group_keys,
            **params,
        }
        rows.append(row)

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    data = data.sort_values('min')
    print(data)

    # for each parameter setting, group all methods with that used those exact
    # comparable params. Then rank how good each method did.  That will be a
    # preference profile. We will give that preference profile a weight (e.g.
    # based on the fastest method in the bunch) and then aggregate them with
    # some voting method.

    USE_OPENSKILL = 1
    if USE_OPENSKILL:
        # Lets try a real ranking method
        # https://github.com/OpenDebates/openskill.py
        import openskill
        method_ratings = {m: openskill.Rating() for m in basis['method']}

    weighted_rankings = ub.ddict(lambda: ub.ddict(float))
    for params, variants in data.groupby(['num_other', 'keytype', 'remove_fraction', 'num_items']):
        variants = variants.sort_values('mean')
        ranking = variants['method'].reset_index(drop=True)

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

        # Choose a ranking weight scheme
        weight = variants['mean'].min()
        # weight = 1
        for rank, method in enumerate(ranking):
            weighted_rankings[method][rank] += weight
            weighted_rankings[method]['total'] += weight

    # Probably a more robust voting method to do this
    weight_rank_rows = []
    for method_name, ranks in weighted_rankings.items():
        weights = ub.dict_diff(ranks, ['total'])
        p_rank = ub.map_vals(lambda w: w / ranks['total'], weights)

        for rank, w in p_rank.items():
            weight_rank_rows.append({'rank': rank, 'weight': w, 'name': method_name})
    weight_rank_df = pd.DataFrame(weight_rank_rows)
    piv = weight_rank_df.pivot(['name'], ['rank'], ['weight'])
    print(piv)

    if USE_OPENSKILL:
        from openskill import predict_win
        win_prob = predict_win([[r] for r in method_ratings.values()])
        skill_agg = pd.Series(ub.dzip(method_ratings.keys(), win_prob)).sort_values(ascending=False)
        print('skill_agg =\n{}'.format(skill_agg))

    aggregated = (piv * piv.columns.levels[1].values).sum(axis=1).sort_values()
    print('weight aggregated =\n{}'.format(aggregated))

    plot = True
    if plot:
        # import seaborn as sns
        # kwplot autosns works well for IPython and script execution.
        # not sure about notebooks.
        import kwplot
        sns = kwplot.autosns()

        plotkw = {}
        for gname, labels in group_labels.items():
            if labels:
                plotkw[gname] = gname + '_key'

        # Your variables may change
        ax = kwplot.figure(fnum=1, doclf=True).gca()
        sns.lineplot(data=data, x=xlabel, y='min', marker='o', ax=ax, **plotkw)
        ax.set_title('Benchmark')
        ax.set_xlabel('A better x-variable description')
        ax.set_ylabel('A better y-variable description')
