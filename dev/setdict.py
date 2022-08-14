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
    A dictionary subclass where all set operations are defined.

    All of the set operations are defined in a key-wise fashion, that is it is
    like performing the operation on sets of keys.

    Value-wise or item-wise operations are in general not hashable and
    therefore not supported. A heavier extension would be needed for that.

    Example:
        >>> import ubelt as ub
        >>> primes = SetDict({v: f'prime_{v}' for v in [2, 3, 5, 7, 11]})
        >>> evens = SetDict({v: f'even_{v}' for v in [0, 2, 4, 6, 8, 10]})
        >>> odds = SetDict({v: f'odd_{v}' for v in [1, 3, 5, 7, 9, 11]})
        >>> squares = SetDict({v: f'square_{v}' for v in [0, 1, 4, 9]})
        >>> div3 = SetDict({v: f'div3_{v}' for v in [0, 3, 6, 9]})
        >>> # All of the set methods are defined
        >>> results1 = {}
        >>> results1['ints'] = odds.union(evens)
        >>> results1['composites'] = ints.difference(primes)
        >>> results1['even_primes'] = evens.intersection(primes)
        >>> results1['odd_nonprimes_and_two'] = odds.symmetric_difference(primes)
        >>> print('results1 = {}'.format(ub.repr2(results1, nl=2, sort=True)))
        results1 = {
            'composites': {
                0: 'even_0',
                1: 'odd_1',
                4: 'even_4',
                6: 'even_6',
                8: 'even_8',
                9: 'odd_9',
                10: 'even_10',
            },
            'even_primes': {
                2: 'even_2',
            },
            'ints': {
                0: 'even_0',
                1: 'odd_1',
                2: 'even_2',
                3: 'odd_3',
                4: 'even_4',
                5: 'odd_5',
                6: 'even_6',
                7: 'odd_7',
                8: 'even_8',
                9: 'odd_9',
                10: 'even_10',
                11: 'odd_11',
            },
            'odd_nonprimes_and_two': {
                1: 'odd_1',
                2: 'prime_2',
                9: 'odd_9',
            },
        }
        >>> # As well as their corresponding binary operators
        >>> assert results1['ints'] == odds | evens
        >>> assert results1['composites'] == ints - primes
        >>> assert results1['even_primes'] == evens & primes
        >>> assert results1['odd_nonprimes_and_two'] == odds ^ primes
        >>> # These can also be used as classmethods
        >>> assert results1['ints'] = SetDict.union(odds, evens)
        >>> assert results1['composites'] = SetDict.difference(ints, primes)
        >>> assert results1['even_primes'] = SetDict.intersection(evens, primes)
        >>> assert results1['odd_nonprimes_and_two'] = SetDict.symmetric_difference(odds, primes)
        >>> # The narry variants are also implemented
        >>> results2 = {}
        >>> results2['nary_union'] = SetDict.union(primes, div3, odds)
        >>> results2['nary_difference'] = SetDict.difference(primes, div3, odds)
        >>> results2['nary_intersection'] = SetDict.intersection(primes, div3, odds)
        >>> # Note that the definition of symmetric difference might not be what you think in the nary case.
        >>> results2['nary_symmetric_difference'] = SetDict.symmetric_difference(primes, div3, odds)
        >>> print('results2 = {}'.format(ub.repr2(results2, nl=2, sort=True)))
        results2 = {
            'nary_difference': {
                2: 'prime_2',
            },
            'nary_intersection': {
                3: 'prime_3',
            },
            'nary_symmetric_difference': {
                0: 'div3_0',
                1: 'odd_1',
                2: 'prime_2',
                3: 'odd_3',
                6: 'div3_6',
            },
            'nary_union': {
                0: 'div3_0',
                1: 'odd_1',
                2: 'prime_2',
                3: 'odd_3',
                5: 'odd_5',
                6: 'div3_6',
                7: 'odd_7',
                9: 'odd_9',
                11: 'odd_11',
            },
        }
        >>> # Lastly there is also a subdict method, which is similar to
        >>> # Intersect, but it will error if the key doesn't exist unless
        >>> # a default value is given
        >>> sub_primes = primes.subdict([2, 3, 5])
        >>> import pytest
        >>> with pytest.raises(KeyError):
        >>>     sub_primes = primes.subdict([1, 3, 5])
        >>> bad_sub_primes = primes.subdict([1, 3, 5], default='DEFAULT')
        >>> print(f'sub_primes={sub_primes}')
        >>> print(f'bad_sub_primes={bad_sub_primes}')
        sub_primes={2: 'prime_2', 3: 'prime_3', 5: 'prime_5'}
        bad_sub_primes={1: 'DEFAULT', 3: 'prime_3', 5: 'prime_5'}

    Example:
        >>> # A neat thing about our implementation is that often the right
        >>> # hand side is not required to be a dictionary, just something
        >>> # that can be cast to a set.
        >>> primes = SetDict({2: 'a', 3: 'b', 5: 'c', 7: 'd', 11: 'e'})
        >>> primes - {2, 3}
        {5: 'c', 7: 'd', 11: 'e'}
        >>> primes & {2, 3}
        {2: 'a', 3: 'b'}
        >>> # Union does need to have a second dictionary
        >>> import pytest
        >>> with pytest.raises(AttributeError):
        >>>     primes | {2, 3}

    """

    # We could just use the builtin variant for this specific operation
    def __or__(self, other):
        """ The | union operator """
        return self.union(other)

    def __and__(self, other):
        """ The & intersection operator """
        return self.intersection(other)

    def __sub__(self, other):
        """ The - difference operator """
        return self.difference(other)

    def __xor__(self, other):
        """ The ^ symmetric_difference operator """
        return self.symmetric_difference(other)

    ### Main set operations

    def union(self, *others):
        """
        Return the key-wise union of two or more dictionaries.

        For items with intersecting keys, dictionaries towards the end of the
        sequence are given precedence.

        Args:
            self (SetDict | dict):
                if called as a static method this must be provided.

            *others : other dictionary like objects that have an ``items``
                method. (i.e. it must return an iterable of 2-tuples where the
                first item is hashable.)

        Returns:
            dict : whatever the dictionary type of the first argument is

        Example:
            >>> a = SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> a | b
            {2: 'B_c', 3: 'A_d', 5: 'A_f', 7: 'B_h', 4: 'B_e', 0: 'B_a'}
            >>> a.union(b)
            >>> a | b | c
            >>> res = SetDict.union(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {0: B_a, 2: C_c, 3: C_d, 4: B_e, 5: A_f, 7: B_h, 8: C_i, 9: D_j, 10: D_k, 11: D_l}
        """
        cls = self.__class__
        args = it.chain([self], others)
        new = cls(it.chain.from_iterable(d.items() for d in args))
        return new

    def intersection(self, *others):
        """
        Return the key-wise intersection of two or more dictionaries.

        All items returned will be from the first dictionary for keys that
        exist in all other dictionaries / sets provided.

        Args:
            self (SetDict | dict):
                if called as a static method this must be provided.

            *others : other dictionary or set like objects that can
                be coerced into a set of keys.

        Returns:
            dict : whatever the dictionary type of the first argument is

        Example:
            >>> a = SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> a & b
            {2: 'A_c', 7: 'A_h'}
            >>> a.intersection(b)
            >>> a & b & c
            >>> res = SetDict.intersection(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {}
        """
        cls = self.__class__
        isect_keys = set(self.keys())
        for v in others:
            isect_keys.intersection_update(v)
        new = cls((k, self[k]) for k in self if k in isect_keys)
        return new

    def difference(self, *others):
        """
        Return the key-wise difference between this dictionary and one or
        more other dictionary / keys.

        The returned items will be from the first dictionary, and will only
        contain keys that do not appear in any of the other dictionaries /
        sets.

        Args:
            self (SetDict | dict):
                if called as a static method this must be provided.

            *others : other dictionary or set like objects that can
                be coerced into a set of keys.

        Returns:
            dict : whatever the dictionary type of the first argument is

        Example:
            >>> a = SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> a - b
            {3: 'A_d', 5: 'A_f'}
            >>> a.difference(b)
            >>> a - b - c
            >>> res = SetDict.difference(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {5: 'A_f'}
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
        Return the key-wise symmetric difference between this dictionary and
        one or more other dictionaries.

        Returns items that are (key-wise) in an odd number of the given
        dictionaries. This is consistent with the standard n-ary definition of
        symmetric difference [WikiSymDiff]_ and corresponds with the xor
        operation.

        It is unclear if this is the best definition, and I'm open to modifying
        this API. See also [PySymDiff]_.

        Args:
            self (SetDict | dict):
                if called as a static method this must be provided.

            *others : other dictionary or set like objects that can
                be coerced into a set of keys.

        Returns:
            dict : whatever the dictionary type of the first argument is

        References:
            .. [PySymDiff] https://www.geeksforgeeks.org/python-symmetric-difference-of-dictionaries/
            .. [WikiSymDiff] https://en.wikipedia.org/wiki/Symmetric_difference

        Example:
            >>> a = SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> a ^ b
            {3: 'A_d', 5: 'A_f', 4: 'B_e', 0: 'B_a'}
            >>> a.symmetric_difference(b)
            >>> a - b - c
            >>> res = SetDict.symmetric_difference(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {0: B_a, 2: C_c, 4: B_e, 5: A_f, 8: C_i, 9: D_j, 10: D_k, 11: D_l}
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

        Args:
            self (Dict[KT, VT]): superset dictionary

            keys (Iterable[KT]): keys to take from ``dict_``

            default (Optional[object] | NoParamType):
                if specified uses default if keys are missing.

        Raises:
            KeyError : if a key does not exist and default is not specified

        Example:
            >>> a = SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> s = a.subdict({2, 5})
            >>> print('s = {}'.format(ub.repr2(s, nl=0)))
            s = {2: 'A_c', 5: 'A_f'}
            >>> import pytest
            >>> with pytest.raises(KeyError):
            >>>     s = a.subdict({2, 5, 100})
            >>> s = a.subdict({2, 5, 100}, default='DEF')
            >>> print('s = {}'.format(ub.repr2(s, nl=0)))
            s = {2: 'A_c', 5: 'A_f', 100: 'DEF'}
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


def bench():
    """

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

import ubelt as ub  # NOQA


class RorUDictType(type):
    cls = ub.UDict

    @classmethod
    def __ror__(mcls, obj):
        print('__ror__')
        print(f'{mcls=} {type(mcls)=}')
        print(f'{obj=} {type(obj)=}')
        return mcls.cls(obj)

    @classmethod
    def __or__(mcls, obj):
        print('__or__')
        print(f'{mcls=} {type(mcls)=}')
        print(f'{obj=} {type(obj)=}')
        return mcls.cls(obj)


class RorUDict(RorUDictType.cls, metaclass=RorUDictType):
    pass

try:
    type({'10': 10} | RorUDict)
except Exception as ex:
    print(f'ex={ex}')

try:
    RorUDict | {'10': 10}
except Exception as ex:
    print(f'ex={ex}')
