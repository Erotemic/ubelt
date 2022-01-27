"""
Functions for working with dictionaries.

The :func:`dict_hist` function counts the number of discrete occurrences of hashable
items. Similarly :func:`find_duplicates` looks for indices of items that occur more
than `k=1` times.

The :func:`map_keys` and :func:`map_vals` functions are useful for transforming the keys
and values of a dictionary with less syntax than a dict comprehension.

The :func:`dict_union`, :func:`dict_isect`, and :func:`dict_diff` functions
are similar to the set equivalents.

The :func:`dzip` function zips two iterables and packs them into a dictionary
where the first iterable is used to generate keys and the second generates
values.

The :func:`group_items` function takes two lists and returns a dict mapping
values in the second list to all items in corresponding locations in the first
list.

The :func:`invert_dict` function swaps keys and values. See the function docs
for details on dealing with unique and non-unique values.

The :func:`ddict` and :func:`odict` functions are alias for the commonly used
:func:`collections.defaultdict` and :func:`collections.OrderedDict` classes.

"""
import operator as op
import itertools as it
from collections import OrderedDict
from collections import defaultdict
from ubelt import util_const
from ubelt import util_list
from ubelt.util_const import NoParam

__all__ = [
    'AutoDict',
    'AutoOrderedDict',
    'dzip',
    'ddict',
    'dict_hist',
    'dict_subset',
    'dict_union',
    'dict_isect',
    'dict_diff',
    'find_duplicates',
    'group_items',
    'invert_dict',
    'map_keys',
    'map_vals',
    'sorted_keys',
    'sorted_vals',
    'odict',
    'named_product',
    'varied_values',
]


# Expose for convenience
odict = OrderedDict
ddict = defaultdict


class AutoDict(dict):
    """
    An infinitely nested default dict of dicts.

    Implementation of Perl's autovivification feature.

    SeeAlso:
        :class:`AutoOrderedDict` - the ordered version

    References:
        .. [SO_651794] http://stackoverflow.com/questions/651794/init-dict-of-dicts

    Example:
        >>> import ubelt as ub
        >>> auto = ub.AutoDict()
        >>> auto[0][10][100] = None
        >>> assert str(auto) == '{0: {10: {100: None}}}'
    """
    _base = dict

    def __getitem__(self, key):
        try:
            # value = super(AutoDict, self).__getitem__(key)
            value = self._base.__getitem__(self, key)
        except KeyError:
            value = self[key] = type(self)()
        return value

    def to_dict(self):
        """
        Recursively casts a AutoDict into a regular dictionary. All nested
        AutoDict values are also converted.

        Returns:
            dict: a copy of this dict without autovivification

        Example:
            >>> from ubelt.util_dict import AutoDict
            >>> auto = AutoDict()
            >>> auto[1] = 1
            >>> auto['n1'] = AutoDict()
            >>> static = auto.to_dict()
            >>> assert not isinstance(static, AutoDict)
            >>> assert not isinstance(static['n1'], AutoDict)
        """
        return self._base(
            (key, (value.to_dict() if isinstance(value, AutoDict) else value))
            for key, value in self.items())


class AutoOrderedDict(OrderedDict, AutoDict):
    """
    An infinitely nested default dict of dicts that maintains the ordering
    of items.

    SeeAlso:
        :class:`AutoDict` - the unordered version of this class

    Example:
        >>> import ubelt as ub
        >>> auto = ub.AutoOrderedDict()
        >>> auto[0][3] = 3
        >>> auto[0][2] = 2
        >>> auto[0][1] = 1
        >>> assert list(auto[0].values()) == [3, 2, 1]
    """
    _base = OrderedDict


