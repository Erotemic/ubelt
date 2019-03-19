def bench_dict_hist():

    import operator as op
    import ubelt as ub

    import random
    import string
    rng = random.Random(0)
    items = [rng.choice(string.printable) for _ in range(5000)]
    hist_ = ub.ddict(lambda: 0)
    for item in items:
        hist_[item] += 1

    OrderedDict = ub.odict

    ti = ub.Timerit(1000, bestof=10, verbose=2)

    for timer in ti.reset('time'):
        with timer:
            getval = op.itemgetter(1)
            key_order = (key for (key, value) in sorted(hist_.items(), key=getval))
            hist = ub.dict_subset(hist_, key_order)

    for timer in ti.reset('time'):
        with timer:
            getval = op.itemgetter(1)
            key_order = [key for (key, value) in sorted(hist_.items(), key=getval)]
            hist = ub.dict_subset(hist_, key_order)

    for timer in ti.reset('itemgetter'):
        with timer:
            # WINNER
            getval = op.itemgetter(1)
            hist = OrderedDict([
                (key, value)
                for (key, value) in sorted(hist_.items(), key=getval)
            ])

    # -----------------

    for timer in ti.reset('itemgetter'):
        with timer:
            # WINNER
            getval = op.itemgetter(1)
            key_order = [key for (key, value) in sorted(hist_.items(), key=getval)]

    for timer in ti.reset('lambda'):
        with timer:
            key_order = [key for (key, value) in sorted(hist_.items(), key=lambda x: x[1])]
