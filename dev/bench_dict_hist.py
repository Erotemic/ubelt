def bench_dict_hist():
    """
    CommandLine:
        xdoctest -m ~/code/ubelt/dev/bench_dict_hist.py bench_dict_hist

    Results:
        Timed best=48.330 µs, mean=49.437 ± 1.0 µs for dict_subset_iter
        Timed best=59.392 µs, mean=63.395 ± 11.9 µs for dict_subset_list
        Timed best=47.203 µs, mean=47.632 ± 0.2 µs for direct_itemgetter
    """

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

    ti = ub.Timerit(1000, bestof=10, verbose=1)

    for timer in ti.reset('dict_subset_iter'):
        with timer:
            getval = op.itemgetter(1)
            key_order = (key for (key, value) in sorted(hist_.items(), key=getval))
            hist = ub.dict_subset(hist_, key_order)

    for timer in ti.reset('dict_subset_list'):
        with timer:
            getval = op.itemgetter(1)
            key_order = [key for (key, value) in sorted(hist_.items(), key=getval)]
            hist = ub.dict_subset(hist_, key_order)

    for timer in ti.reset('direct_itemgetter'):
        with timer:
            # WINNER
            getval = op.itemgetter(1)
            hist = OrderedDict([
                (key, value)
                for (key, value) in sorted(hist_.items(), key=getval)
            ])

    del hist


def bench_sort_dictionary():
    """
    CommandLine:
        xdoctest -m ~/code/ubelt/dev/bench_dict_hist.py bench_sort_dictionary

    Results:
        Timed best=25.484 µs, mean=25.701 ± 0.1 µs for itemgetter
        Timed best=28.810 µs, mean=29.138 ± 0.3 µs for lambda
    """
    import operator as op
    import ubelt as ub

    import random
    import string
    rng = random.Random(0)
    items = [rng.choice(string.printable) for _ in range(5000)]
    hist_ = ub.ddict(lambda: 0)
    for item in items:
        hist_[item] += 1

    ti = ub.Timerit(1000, bestof=10, verbose=1)
    for timer in ti.reset('itemgetter'):
        with timer:
            # WINNER
            getval = op.itemgetter(1)
            key_order = [key for (key, value) in sorted(hist_.items(), key=getval)]

    for timer in ti.reset('lambda'):
        with timer:
            key_order = [key for (key, value) in sorted(hist_.items(), key=lambda x: x[1])]

    del key_order