def dzip(items1, items2, cls=dict):
    """
    Zips elementwise pairs between items1 and items2 into a dictionary.

    Values from items2 can be broadcast onto items1.

    Args:
        items1 (Iterable[KT]): full sequence

        items2 (Iterable[VT]):
            can either be a sequence of one item or a sequence of equal length
            to ``items1``

        cls (Type[dict], default=dict): dictionary type to use.

    Returns:
        Dict[KT, VT]: similar to ``dict(zip(items1, items2))``.

    Example:
        >>> import ubelt as ub
        >>> assert ub.dzip([1, 2, 3], [4]) == {1: 4, 2: 4, 3: 4}
        >>> assert ub.dzip([1, 2, 3], [4, 4, 4]) == {1: 4, 2: 4, 3: 4}
        >>> assert ub.dzip([], [4]) == {}
    """
    try:
        len(items1)
    except TypeError:
        items1 = list(items1)
    try:
        len(items2)
    except TypeError:
        items2 = list(items2)
    if len(items1) == 0 and len(items2) == 1:
        # Corner case:
        # allow the first list to be empty and the second list to broadcast a
        # value. This means that the equality check won't work for the case
        # where items1 and items2 are supposed to correspond, but the length of
        # items2 is 1.
        items2 = []
    if len(items2) == 1 and len(items1) > 1:
        items2 = items2 * len(items1)
    if len(items1) != len(items2):
        raise ValueError('out of alignment len(items1)=%r, len(items2)=%r' % (
            len(items1), len(items2)))
    return cls(zip(items1, items2))


def group_items(items, key):
    """
    Groups a list of items by group id.

    Args:
        items (Iterable[VT]): a list of items to group

        key (Iterable[KT] | Callable[[VT], KT]):
            either a corresponding list of group-ids for each item or
            a function used to map each item to a group-id.

    Returns:
        dict[KT, List[VT]]:
            a mapping from each group id to the list of corresponding items

    Example:
        >>> import ubelt as ub
        >>> items    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'banana']
        >>> groupids = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
        >>> id_to_items = ub.group_items(items, groupids)
        >>> print(ub.repr2(id_to_items, nl=0))
        {'dairy': ['cheese'], 'fruit': ['jam', 'banana'], 'protein': ['ham', 'spam', 'eggs']}
    """
    if callable(key):
        keyfunc = key
        pair_list = ((keyfunc(item), item) for item in items)
    else:
        pair_list = zip(key, items)

    # Initialize a dict of lists
    id_to_items = defaultdict(list)
    # Insert each item into the correct group
    for key, item in pair_list:
        id_to_items[key].append(item)
    return id_to_items


def dict_hist(items, weights=None, ordered=False, labels=None):
    """
    Builds a histogram of items, counting the number of time each item appears
    in the input.

    Args:
        items (Iterable[T]):
            hashable items (usually containing duplicates)

        weights (Iterable[float], default=None):
            Corresponding weights for each item.

        ordered (bool, default=False):
            If True the result is ordered by frequency.

        labels (Iterable[T], default=None):
            Expected labels.  Allows this function to pre-initialize the
            histogram.  If specified the frequency of each label is initialized
            to zero and ``items`` can only contain items specified in labels.

    Returns:
        dict[T, int] :
            dictionary where the keys are unique elements from ``items``, and
            the values are the number of times the item appears in ``items``.

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist = ub.dict_hist(items)
        >>> print(ub.repr2(hist, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist1 = ub.dict_hist(items)
        >>> hist2 = ub.dict_hist(items, ordered=True)
        >>> try:
        >>>     hist3 = ub.dict_hist(items, labels=[])
        >>> except KeyError:
        >>>     pass
        >>> else:
        >>>     raise AssertionError('expected key error')
        >>> weights = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1]
        >>> hist4 = ub.dict_hist(items, weights=weights)
        >>> print(ub.repr2(hist1, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}
        >>> print(ub.repr2(hist4, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 1, 1232: 0}
    """
    if labels is None:
        hist_ = defaultdict(lambda: 0)
    else:
        hist_ = {k: 0 for k in labels}
    if weights is None:
        weights = it.repeat(1)
    # Accumulate frequency
    for item, weight in zip(items, weights):
        hist_[item] += weight
    if ordered:
        # Order by value
        getval = op.itemgetter(1)
        hist = OrderedDict([
            (key, value)
            for (key, value) in sorted(hist_.items(), key=getval)
        ])
    else:
        # Cast to a normal dictionary
        hist = dict(hist_)
    return hist


