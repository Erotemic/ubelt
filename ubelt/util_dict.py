"""
Functions for working with dictionaries.

The :class:`UDict` is a subclass of :class:`dict` with quality of life
improvements. It contains methods for n-ary key-wise set operations as well as
support for the binary operators in addition to other methods for mapping,
inversion, subdicts, and peeking. It can be accessed via the alias
``ubelt.udict``.

The :class:`SetDict` only contains the key-wise set extensions to dict. It can
be accessed via the alias ``ubelt.sdict``.

The :func:`dict_hist` function counts the number of discrete occurrences of hashable
items. Similarly :func:`find_duplicates` looks for indices of items that occur more
than `k=1` times.

The :func:`map_keys` and :func:`map_values` functions are useful for
transforming the keys and values of a dictionary with less syntax than a dict
comprehension.

The :func:`dict_union`, :func:`dict_isect`, and :func:`dict_diff` functions are
similar to the set equivalents.

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

Related Work:
    * Note that Python does support set operations on dictionary **views** [DictView]_ [Pep3106]_, but these methods can be inflexible and often leave you only with keys (and no dictionary subset operation), whereas the ubelt definition of these operations is more straightforward.
    * There are several recipes for dictionaries that support set operations [SetDictRecipe1]_ [SetDictRecipe2]_.
    * The :py:mod:`dictmap` package contains a function similar to :func:`map_values` [GHDictMap]_.
    * The :py:mod:`dictdiffer` package contains tools for nested difference operations [PypiDictDiffer]_.
    * There are lots of other python dictionary utility libraries [PyPIAddict]_.

References:
    .. [PyPIAddict] https://github.com/mewwts/addict
    .. [SetDictRecipe1] https://gist.github.com/rossmacarthur/38fa948b175abb512e12c516cc3b936d
    .. [SetDictRecipe2] https://code.activestate.com/recipes/577471-setdict/
    .. [PypiDictDiffer] https://pypi.org/project/dictdiffer/
    .. [DictView] https://docs.python.org/3.0/library/stdtypes.html#dictionary-view-objects
    .. [Pep3106] https://peps.python.org/pep-3106/
    .. [GHDictMap] https://github.com/ulisesojeda/dictionary_map
"""
import sys
import operator as op
import itertools as it
from collections import OrderedDict
from collections import defaultdict
# from ubelt import util_const
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
    'map_values',
    'sorted_keys',
    'sorted_vals',
    'sorted_values',
    'odict',
    'named_product',
    'varied_values',
    'SetDict',
    'UDict',
    'sdict',
    'udict',
]


# Expose for convenience
odict = OrderedDict
ddict = defaultdict


# Use an ordered dictionary in < 3.7 as the base

if sys.version_info[0:2] <= (3, 6):  # nocover
    DictBase = OrderedDict
