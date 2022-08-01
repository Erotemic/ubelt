"""
An implemention of a set-enabled dictionary that we might include

References:
    .. [SetDictRecipe1] https://gist.github.com/rossmacarthur/38fa948b175abb512e12c516cc3b936d
    .. [SetDictRecipe2] https://code.activestate.com/recipes/577471-setdict/
"""
import itertools as it
from ubelt import NoParam


class SetDict(dict):
    """
    An extension of dict with set operations.


    Benchmark:
        import sys, ubelt
        sys.path.append(ubelt.expandpath('~/code/ubelt/dev'))
        from setdict import *  # NOQA

        # pip install nprime

        import nprime
        size = 10

        primes = SetDict({v: f'prime_{v}' for v in nprime.generate_primes(size)})
        evens = SetDict({v: f'even_{v}' for v in range(0, size, 2)})
        odds = SetDict({v: f'odd_{v}' for v in range(1, size, 2)})
        ints = SetDict({v: f'int_{v}' for v in range(0, size)})
        squares = SetDict({v: f'square_{v}' for _ in range(0, size) if (v:= _ ** 2) < size})
        div3 = SetDict({v: f'div3_{v}' for v in range(0, size) if v % 3 == 0})

        evens - squares
        odds & primes
        squares | primes
        odds ^ primes

        ints.intersection(odds, primes)
        evens.union(odds, primes)
        ints.difference(primes, squares)
        odds.symmetric_difference(primes, div3)

        ints.subset(primes.keys())

        base_dicts = {}
        base_dicts['primes'] = SetDict({v: f'prime_{v}' for v in nprime.generate_primes(size)})
        base_dicts['evens'] = SetDict({v: f'even_{v}' for v in range(0, size, 2)})
        base_dicts['odds'] = SetDict({v: f'odd_{v}' for v in range(1, size, 2)})
        base_dicts['ints'] = SetDict({v: f'int_{v}' for v in range(0, size)})
        base_dicts['squares'] = SetDict({v: f'square_{v}' for _ in range(0, size) if (v:= _ ** 2) < size})

        #### Benchmarks

        keysets = {k: set(v.keys()) for k, v in base_dicts.items()}
        many_keysets = {k: [{n} for n in v.keys()] for k, v in base_dicts.items()}

        import timerit
        ti = timerit.Timerit(10000, bestof=50, verbose=2)

        k1 = 'primes'
        k2 = 'odds'

        d1 = base_dicts[k1]
        d2 = base_dicts[k2]

        ks2 = keysets[k2]
        many_ks2 = many_keysets[k2]

        print('---')

        for timer in ti.reset(f'{k1}.union({k2})'):
            d1.union(d2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.union({k2})'):
            ub.dict_union(d1, d2)

        # ---
        print('---')

        for timer in ti.reset(f'{k1}.intersection({k2})'):
            d1.intersection(d2)

        for timer in ti.reset(f'{k1}.intersection(keyset-{k2})'):
            d1.intersection(ks2)

        for timer in ti.reset(f'{k1}.intersection(many-keyset-{k2})'):
            d1.intersection(*many_ks2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.intersection({k2})'):
            ub.dict_isect(d1, d2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.intersection(keyset-{k2})'):
            ub.dict_isect(d1, ks2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.intersection(many-keyset-{k2})'):
            ub.dict_isect(d1, *many_ks2)

        # ---
        print('---')

        for timer in ti.reset(f'{k1}.difference({k2})'):
            d1.difference(d2)

        for timer in ti.reset(f'{k1}.difference(keyset-{k2})'):
            d1.difference(ks2)

        for timer in ti.reset(f'{k1}.difference(many-keyset-{k2})'):
            d1.difference(*many_ks2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.difference({k2})'):
            ub.dict_diff(d1, d2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.difference(keyset-{k2})'):
            ub.dict_diff(d1, ks2)

        for timer in ti.reset(f'ubelt.dict_ {k1}.difference(many-keyset-{k2})'):
            ub.dict_diff(d1, *many_ks2)


        # Test builtin dictionary union op
        dict.__or__(evens, odds)

        self = evens
        others = (odds,)

        evens.difference(odds)
        evens.union(odds)
        evens.intersection(odds)

        odds.difference(primes)
        odds.intersection(primes)
        odds.union(primes)
    """

    # We could just use the builtin variant
    # def __or__(self, other):
    #     return self.union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __sub__(self, other):
        return self.difference(other)

    def __xor__(self, other):
        return self.symmetric_difference(other)

    ### Main set operations

    def union(self, *others):
        """
        Return the key-based union of two or more dictionaries.

        For items with intersecting keys, dictionaries towards the end of the
        sequence are given precedence.
        """
        cls = self.__class__
        args = it.chain([self], others)
        new = cls(it.chain.from_iterable(d.items() for d in args))
        return new

    def intersection(self, *others):
        """
        Return the key-based intersection of two or more dictionaries.
        """
        cls = self.__class__
        isect_keys = set(self.keys())
        for v in others:
            isect_keys.intersection_update(v)
        new = cls((k, self[k]) for k in self if k in isect_keys)
        return new

    def difference(self, *others):
        """
        Return the key-based difference between this dictionary and one ore
        more other dictionary / keys.

        Note that value and item based differences are not generally efficient
        and therefore unsupported.
        """
        cls = self.__class__
        other_keys = set()
        for v in others:
            other_keys.update(v)
        # Looping over original keys is important to maintain partial order.
        new = cls((k, self[k]) for k in self.keys() if k not in other_keys)
        return new

    def symmetric_difference(self, *others):
        """
        Returns elements that are in an odd number of the given dictionaries

        or... should this be defined as keys that are in an odd number of
        dictionaries, similar to xor of bits?

        Returns elements that are in exactly one of the given dictionaries?

        References:
            https://www.geeksforgeeks.org/python-symmetric-difference-of-dictionaries/
            https://en.wikipedia.org/wiki/Symmetric_difference
        """
        from collections import defaultdict
        cls = self.__class__
        accum_count = defaultdict(lambda: 0)
        accum_refs = {}
        for d in it.chain([self], others):
            for k in d.keys():
                accum_count[k] += 1
                accum_refs[k] = d
        new = cls((k, accum_refs[k][k]) for k, count in accum_count.items()
                  if count % 2 == 1)
        return new

    ### Extra set operations

    def subdict(self, keys, default=NoParam):
        """
        Get a subset of a dictionary
        """
        cls = self.__class__
        if default is NoParam:
            new = cls([(k, self[k]) for k in keys])
        else:
            new = cls([(k, self.get(k, default)) for k in keys])
        return new