def find_duplicates(items, k=2, key=None):
    """
    Find all duplicate items in a list.

    Search for all items that appear more than ``k`` times and return a mapping
    from each (k)-duplicate item to the positions it appeared in.

    Args:
        items (Iterable[T]):
            hashable items possibly containing duplicates

        k (int, default=2):
            only return items that appear at least ``k`` times.

        key (Callable[[T], Any], default=None):
            Returns indices where `key(items[i])` maps to a particular value at
            least k times.

    Returns:
        dict[T, List[int]] :
            maps each duplicate item to the indices at which it appears

    Notes:
        Similar to :func:`more_itertools.duplicates_everseen`,
        :func:`more_itertools.duplicates_justseen`.

    Example:
        >>> import ubelt as ub
        >>> items = [0, 0, 1, 2, 3, 3, 0, 12, 2, 9]
        >>> duplicates = ub.find_duplicates(items)
        >>> # Duplicates are a mapping from each item that occurs 2 or more
        >>> # times to the indices at which they occur.
        >>> assert duplicates == {0: [0, 1, 6], 2: [3, 8], 3: [4, 5]}
        >>> # You can set k=3 if you want to don't mind duplicates but you
        >>> # want to find triplicates or quadruplets etc.
        >>> assert ub.find_duplicates(items, k=3) == {0: [0, 1, 6]}

    Example:
        >>> import ubelt as ub
        >>> items = [0, 0, 1, 2, 3, 3, 0, 12, 2, 9]
        >>> # note: k can less then 2
        >>> duplicates = ub.find_duplicates(items, k=0)
        >>> print(ub.repr2(duplicates, nl=0))
        {0: [0, 1, 6], 1: [2], 2: [3, 8], 3: [4, 5], 9: [9], 12: [7]}

    Example:
        >>> import ubelt as ub
        >>> items = [10, 11, 12, 13, 14, 15, 16]
        >>> duplicates = ub.find_duplicates(items, key=lambda x: x // 2)
        >>> print(ub.repr2(duplicates, nl=0))
        {5: [0, 1], 6: [2, 3], 7: [4, 5]}
    """
    # Build mapping from items to the indices at which they appear
    duplicates = defaultdict(list)
    if key is None:
        for count, item in enumerate(items):
            duplicates[item].append(count)
    else:
        for count, item in enumerate(items):
            duplicates[key(item)].append(count)
    # remove items seen fewer than k times.
    for key in list(duplicates.keys()):
        if len(duplicates[key]) < k:
            del duplicates[key]
    duplicates = dict(duplicates)
    return duplicates


def dict_subset(dict_, keys, default=util_const.NoParam, cls=OrderedDict):
    """
    Get a subset of a dictionary

    Args:
        dict_ (Dict[KT, VT]): superset dictionary

        keys (Iterable[KT]): keys to take from ``dict_``

        default (Optional[object] | util_const._NoParamType):
            if specified uses default if keys are missing.

        cls (Type[Dict], default=OrderedDict): type of the returned dictionary.

    Returns:
        Dict[KT, VT]: subset dictionary

    SeeAlso:
        :func:`dict_isect` - similar functionality, but ignores missing keys

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
        >>> keys = ['K', 'dcvs_clip_max']
        >>> subdict_ = ub.dict_subset(dict_, keys)
        >>> print(ub.repr2(subdict_, nl=0))
        {'K': 3, 'dcvs_clip_max': 0.2}
    """
    keys = list(keys)
    items = util_list.take(dict_, keys, default)
    subdict_ = cls(list(zip(keys, items)))
    return subdict_


