from collections import OrderedDict


def bench_dict_isect():
    import ubelt as ub

    def random_dict(n):
        import random
        keys = set(random.randint(0, n) for _ in range(n))
        return {k: k for k in keys}

    d1 = random_dict(1000)
    d2 = random_dict(1000)

    import xdev
    xdev.profile_now(ub.dict_isect)(d1, d2)
    xdev.profile_now(dict_isect_variant0)(d1, d2)
    xdev.profile_now(dict_isect_variant1)(d1, d2)
    xdev.profile_now(dict_isect_variant2)(d1, d2)
    xdev.profile_now(dict_isect_variant3)(d1, d2)

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=2)
    for timer in ti.reset('current'):
        with timer:
            ub.dict_isect(d1, d2)

    for timer in ti.reset('inline'):
        with timer:
            {k: v for k, v in d1.items() if k in d2}

    for timer in ti.reset('dict_isect_variant0'):
        with timer:
            dict_isect_variant0(d1, d2)

    for timer in ti.reset('dict_isect_variant1'):
        with timer:
            dict_isect_variant1(d1, d2)

    for timer in ti.reset('dict_isect_variant2'):
        with timer:
            dict_isect_variant1(d1, d2)

    for timer in ti.reset('dict_isect_variant3'):
        with timer:
            dict_isect_variant3(d1, d2)

    print('ti.rankings = {}'.format(ub.repr2(ti.rankings['min'], precision=8, align=':', nl=1, sort=0)))


def dict_isect_variant0(d1, d2):
    return {k: v for k, v in d1.items() if k in d2}


def dict_isect_variant1(*args):
    if not args:
        return {}
    else:
        dictclass = args[0].__class__
        common_keys = set.intersection(*map(set, args))
        first_dict = args[0]
        return dictclass((k, first_dict[k]) for k in first_dict
                         if k in common_keys)


def dict_isect_variant2(*args):
    if not args:
        return {}
    else:
        dictclass = args[0].__class__
        common_keys = set.intersection(*map(set, args))
        first_dict = args[0]
        return dictclass((k, first_dict[k]) for k in common_keys)


def dict_isect_variant3(*args):
    if not args:
        return {}
    else:
        common_keys = set.intersection(*map(set, args))
        first_dict = args[0]
        return {k: first_dict[k] for k in common_keys}

if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_dict_operations.py
    """
    bench_dict_isect()