sdict = SetDict


class UbeltDict(SetDict):

    def map_keys(self, func):
        import ubelt as ub
        return ub.map_keys(func, self)

    def map_values(self, func):
        import ubelt as ub
        return ub.map_values(func, self)

    def invert(self, unique_vals=True):
        import ubelt as ub
        return ub.invert_dict(self, unique_vals=unique_vals)


def intersection_method_bench():
    """
        Ignore:
            import random
            num_sets = 100
            num_others = 100
            num_core = 5
            import ubelt
            import sys
            sys.path.append(ubelt.expandpath('~/code/ultrajson/json_benchmarks'))
            sys.path.append(ubelt.expandpath('~/code/ultrajson'))
            from json_benchmarks.benchmarker.benchmarker import *  # NOQA
            import benchmarker

            def data_lut(num_sets=100, num_others=100, num_core=5):
                rng = random.Random(0)
                core = set(range(0, num_core))
                datas = []
                for _ in range(num_sets):
                    nextset = core.copy()
                    nextset.update({rng.randint(0, 1000) for _ in range(num_others)})
                    datas.append(nextset)
                return datas

            def method_loop_isect_update(datas):
                isect_keys = set(datas[0])
                for v in datas[1:]:
                    isect_keys.intersection_update(v)

            def method_isect_map_set(datas):
                set.intersection(*map(set, datas))

            basis = {
                'impl': ['method_loop_isect_update', 'method_isect_map_set'],
                'num_sets': [1, 3, 10, 50, 100,]
            }

            impl_lut = vars()

            self = Benchmarker(name='set-isect', num=10000, bestof=30, basis=basis)
            for params in self.iter_params():
                impl = impl_lut[params['impl']]
                datas = data_lut(**ub.compatible(params, data_lut))
                for timer in self.measure():
                    with timer:
                        impl(datas)
            print('self.result = {}'.format(ub.repr2(self.result.__json__(), sort=0, nl=2, precision=8)))
            dpath = ub.Path.appdir('benchmarker/demo').ensuredir()
            self.dump_in_dpath(dpath)

            results = self.result.to_result_list()
            metric_key = "mean_time"
            analysis = benchmarker.result_analysis.ResultAnalysis(
                results,
                metrics=[metric_key],
                params=["impl"],
                metric_objectives={
                    "min_time": "min",
                    "mean_time": "min",
                    "time": "min",
                },
            )
            import kwplot
            kwplot.autompl()
            analysis.analysis()
            xlabel = 'num_sets'
            metric_key = 'mean_time'
            group_labels = {
                 # 'fig': ['u'],
                 # 'col': ['y', 'v'],
                 'hue': ['impl'],
            }
            analysis.plot(xlabel, metric_key, group_labels)
    """