def dict_union(*args):
    """
    Dictionary set extension for ``set.union``

    Combines the disjoint keys in multiple dictionaries. For intersecting keys,
    dictionaries towards the end of the sequence are given precedence.

    Args:
        *args (List[Dict]) : a sequence of dictionaries

    Returns:
        Dict | OrderedDict :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    SeeAlso:
        :func:`collections.ChainMap` - a standard python builtin data structure
        that provides a view that treats multiple dicts as a single dict.
        `<https://docs.python.org/3/library/collections.html#chainmap-objects>`_

    Example:
        >>> import ubelt as ub
        >>> result = ub.dict_union({'a': 1, 'b': 1}, {'b': 2, 'c': 2})
        >>> assert result == {'a': 1, 'b': 2, 'c': 2}
        >>> ub.dict_union(
        >>>     ub.odict([('a', 1), ('b', 2)]),
        >>>     ub.odict([('c', 3), ('d', 4)]))
        OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        >>> ub.dict_union()
        {}
    """
    if not args:
        return {}
    else:
        dictclass = OrderedDict if isinstance(args[0], OrderedDict) else dict
        return dictclass(it.chain.from_iterable(d.items() for d in args))


def dict_diff(*args):
    """
    Dictionary set extension for :func:`set.difference`

    Constructs a dictionary that contains any of the keys in the first arg,
    which are not in any of the following args.

    Args:
        *args (List[Dict[KT, VT] | Iterable[KT]]) :
            A sequence of dictionaries (or sets of keys). The first argument
            should always be a dictionary, but the subsequent arguments can
            just be sets of keys.

    Returns:
        Dict[KT, VT] | OrderedDict[KT, VT] :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    TODO:
        - [ ] Add inplace keyword argument, which modifies the first dictionary
          inplace.

    Example:
        >>> import ubelt as ub
        >>> ub.dict_diff({'a': 1, 'b': 1}, {'a'}, {'c'})
        {'b': 1}
        >>> ub.dict_diff(odict([('a', 1), ('b', 2)]), odict([('c', 3)]))
        OrderedDict([('a', 1), ('b', 2)])
        >>> ub.dict_diff()
        {}
        >>> ub.dict_diff({'a': 1, 'b': 2}, {'c'})
    """
    if not args:
        return {}
    else:
        first_dict = args[0]
        dictclass = OrderedDict if isinstance(first_dict, OrderedDict) else dict
        # remove_keys = set.union(*map(set, args[1:]))
        # new = dictclass((k, v) for k, v in first_dict.items() if k not in remove_keys)
        remove_keys = set.union(*map(set, args[1:]))
        new = dictclass((k, first_dict[k]) for k in first_dict.keys() if k not in remove_keys)
        return new


def dict_isect(*args):
    """
    Dictionary set extension for :func:`set.intersection`

    Constructs a dictionary that contains keys common between all inputs.
    The returned values will only belong to the first dictionary.

    Args:
        *args (List[Dict[KT, VT] | Iterable[KT]]) :
            A sequence of dictionaries (or sets of keys). The first argument
            should always be a dictionary, but the subsequent arguments can
            just be sets of keys.

    Returns:
        Dict[KT, VT] | OrderedDict[KT, VT] :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    Note:
        This function can be used as an alternative to :func:`dict_subset`
        where any key not in the dictionary is ignored. See the following
        example:

        >>> import ubelt as ub
        >>> # xdoctest: +IGNORE_WANT
        >>> ub.dict_isect({'a': 1, 'b': 2, 'c': 3}, ['a', 'c', 'd'])
        {'a': 1, 'c': 3}

    Example:
        >>> import ubelt as ub
        >>> ub.dict_isect({'a': 1, 'b': 1}, {'b': 2, 'c': 2})
        {'b': 1}
        >>> ub.dict_isect(odict([('a', 1), ('b', 2)]), odict([('c', 3)]))
        OrderedDict()
        >>> ub.dict_isect()
        {}
    """
    if not args:
        return {}
    else:
        dictclass = OrderedDict if isinstance(args[0], OrderedDict) else dict
        common_keys = set.intersection(*map(set, args))
        first_dict = args[0]
        return dictclass((k, first_dict[k]) for k in first_dict
                         if k in common_keys)