else:  # nocover
    DictBase = dict


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
            Corresponding weights for each item, defaults to 1 if unspecified.

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

    SeeAlso:
        :class:`collections.Counter`

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist = ub.dict_hist(items)
        >>> print(ub.repr2(hist, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}

    Example:
        >>> import ubelt as ub
        >>> import pytest
        >>> items = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist1 = ub.dict_hist(items)
        >>> hist2 = ub.dict_hist(items, ordered=True)
        >>> with pytest.raises(KeyError):
        >>>     hist3 = ub.dict_hist(items, labels=[])
        >>> weights = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1]
        >>> hist4 = ub.dict_hist(items, weights=weights)
        >>> print(ub.repr2(hist1, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}
        >>> print(ub.repr2(hist4, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 1, 1232: 0}
    """
    if weights is None and labels is None:
        # Accumulate discrete frequency.
        # In this special case we use an optimized stdlib routine
        from collections import Counter
        hist_ = Counter()
        hist_.update(items)
    else:
        if labels is None:
            hist_ = defaultdict(lambda: 0)
        else:
            hist_ = {k: 0 for k in labels}
        if weights is None:
            weights = it.repeat(1)  # 2x slower than Counter
        # Accumulate weighted frequency
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


def dict_subset(dict_, keys, default=NoParam, cls=OrderedDict):
    """
    Get a subset of a dictionary

    Args:
        dict_ (Dict[KT, VT]): superset dictionary

        keys (Iterable[KT]): keys to take from ``dict_``

        default (Optional[object] | NoParamType):
            if specified uses default if keys are missing.

        cls (Type[Dict], default=OrderedDict): type of the returned dictionary.

    Returns:
        Dict[KT, VT]: subset dictionary

    SeeAlso:
        :func:`dict_isect` - similar functionality, but ignores missing keys
        ::py:meth:`UDict.subdict` - object oriented version of this function

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
        >>> keys = ['K', 'dcvs_clip_max']
        >>> subdict_ = ub.dict_subset(dict_, keys)
        >>> print(ub.repr2(subdict_, nl=0))
        {'K': 3, 'dcvs_clip_max': 0.2}
    """
    from ubelt import util_list
    keys = list(keys)
    items = util_list.take(dict_, keys, default)
    subdict_ = cls(list(zip(keys, items)))
    return subdict_


def dict_union(*args):
    """
    Dictionary set extension for ``set.union``

    Combines items with from multiple dictionaries.  For items with
    intersecting keys, dictionaries towards the end of the sequence are given
    precedence.

    Args:
        *args (List[Dict]) : A sequence of dictionaries.
            Values are taken from the last

    Returns:
        Dict | OrderedDict :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    Notes:
        In Python 3.8+, the bitwise or operator "|" operator performs a similar
        operation, but as of 2022-06-01 there is still no public method for
        dictionary union (or any other dictionary set operator).

    References:
        https://stackoverflow.com/questions/38987/merge-two-dict

    SeeAlso:
        :func:`collections.ChainMap` - a standard python builtin data structure
        that provides a view that treats multiple dicts as a single dict.
        `<https://docs.python.org/3/library/collections.html#chainmap-objects>`_
        ::py:meth:`UDict.union` - object oriented version of this function

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

    SeeAlso:
        ::py:meth:`UDict.difference` - object oriented version of this function

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

    SeeAlso:
        ::py:meth:`UDict.intersection` - object oriented version of this function

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


def map_values(func, dict_, cls=None):
    """
    Apply a function to every value in a dictionary.

    Creates a new dictionary with the same keys and modified values.

    Args:
        func (Callable[[VT], T] | Mapping[VT, T]): a function or indexable object
        dict_ (Dict[KT, VT]): a dictionary
        cls (type | None): specifies the dict subclassof the result.
            if unspecified will be dict or OrderedDict. This behavior may
            change.

    SeeAlso:
        ::py:meth:`UDict.map_values` - object oriented version of this function

    Returns:
        Dict[KT, T]: transformed dictionary

    Notes:
        Similar to :py:mod:`dictmap.dict_map`

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': [1, 2, 3], 'b': []}
        >>> newdict = ub.map_values(len, dict_)
        >>> assert newdict ==  {'a': 3, 'b': 0}

    Example:
        >>> # Can also use an indexable as ``func``
        >>> import ubelt as ub
        >>> dict_ = {'a': 0, 'b': 1}
        >>> func = [42, 21]
        >>> newdict = ub.map_values(func, dict_)
        >>> assert newdict ==  {'a': 42, 'b': 21}
        >>> print(newdict)
    """
    if not hasattr(func, '__call__'):
        func = func.__getitem__
    keyval_list = [(key, func(val)) for key, val in dict_.items()]
    if cls is None:
        cls = OrderedDict if isinstance(dict_, OrderedDict) else dict
    newdict = cls(keyval_list)
    return newdict

map_vals = map_values  # backwards compatibility


def map_keys(func, dict_, cls=None):
    """
    Apply a function to every key in a dictionary.

    Creates a new dictionary with the same values and modified keys. An error
    is raised if the new keys are not unique.

    Args:
        func (Callable[[KT], T] | Mapping[KT, T]): a function or indexable object
        dict_ (Dict[KT, VT]): a dictionary
        cls (type | None): specifies the dict subclassof the result.
            if unspecified will be dict or OrderedDict. This behavior may
            change.

    SeeAlso:
        ::py:meth:`UDict.map_keys` - object oriented version of this function

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
    if cls is None:
        cls = OrderedDict if isinstance(dict_, OrderedDict) else dict
    newdict = cls(keyval_list)
    if len(newdict) != len(dict_):
        raise Exception('multiple input keys mapped to the same output key')
    return newdict


def sorted_values(dict_, key=None, reverse=False, cls=OrderedDict):
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

        cls (type): specifies the dict return type

    SeeAlso:
        ::py:meth:`UDict.sorted_values` - object oriented version of this function

    Returns:
        OrderedDict[KT, VT]: new dictionary where the values are ordered

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'spam': 2.62, 'eggs': 1.20, 'jam': 2.92}
        >>> newdict = sorted_values(dict_)
        >>> print(ub.repr2(newdict, nl=0))
        {'eggs': 1.2, 'spam': 2.62, 'jam': 2.92}
        >>> newdict = sorted_values(dict_, reverse=True)
        >>> print(ub.repr2(newdict, nl=0))
        {'jam': 2.92, 'spam': 2.62, 'eggs': 1.2}
        >>> newdict = sorted_values(dict_, key=lambda x: x % 1.6)
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


sorted_vals = sorted_values  # backwards compatibility


def sorted_keys(dict_, key=None, reverse=False, cls=OrderedDict):
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

        cls (type): specifies the dict return type

    SeeAlso:
        ::py:meth:`UDict.sorted_keys` - object oriented version of this function

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


def invert_dict(dict_, unique_vals=True, cls=None):
    """
    Swaps the keys and values in a dictionary.

    Args:
        dict_ (Dict[KT, VT]): dictionary to invert

        unique_vals (bool, default=True): if False, the values of the new
            dictionary are sets of the original keys.

        cls (type | None): specifies the dict subclassof the result.
            if unspecified will be dict or OrderedDict. This behavior may
            change.

    SeeAlso:
        ::py:meth:`UDict.invert` - object oriented version of this function

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
    if cls is None:
        cls = OrderedDict if isinstance(dict_, OrderedDict) else dict
    if unique_vals:
        # Wonder what byte code is better here?
        if cls is dict:
            inverted = {val: key for key, val in dict_.items()}
        else:
            inverted = cls((val, key) for key, val in dict_.items())
    else:
        # Handle non-unique keys using groups
        inverted = defaultdict(set)
        for key, value in dict_.items():
            inverted[value].add(key)
        inverted = cls(inverted)
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

        default (VT | NoParamType):
            if specified, unspecified columns are given this value.
            Defaults to NoParam.

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


class SetDict(dict):
    """
    A dictionary subclass where all set operations are defined.

    All of the set operations are defined in a key-wise fashion, that is it is
    like performing the operation on sets of keys.

    Note:
        The SetDict class only defines key-wise set operations.  Value-wise or
        item-wise operations are in general not hashable and therefore not
        supported. A heavier extension would be needed for that.

    Example:
        >>> import ubelt as ub
        >>> primes = ub.sdict({v: f'prime_{v}' for v in [2, 3, 5, 7, 11]})
        >>> evens = ub.sdict({v: f'even_{v}' for v in [0, 2, 4, 6, 8, 10]})
        >>> odds = ub.sdict({v: f'odd_{v}' for v in [1, 3, 5, 7, 9, 11]})
        >>> squares = ub.sdict({v: f'square_{v}' for v in [0, 1, 4, 9]})
        >>> div3 = ub.sdict({v: f'div3_{v}' for v in [0, 3, 6, 9]})
        >>> # All of the set methods are defined
        >>> results1 = {}
        >>> results1['ints'] = ints = odds.union(evens)
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
        >>> assert results1['ints'] == ub.sdict.union(odds, evens)
        >>> assert results1['composites'] == ub.sdict.difference(ints, primes)
        >>> assert results1['even_primes'] == ub.sdict.intersection(evens, primes)
        >>> assert results1['odd_nonprimes_and_two'] == ub.sdict.symmetric_difference(odds, primes)
        >>> # The narry variants are also implemented
        >>> results2 = {}
        >>> results2['nary_union'] = ub.sdict.union(primes, div3, odds)
        >>> results2['nary_difference'] = ub.sdict.difference(primes, div3, odds)
        >>> results2['nary_intersection'] = ub.sdict.intersection(primes, div3, odds)
        >>> # Note that the definition of symmetric difference might not be what you think in the nary case.
        >>> results2['nary_symmetric_difference'] = ub.sdict.symmetric_difference(primes, div3, odds)
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

    Example:
        >>> # A neat thing about our implementation is that often the right
        >>> # hand side is not required to be a dictionary, just something
        >>> # that can be cast to a set.
        >>> import ubelt as ub
        >>> primes = ub.sdict({2: 'a', 3: 'b', 5: 'c', 7: 'd', 11: 'e'})
        >>> assert primes - {2, 3} == {5: 'c', 7: 'd', 11: 'e'}
        >>> assert primes & {2, 3} == {2: 'a', 3: 'b'}
        >>> # Union does need to have a second dictionary
        >>> import pytest
        >>> with pytest.raises(AttributeError):
        >>>     primes | {2, 3}

    """

    def copy(self):
        """
        Example:
            >>> import ubelt as ub
            >>> a = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> b = ub.udict({1: 1, 2: 2, 3: 3})
            >>> c = a.copy()
            >>> d = b.copy()
            >>> assert c is not a
            >>> assert d is not b
            >>> assert d == b
            >>> assert c == a
            >>> list(map(type, [a, b, c, d]))
            >>> assert isinstance(c, ub.sdict)
            >>> assert isinstance(d, ub.udict)
        """
        return self.__class__(self)

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

    # - reverse versions

    def __ror__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> other = {1: 10, 2:20, 4: 40}
            >>> d1 = self | other
            >>> d2 = other | self
            >>> assert isinstance(d1, ub.SetDict), 'should use own type'
            >>> assert isinstance(d2, ub.SetDict), 'should promote type'
            >>> print(f'd1={d1}')
            >>> print(f'd2={d2}')
            d1={1: 10, 2: 20, 3: 3, 4: 40}
            d2={1: 1, 2: 2, 4: 40, 3: 3}
        """
        return SetDict.union(other, self, cls=self.__class__)

    def __rand__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> other = {1: 10, 2:20, 4: 40}
            >>> d1 = self & other
            >>> d2 = other & self
            >>> assert isinstance(d1, ub.SetDict), 'should use own type'
            >>> assert isinstance(d2, ub.SetDict), 'should promote type'
            >>> print(f'd1={d1}')
            >>> print(f'd2={d2}')
            d1={1: 1, 2: 2}
            d2={1: 10, 2: 20}
        """
        return SetDict.intersection(other, self, cls=self.__class__)

    def __rsub__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> other = {1: 10, 2:20, 4: 40}
            >>> d1 = self - other
            >>> d2 = other - self
            >>> assert isinstance(d1, ub.SetDict), 'should use own type'
            >>> assert isinstance(d2, ub.SetDict), 'should promote type'
            >>> print(f'd1={d1}')
            >>> print(f'd2={d2}')
            d1={3: 3}
            d2={4: 40}
        """
        return SetDict.difference(other, self, cls=self.__class__)

    def __rxor__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> other = {1: 10, 2:20, 4: 40}
            >>> d1 = self ^ other
            >>> d2 = other ^ self
            >>> assert isinstance(d1, ub.SetDict), 'should use own type'
            >>> assert isinstance(d2, ub.SetDict), 'should promote type'
            >>> print(f'd1={d1}')
            >>> print(f'd2={d2}')
            d1={3: 3, 4: 40}
            d2={4: 40, 3: 3}
        """
        return SetDict.symmetric_difference(other, self, cls=self.__class__)

    # - inplace versions

    def __ior__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = orig_ref = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> orig_val = orig_ref.copy()
            >>> other = {1: 10, 2:20, 4: 40}
            >>> self |= other
            >>> print(f'self={self}')
            >>> assert self is orig_ref
            >>> assert self == (orig_val | other)
            self={1: 10, 2: 20, 3: 3, 4: 40}
        """
        self.update(other)
        return self

    def __iand__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = orig_ref = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> orig_val = orig_ref.copy()
            >>> other = {1: 10, 2:20, 4: 40}
            >>> self &= other
            >>> print(f'self={self}')
            >>> assert self is orig_ref
            >>> assert self == (orig_val & other)
            self={1: 1, 2: 2}
        """
        result = self.intersection(other)
        self.clear()
        self.update(result)
        return self

    def __isub__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = orig_ref = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> orig_val = orig_ref.copy()
            >>> other = {1: 10, 2:20}
            >>> self -= other
            >>> print(f'self={self}')
            >>> assert self is orig_ref
            >>> assert self == (orig_val - other)
            self={3: 3}

            >>> import ubelt as ub
            >>> self = orig_ref = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> orig_val = orig_ref.copy()
            >>> other = [1]
            >>> self -= other
            >>> print(f'self={self}')
            >>> assert self is orig_ref
            >>> assert self == (orig_val - other)
            self={2: 2, 3: 3}

            >>> import ubelt as ub
            >>> self = orig_ref = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> orig_val = orig_ref.copy()
            >>> other = {1: 10, 2:20, 4: 40}
            >>> self -= other
            >>> print(f'self={self}')
            >>> assert self is orig_ref
            >>> assert self == (orig_val - other)
        """
        result = self.difference(other)
        self.clear()
        self.update(result)
        # common = UDict.intersection(self, other)
        # for k in common:
        #     self.pop(k, None)
        return self

    def __ixor__(self, other):
        """
        Example:
            >>> import ubelt as ub
            >>> self = orig_ref = ub.sdict({1: 1, 2: 2, 3: 3})
            >>> orig_val = orig_ref.copy()
            >>> other = {1: 10, 2:20, 4: 40}
            >>> self ^= other
            >>> print(f'self={self}')
            >>> assert self is orig_ref
            >>> assert self == (orig_val ^ other)
        """
        result = self.symmetric_difference(other)
        self.clear()
        self.update(result)
        return self

    ### Main set operations

    def union(self, *others, cls=None):
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

            cls (type):
                the desired return dictionary type.

        Returns:
            dict : whatever the dictionary type of the first argument is

        Example:
            >>> import ubelt as ub
            >>> a = ub.SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = ub.SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = ub.SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = ub.SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = ub.SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> assert a | b == {2: 'B_c', 3: 'A_d', 5: 'A_f', 7: 'B_h', 4: 'B_e', 0: 'B_a'}
            >>> a.union(b)
            >>> a | b | c
            >>> res = ub.SetDict.union(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {0: B_a, 2: C_c, 3: C_d, 4: B_e, 5: A_f, 7: B_h, 8: C_i, 9: D_j, 10: D_k, 11: D_l}
        """
        cls = cls or self.__class__
        args = it.chain([self], others)
        new = cls(it.chain.from_iterable(d.items() for d in args))
        return new

    def intersection(self, *others, cls=None):
        """
        Return the key-wise intersection of two or more dictionaries.

        All items returned will be from the first dictionary for keys that
        exist in all other dictionaries / sets provided.

        Args:
            self (SetDict | dict):
                if called as a static method this must be provided.

            *others : other dictionary or set like objects that can
                be coerced into a set of keys.

            cls (type):
                the desired return dictionary type.

        Returns:
            dict : whatever the dictionary type of the first argument is

        Example:
            >>> import ubelt as ub
            >>> a = ub.SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = ub.SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = ub.SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = ub.SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = ub.SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> assert a & b == {2: 'A_c', 7: 'A_h'}
            >>> a.intersection(b)
            >>> a & b & c
            >>> res = ub.SetDict.intersection(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {}
        """
        cls = cls or self.__class__
        isect_keys = set(self.keys())
        for v in others:
            isect_keys.intersection_update(v)
        new = cls((k, self[k]) for k in self if k in isect_keys)
        return new

    def difference(self, *others, cls=None):
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

            cls (type):
                the desired return dictionary type.

        Returns:
            dict : whatever the dictionary type of the first argument is

        Example:
            >>> import ubelt as ub
            >>> a = ub.SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = ub.SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = ub.SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = ub.SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = ub.SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> assert a - b == {3: 'A_d', 5: 'A_f'}
            >>> a.difference(b)
            >>> a - b - c
            >>> res = ub.SetDict.difference(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {5: A_f}
        """
        cls = cls or self.__class__
        other_keys = set()
        for v in others:
            other_keys.update(v)
        # Looping over original keys is important to maintain partial order.
        new = cls((k, self[k]) for k in self.keys() if k not in other_keys)
        return new

    def symmetric_difference(self, *others, cls=None):
        """
        Return the key-wise symmetric difference between this dictionary and
        one or more other dictionaries.

        Returns items that are (key-wise) in an odd number of the given
        dictionaries. This is consistent with the standard n-ary definition of
        symmetric difference [WikiSymDiff]_ and corresponds with the xor
        operation.

        Args:
            self (SetDict | dict):
                if called as a static method this must be provided.

            *others : other dictionary or set like objects that can
                be coerced into a set of keys.

            cls (type):
                the desired return dictionary type.

        Returns:
            dict : whatever the dictionary type of the first argument is

        References:
            .. [WikiSymDiff] https://en.wikipedia.org/wiki/Symmetric_difference

        Example:
            >>> import ubelt as ub
            >>> a = ub.SetDict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> b = ub.SetDict({k: 'B_' + chr(97 + k) for k in [2, 4, 0, 7]})
            >>> c = ub.SetDict({k: 'C_' + chr(97 + k) for k in [2, 8, 3]})
            >>> d = ub.SetDict({k: 'D_' + chr(97 + k) for k in [9, 10, 11]})
            >>> e = ub.SetDict({k: 'E_' + chr(97 + k) for k in []})
            >>> a ^ b
            {3: 'A_d', 5: 'A_f', 4: 'B_e', 0: 'B_a'}
            >>> a.symmetric_difference(b)
            >>> a - b - c
            >>> res = ub.SetDict.symmetric_difference(a, b, c, d, e)
            >>> print(ub.repr2(res, sort=1, nl=0, si=1))
            {0: B_a, 2: C_c, 4: B_e, 5: A_f, 8: C_i, 9: D_j, 10: D_k, 11: D_l}
        """
        cls = cls or self.__class__
        new = cls(self)  # shallow copy
        for d in others:
            for k, v in d.items():
                if k in new:
                    new.pop(k)
                else:
                    new[k] = v
        return new


sdict = SetDict


# Might need to make these mixins for 3.6
class UDict(SetDict):
    """
    A subclass of dict with ubelt enhancements

    This builds on top of :class:`SetDict` which itself is a simple extension
    that contains only that extra functionality. The extra invert, map, sorted,
    and peek functions are less fundamental and there are at least reasonable
    workarounds when they are not available.

    The UDict class is a simple subclass of dict that provides the following upgrades:

        * set operations - inherited from :class:`SetDict`
            + intersection - find items in common
            + union - merge dicts
            + difference - find items in one but not the other
            + symmetric_difference - find items that appear an odd number of times

        * subdict - take a subset with optional default values. (similar to intersection, but the later ignores non-common values)

        * inversion -
            + invert - swaps a dictionary keys and values (with options for dealing with duplicates).

        * mapping -
           + map_keys - applies a function over each key and keeps the values the same
           + map_values - applies a function over each key and keeps the values the same

        * sorting -
           + sorted_keys - returns a dictionary ordered by the keys
           + sorted_values - returns a dictionary ordered by the values

    IMO key-wise set operations on dictionaries are fundamentaly and sorely
    missing from the stdlib, mapping is super convinient, sorting and inversion
    are less common, but still useful to have.

    TODO:
        - [ ] UbeltDict, UltraDict, not sure what the name is.  We may just rename this to Dict,

    Example:
        >>> import ubelt as ub
        >>> a = ub.udict({1: 20, 2: 20, 3: 30, 4: 40})
        >>> b = ub.udict({0: 0, 2: 20, 4: 42})
        >>> c = ub.udict({3: -1, 5: -1})
        >>> # Demo key-wise set operations
        >>> assert a & b == {2: 20, 4: 40}
        >>> assert a - b == {1: 20, 3: 30}
        >>> assert a ^ b == {1: 20, 3: 30, 0: 0}
        >>> assert a | b == {1: 20, 2: 20, 3: 30, 4: 42, 0: 0}
        >>> # Demo new n-ary set methods
        >>> a.union(b, c) == {1: 20, 2: 20, 3: -1, 4: 42, 0: 0, 5: -1}
        >>> a.intersection(b, c) == {}
        >>> a.difference(b, c) == {1: 20}
        >>> a.symmetric_difference(b, c) == {1: 20, 0: 0, 5: -1}
        >>> # Demo new quality of life methods
        >>> assert a.subdict({2, 4, 6, 8}, default=None) == {8: None, 2: 20, 4: 40, 6: None}
        >>> assert a.invert() == {20: 2, 30: 3, 40: 4}
        >>> assert a.invert(unique_vals=0) == {20: {1, 2}, 30: {3}, 40: {4}}
        >>> assert a.peek_key() == ub.peek(a.keys())
        >>> assert a.peek_value() == ub.peek(a.values())
        >>> assert a.map_keys(lambda x: x * 10) == {10: 20, 20: 20, 30: 30, 40: 40}
        >>> assert a.map_values(lambda x: x * 10) == {1: 200, 2: 200, 3: 300, 4: 400}
    """

    def subdict(self, keys, default=NoParam):
        """
        Get a subset of a dictionary

        Args:
            self (Dict[KT, VT]): dictionary or the implicit instance

            keys (Iterable[KT]): keys to take from ``self``

            default (Optional[object] | NoParamType):
                if specified uses default if keys are missing.

        Raises:
            KeyError : if a key does not exist and default is not specified

        SeeAlso:
            :func:`ubelt.util_dict.dict_subset`
            :func:`ubelt.UDict.take`

        Example:
            >>> import ubelt as ub
            >>> a = ub.udict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> s = a.subdict({2, 5})
            >>> print('s = {}'.format(ub.repr2(s, nl=0, sort=1)))
            s = {2: 'A_c', 5: 'A_f'}
            >>> import pytest
            >>> with pytest.raises(KeyError):
            >>>     s = a.subdict({2, 5, 100})
            >>> s = a.subdict({2, 5, 100}, default='DEF')
            >>> print('s = {}'.format(ub.repr2(s, nl=0, sort=1)))
            s = {2: 'A_c', 5: 'A_f', 100: 'DEF'}
        """
        cls = self.__class__
        if default is NoParam:
            new = cls([(k, self[k]) for k in keys])
        else:
            new = cls([(k, self.get(k, default)) for k in keys])
        return new

    def take(self, keys, default=NoParam):
        """
        Get values of an iterable of keys.

        Args:
            self (Dict[KT, VT]): dictionary or the implicit instance

            keys (Iterable[KT]): keys to take from ``self``

            default (Optional[object] | NoParamType):
                if specified uses default if keys are missing.

        Yields:
            VT: a selected value within the dictionary

        Raises:
            KeyError : if a key does not exist and default is not specified

        SeeAlso:
            :func:`ubelt.util_list.take`
            :func:`ubelt.UDict.subdict`

        Example:
            >>> import ubelt as ub
            >>> a = ub.udict({k: 'A_' + chr(97 + k) for k in [2, 3, 5, 7]})
            >>> s = list(a.take({2, 5}))
            >>> print('s = {}'.format(ub.repr2(s, nl=0, sort=1)))
            s = ['A_c', 'A_f']
            >>> import pytest
            >>> with pytest.raises(KeyError):
            >>>     s = a.subdict({2, 5, 100})
            >>> s = list(a.take({2, 5, 100}, default='DEF'))
            >>> print('s = {}'.format(ub.repr2(s, nl=0, sort=1)))
            s = ['A_c', 'A_f', 'DEF']
        """
        if default is NoParam:
            for k in keys:
                yield self[k]
        else:
            for k in keys:
                yield self.get(k, default)

    def invert(self, unique_vals=True):
        """
        Swaps the keys and values in a dictionary.

        Args:
            self (Dict[KT, VT]): dictionary or the implicit instance to invert

            unique_vals (bool, default=True): if False, the values of the new
                dictionary are sets of the original keys.

            cls (type | None): specifies the dict subclassof the result.
                if unspecified will be dict or OrderedDict. This behavior may
                change.

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
            >>> inverted = ub.udict({'a': 1, 'b': 2}).invert()
            >>> assert inverted == {1: 'a', 2: 'b'}
        """
        import ubelt as ub
        return ub.invert_dict(self, unique_vals=unique_vals, cls=self.__class__)

    def map_keys(self, func):
        """
        Apply a function to every value in a dictionary.

        Creates a new dictionary with the same keys and modified values.

        Args:
            self (Dict[KT, VT]): a dictionary or the implicit instance.
            func (Callable[[VT], T] | Mapping[VT, T]): a function or indexable object

        Returns:
            Dict[KT, T]: transformed dictionary

        Example:
            >>> import ubelt as ub
            >>> new = ub.udict({'a': [1, 2, 3], 'b': []}).map_keys(ord)
            >>> assert new == {97: [1, 2, 3], 98: []}
        """
        import ubelt as ub
        return ub.map_keys(func, self, cls=self.__class__)

    def map_values(self, func):
        """
        Apply a function to every value in a dictionary.

        Creates a new dictionary with the same keys and modified values.

        Args:
            self (Dict[KT, VT]): a dictionary or the implicit instance.
            func (Callable[[VT], T] | Mapping[VT, T]): a function or indexable object

        Returns:
            Dict[KT, T]: transformed dictionary

        Example:
            >>> import ubelt as ub
            >>> newdict = ub.udict({'a': [1, 2, 3], 'b': []}).map_values(len)
            >>> assert newdict ==  {'a': 3, 'b': 0}
        """
        import ubelt as ub
        return ub.map_values(func, self, cls=self.__class__)

    def sorted_keys(self, key=None, reverse=False):
        """
        Return an ordered dictionary sorted by its keys

        Args:
            self (Dict[KT, VT]):
                dictionary to sort or the implicit instance.
                The keys must be of comparable types.

            key (Callable[[KT], Any] | None):
                If given as a callable, customizes the sorting by ordering using
                transformed keys.

            reverse (bool, default=False):
                if True returns in descending order

        Returns:
            OrderedDict[KT, VT]: new dictionary where the keys are ordered

        Example:
            >>> import ubelt as ub
            >>> new = ub.udict({'spam': 2.62, 'eggs': 1.20, 'jam': 2.92}).sorted_keys()
            >>> assert new == ub.odict([('eggs', 1.2), ('jam', 2.92), ('spam', 2.62)])
        """
        import ubelt as ub
        return ub.sorted_keys(self, key=key, reverse=reverse, cls=self.__class__)

    def sorted_values(self, key=None, reverse=False):
        """
        Return an ordered dictionary sorted by its values

        Args:
            self (Dict[KT, VT]):
                dictionary to sort or the implicit instance.
                The values must be of comparable types.

            key (Callable[[VT], Any] | None):
                If given as a callable, customizes the sorting by ordering using
                transformed values.

            reverse (bool, default=False):
                if True returns in descending order

        Returns:
            OrderedDict[KT, VT]: new dictionary where the values are ordered

        Example:
            >>> import ubelt as ub
            >>> new = ub.udict({'spam': 2.62, 'eggs': 1.20, 'jam': 2.92}).sorted_values()
            >>> assert new == ub.odict([('eggs', 1.2), ('spam', 2.62), ('jam', 2.92)])
        """
        import ubelt as ub
        return ub.sorted_values(self, key=key, reverse=reverse, cls=self.__class__)

    def peek_key(self, default=NoParam):
        """
        Get the first key in the dictionary

        Args:
            self (Dict): a dictionary or the implicit instance

            default (KT | NoParamType): default item to return if the iterable is empty,
                otherwise a StopIteration error is raised

        Returns:
            KT: the first value or the default

        Example:
            >>> import ubelt as ub
            >>> assert ub.udict({1: 2}).peek_key() == 1
        """
        import ubelt as ub
        return ub.peek(self.keys(), default=default)

    def peek_value(self, default=NoParam):
        """
        Get the first value in the dictionary

        Args:
            self (Dict[KT, VT]): a dictionary or the implicit instance
            default (VT | NoParamType): default item to return if the iterable is empty,
                otherwise a StopIteration error is raised

        Returns:
            VT: the first value or the default

        Example:
            >>> import ubelt as ub
            >>> assert ub.udict({1: 2}).peek_value() == 2
        """
        import ubelt as ub
        return ub.peek(self.values(), default=default)


class AutoDict(UDict):
    """
    An infinitely nested default dict of dicts.

    Implementation of Perl's autovivification feature that follows
    [SO_651794]_.

    References:
        .. [SO_651794] http://stackoverflow.com/questions/651794/init-dict-of-dicts

    Example:
        >>> import ubelt as ub
        >>> auto = ub.AutoDict()
        >>> auto[0][10][100] = None
        >>> assert str(auto) == '{0: {10: {100: None}}}'
    """
    _base = UDict

    def __getitem__(self, key):
        try:
            # value = super(AutoDict, self).__getitem__(key)
            value = self._base.__getitem__(self, key)
        except KeyError:
            value = self[key] = self.__class__()
        return value

    def to_dict(self):
        """
        Recursively casts a AutoDict into a regular dictionary. All directly
        nested AutoDict values are also converted.

        This effectively de-defaults the structure.

        Returns:
            dict: a copy of this dict without autovivification

        Example:
            >>> import ubelt as ub
            >>> auto = ub.AutoDict()
            >>> auto[1] = 1
            >>> auto['n1'] = ub.AutoDict()
            >>> static = auto.to_dict()
            >>> assert not isinstance(static, ub.AutoDict)
            >>> assert not isinstance(static['n1'], ub.AutoDict)

        Example:
            >>> import ubelt as ub
            >>> auto = ub.AutoOrderedDict()
            >>> auto[0][3] = 3
            >>> auto[0][2] = 2
            >>> auto[0][1] = 1
            >>> assert list(auto[0].values()) == [3, 2, 1]
        """
        return self._base(
            (key, (value.to_dict() if isinstance(value, AutoDict) else value))
            for key, value in self.items())


# DEPRECATED. This is no longer needed. AutoDict is always ordered
AutoOrderedDict = AutoDict
udict = UDict