def map_vals(func, dict_):
    """
    Apply a function to every value in a dictionary.

    Creates a new dictionary with the same keys and modified values.

    Args:
        func (Callable[[VT], T] | Mapping[VT, T]): a function or indexable object
        dict_ (Dict[KT, VT]): a dictionary

    Returns:
        Dict[KT, T]: transformed dictionary

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': [1, 2, 3], 'b': []}
        >>> newdict = ub.map_vals(len, dict_)
        >>> assert newdict ==  {'a': 3, 'b': 0}

    Example:
        >>> # Can also use an indexable as ``func``
        >>> import ubelt as ub
        >>> dict_ = {'a': 0, 'b': 1}
        >>> func = [42, 21]
        >>> newdict = ub.map_vals(func, dict_)
        >>> assert newdict ==  {'a': 42, 'b': 21}
        >>> print(newdict)
    """
    if not hasattr(func, '__call__'):
        func = func.__getitem__
    keyval_list = [(key, func(val)) for key, val in dict_.items()]
    dictclass = OrderedDict if isinstance(dict_, OrderedDict) else dict
    newdict = dictclass(keyval_list)
    return newdict


def map_keys(func, dict_):
    """
    Apply a function to every key in a dictionary.

    Creates a new dictionary with the same values and modified keys. An error
    is raised if the new keys are not unique.

    Args:
        func (Callable[[KT], T] | Mapping[KT, T]): a function or indexable object
        dict_ (Dict[KT, VT]): a dictionary

    Returns:
        Dict[T, VT]: transformed dictionary

    Raises:
        Exception : if multiple keys map to the same value

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': [1, 2, 3], 'b': []}
        >>> func = ord
        >>> newdict = ub.map_keys(func, dict_)
        >>> print(newdict)
        >>> assert newdict == {97: [1, 2, 3], 98: []}
        >>> dict_ = {0: [1, 2, 3], 1: []}
        >>> func = ['a', 'b']
        >>> newdict = ub.map_keys(func, dict_)
        >>> print(newdict)
        >>> assert newdict == {'a': [1, 2, 3], 'b': []}
    """
    if not hasattr(func, '__call__'):
        func = func.__getitem__
    keyval_list = [(func(key), val) for key, val in dict_.items()]
    dictclass = OrderedDict if isinstance(dict_, OrderedDict) else dict
    newdict = dictclass(keyval_list)
    if len(newdict) != len(dict_):
        raise Exception('multiple input keys mapped to the same output key')
    return newdict


def sorted_vals(dict_, key=None, reverse=False):
    """
    Return an ordered dictionary sorted by its values

    Args:
        dict_ (Dict[KT, VT]):
            dictionary to sort. The values must be of comparable types.

        key (Callable[[VT], Any] | None):
            If given as a callable, customizes the sorting by ordering using
            transformed values.

        reverse (bool, default=False):
            if True returns in descending order

    Returns:
        OrderedDict[KT, VT]: new dictionary where the values are ordered

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'spam': 2.62, 'eggs': 1.20, 'jam': 2.92}
        >>> newdict = sorted_vals(dict_)
        >>> print(ub.repr2(newdict, nl=0))
        {'eggs': 1.2, 'spam': 2.62, 'jam': 2.92}
        >>> newdict = sorted_vals(dict_, reverse=True)
        >>> print(ub.repr2(newdict, nl=0))
        {'jam': 2.92, 'spam': 2.62, 'eggs': 1.2}
        >>> newdict = sorted_vals(dict_, key=lambda x: x % 1.6)
        >>> print(ub.repr2(newdict, nl=0))
        {'spam': 2.62, 'eggs': 1.2, 'jam': 2.92}
    """
    if key is None:
        newdict = OrderedDict(sorted(dict_.items(), key=lambda kv: kv[1],
                                     reverse=reverse))
    else:
        newdict = OrderedDict(sorted(dict_.items(), key=lambda kv: key(kv[1]),
                                     reverse=reverse))
    return newdict


sorted_values = sorted_vals  # ? Is this a better name?


def sorted_keys(dict_, key=None, reverse=False):
    """
    Return an ordered dictionary sorted by its keys

    Args:
        dict_ (Dict[KT, VT]):
            dictionary to sort. The keys must be of comparable types.

        key (Callable[[KT], Any] | None):
            If given as a callable, customizes the sorting by ordering using
            transformed keys.

        reverse (bool, default=False):
            if True returns in descending order

    Returns:
        OrderedDict[KT, VT]: new dictionary where the keys are ordered

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'spam': 2.62, 'eggs': 1.20, 'jam': 2.92}
        >>> newdict = sorted_keys(dict_)
        >>> print(ub.repr2(newdict, nl=0))
        {'eggs': 1.2, 'jam': 2.92, 'spam': 2.62}
        >>> newdict = sorted_keys(dict_, reverse=True)
        >>> print(ub.repr2(newdict, nl=0))
        {'spam': 2.62, 'jam': 2.92, 'eggs': 1.2}
        >>> newdict = sorted_keys(dict_, key=lambda x: sum(map(ord, x)))
        >>> print(ub.repr2(newdict, nl=0))
        {'jam': 2.92, 'eggs': 1.2, 'spam': 2.62}
    """
    if key is None:
        newdict = OrderedDict(sorted(dict_.items(), key=lambda kv: kv[0],
                                     reverse=reverse))
    else:
        newdict = OrderedDict(sorted(dict_.items(), key=lambda kv: key(kv[0]),
                                     reverse=reverse))
    return newdict


def invert_dict(dict_, unique_vals=True):
    """
    Swaps the keys and values in a dictionary.

    Args:
        dict_ (Dict[KT, VT]): dictionary to invert

        unique_vals (bool, default=True): if False, the values of the new
            dictionary are sets of the original keys.

    Returns:
        Dict[VT, KT] | Dict[VT, Set[KT]]:
            the inverted dictionary

    Note:
        The must values be hashable.

        If the original dictionary contains duplicate values, then only one of
        the corresponding keys will be returned and the others will be
        discarded.  This can be prevented by setting ``unique_vals=False``,
        causing the inverted keys to be returned in a set.

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': 1, 'b': 2}
        >>> inverted = ub.invert_dict(dict_)
        >>> assert inverted == {1: 'a', 2: 'b'}

    Example:
        >>> import ubelt as ub
        >>> dict_ = ub.odict([(2, 'a'), (1, 'b'), (0, 'c'), (None, 'd')])
        >>> inverted = ub.invert_dict(dict_)
        >>> assert list(inverted.keys())[0] == 'a'

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': 1, 'b': 0, 'c': 0, 'd': 0, 'f': 2}
        >>> inverted = ub.invert_dict(dict_, unique_vals=False)
        >>> assert inverted == {0: {'b', 'c', 'd'}, 1: {'a'}, 2: {'f'}}
    """
    if unique_vals:
        if isinstance(dict_, OrderedDict):
            inverted = OrderedDict((val, key) for key, val in dict_.items())
        else:
            inverted = {val: key for key, val in dict_.items()}
    else:
        # Handle non-unique keys using groups
        inverted = defaultdict(set)
        for key, value in dict_.items():
            inverted[value].add(key)
        inverted = dict(inverted)
    return inverted


def named_product(_=None, **basis):
    """
    Generates the Cartesian product of the ``basis.values()``, where each
    generated item labeled by ``basis.keys()``.

    In other words, given a dictionary that maps each "axes" (i.e. some
    variable) to its "basis" (i.e. the possible values that it can take),
    generate all possible points in that grid (i.e. unique assignments of
    variables to values).

    Args:
        _ (Dict[str, List[VT]] | None, default=None):
            Use of this positional argument is not recommend. Instead specify
            all arguments as keyword args.

            If specified, this should be a dictionary is unioned with the
            keyword args.  This exists to support ordered dictionaries before
            Python 3.6, and may eventually be removed.

        basis (Dict[str, List[VT]]):
            A dictionary where the keys correspond to "columns" and the values
            are a list of possible values that "column" can take.

            I.E. each key corresponds to an "axes", the values are the list of
            possible values for that "axes".

    Yields:
        Dict[str, VT] :
            a "row" in the "longform" data containing a point in the Cartesian
            product.

    Note:
        This function is similar to :func:`itertools.product`, the only
        difference is that the generated items are a dictionary that retains
        the input keys instead of an tuple.

        This function used to be called "basis_product", but "named_product"
        might be more appropriate. This function exists in other places
        ([minstrel271_namedproduct]_, [pytb_namedproduct]_, and
        [Hettinger_namedproduct]_).

    References:
        .. [minstrel271_namedproduct] https://gist.github.com/minstrel271/d51654af3fa4e6411267
        .. [pytb_namedproduct] https://py-toolbox.readthedocs.io/en/latest/modules/itertools.html#
        .. [Hettinger_namedproduct] https://twitter.com/raymondh/status/970380630822305792

    Example:
        >>> # An example use case is looping over all possible settings in a
        >>> # configuration dictionary for a grid search over parameters.
        >>> import ubelt as ub
        >>> basis = {
        >>>     'arg1': [1, 2, 3],
        >>>     'arg2': ['A1', 'B1'],
        >>>     'arg3': [9999, 'Z2'],
        >>>     'arg4': ['always'],
        >>> }
        >>> import ubelt as ub
        >>> # sort input data for older python versions
        >>> basis = ub.odict(sorted(basis.items()))
        >>> got = list(ub.named_product(basis))
        >>> print(ub.repr2(got, nl=-1))
        [
            {'arg1': 1, 'arg2': 'A1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 1, 'arg2': 'A1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 1, 'arg2': 'B1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 1, 'arg2': 'B1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'A1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'A1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'B1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'B1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'A1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'A1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'B1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'B1', 'arg3': 'Z2', 'arg4': 'always'}
        ]

    Example:
        >>> import ubelt as ub
        >>> list(ub.named_product(a=[1, 2, 3]))
        [{'a': 1}, {'a': 2}, {'a': 3}]
        >>> # xdoctest: +IGNORE_WANT
        >>> list(ub.named_product(a=[1, 2, 3], b=[4, 5]))
        [{'a': 1, 'b': 4},
         {'a': 1, 'b': 5},
         {'a': 2, 'b': 4},
         {'a': 2, 'b': 5},
         {'a': 3, 'b': 4},
         {'a': 3, 'b': 5}]
    """
    # Handle one positional argument.
    if _ is not None:
        _basis = _
        _basis.update(basis)
        basis = _basis
    keys = list(basis.keys())
    for vals in it.product(*basis.values()):
        kw = dict(zip(keys, vals))
        yield kw


def varied_values(longform, min_variations=0, default=NoParam):
    """
    Given a list of dictionaries, find the values that differ between them.

    Args:
        longform (List[Dict[KT, VT]]):
            This is longform data, as described in [SeabornLongform]_. It is a
            list of dictionaries.

            Each item in the list - or row - is a dictionary and can be thought
            of as an observation. The keys in each dictionary are the columns.
            The values of the dictionary must be hashable. Lists will be
            converted into tuples.

        min_variations (int, default=0):
            "columns" with fewer than ``min_variations`` unique values are
            removed from the result.

        default (VT, default=NoParam):
            if specified, unspecified columns are given this value.

    Returns:
        Dict[KT, List[VT]] :
            a mapping from each "column" to the set of unique values it took
            over each "row". If a column is not specified for each row, it is
            assumed to take a `default` value, if it is specified.

    Raises:
        KeyError: If ``default`` is unspecified and all the rows
            do not contain the same columns.

    References:
        .. [SeabornLongform] https://seaborn.pydata.org/tutorial/data_structure.html#long-form-data

    Example:
        >>> # An example use case is to determine what values of a
        >>> # configuration dictionary were tried in a random search
        >>> # over a parameter grid.
        >>> import ubelt as ub
        >>> longform = [
        >>>     {'col1': 1, 'col2': 'foo', 'col3': None},
        >>>     {'col1': 1, 'col2': 'foo', 'col3': None},
        >>>     {'col1': 2, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 3, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 9, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 1, 'col2': 'bar', 'col3': None},
        >>> ]
        >>> varied = ub.varied_values(longform)
        >>> print('varied = {}'.format(ub.repr2(varied, nl=1)))
        varied = {
            'col1': {1, 2, 3, 9},
            'col2': {'bar', 'foo'},
            'col3': {None},
        }

    Example:
        >>> import ubelt as ub
        >>> import random
        >>> longform = [
        >>>     {'col1': 1, 'col2': 'foo', 'col3': None},
        >>>     {'col1': 1, 'col2': [1, 2], 'col3': None},
        >>>     {'col1': 2, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 3, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 9, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 1, 'col2': 'bar', 'col3': None, 'extra_col': 3},
        >>> ]
        >>> # Operation fails without a default
        >>> import pytest
        >>> with pytest.raises(KeyError):
        >>>     varied = ub.varied_values(longform)
        >>> #
        >>> # Operation works with a default
        >>> varied = ub.varied_values(longform, default='<unset>')
        >>> expected = {
        >>>     'col1': {1, 2, 3, 9},
        >>>     'col2': {'bar', 'foo', (1, 2)},
        >>>     'col3': set([None]),
        >>>     'extra_col': {'<unset>', 3},
        >>> }
        >>> print('varied = {!r}'.format(varied))
        >>> assert varied == expected

    Example:
        >>> # xdoctest: +REQUIRES(PY3)
        >>> # Random numbers are different in Python2, so skip in that case
        >>> import ubelt as ub
        >>> import random
        >>> num_cols = 11
        >>> num_rows = 17
        >>> rng = random.Random(0)
        >>> # Generate a set of columns
        >>> columns = sorted(ub.hash_data(i)[0:8] for i in range(num_cols))
        >>> # Generate rows for each column
        >>> longform = [
        >>>     {key: ub.hash_data(key)[0:8] for key in columns}
        >>>     for _ in range(num_rows)
        >>> ]
        >>> # Add in some varied values in random positions
        >>> for row in longform:
        >>>     if rng.random() > 0.5:
        >>>         for key in sorted(row.keys()):
        >>>             if rng.random() > 0.95:
        >>>                 row[key] = 'special-' + str(rng.randint(1, 32))
        >>> varied = ub.varied_values(longform, min_variations=1)
        >>> print('varied = {}'.format(ub.repr2(varied, nl=1, sort=True)))
        varied = {
            '095f3e44': {'8fb4d4c9', 'special-23'},
            '365d11a1': {'daa409da', 'special-31', 'special-32'},
            '5815087d': {'1b823610', 'special-3'},
            '7b54b668': {'349a782c', 'special-10'},
            'b8244d02': {'d57bca90', 'special-8'},
            'f27b5bf8': {'fa0f90d1', 'special-19'},
        }
    """
    # Enumerate all defined columns
    columns = set()
    for row in longform:
        if default is NoParam and len(row) != len(columns) and len(columns):
            missing = set(columns).symmetric_difference(set(row))
            raise KeyError((
                'No default specified and not every '
                'row contains columns {}').format(missing))
        columns.update(row.keys())

    # Build up the set of unique values for each column
    varied = ddict(set)
    for row in longform:
        for key in columns:
            value = row.get(key, default)
            if isinstance(value, list):
                value = tuple(value)
            varied[key].add(value)

    # Remove any column that does not have enough variation
    if min_variations > 0:
        for key, values in list(varied.items()):
            if len(values) <= min_variations:
                varied.pop(key)
    return varied
