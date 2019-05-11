# -*- coding: utf-8 -*-
"""
Functions for working with dictionaries.

The `dict_hist` function counts the number of discrete occurrences of hashable
items. Similarly `find_duplicates` looks for indices of items that occur more
than `k=1` times.

The `map_keys` and `map_vals` functions are useful for transforming the keys
and values of a dictionary with less syntax than a dict comprehension.

The `dict_union`, `dict_isect`, and `dict_subset` functions are similar to the set equivalents.

The `dict_take` function works similarly to `ubelt.take` and `np.take`, except it allows for a default value to be specified.

The `dzip` function zips two iterables and packs them into a dictionary where the first iterable is used to generate keys and the second generates values.

The `group_items` function takes two lists and returns a dict mapping values in the second list to all items in corresponding locations in the first list.

The `invert_dict` function swaps keys and values. See the function docs for details on dealing with unique and non-unique values.

The `ddict` and `odict` functions are alias for the commonly used`collections.defaultdict` and `collections.OrderedDict` classes.

"""
from __future__ import absolute_import, division, print_function, unicode_literals
import six
import operator as op
import itertools as it
from collections import OrderedDict
from collections import defaultdict
from six.moves import zip
from ubelt import util_const


# Expose for convenience
odict = OrderedDict
ddict = defaultdict

__all__ = [
    'AutoDict',
    'AutoOrderedDict',
    'dzip',
    'ddict',
    'dict_hist',
    'dict_subset',
    'dict_take',
    'dict_union',
    'dict_isect',
    'find_duplicates',
    'group_items',
    'invert_dict',
    'map_keys',
    'map_vals',
    'odict'
]


class AutoDict(dict):
    """
    An infinitely nested default dict of dicts.

    Implementation of Perl's autovivification feature.

    SeeAlso:
        ub.AutoOrderedDict - the ordered version

    References:
        http://stackoverflow.com/questions/651794/init-dict-of-dicts

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
        ub.AutoDict - the unordered version

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
    Zips elementwise pairs between items1 and items2 into a dictionary. Values
    from items2 can be broadcast onto items1.

    Args:
        items1 (Iterable): full sequence
        items2 (Iterable): can either be a sequence of one item or a sequence
            of equal length to `items1`
        cls (Type[dict]): dictionary type to use. Defaults to dict, but could
            be ordered dict instead.

    Returns:
        dict: similar to dict(zip(items1, items2))

    Example:
        >>> assert dzip([1, 2, 3], [4]) == {1: 4, 2: 4, 3: 4}
        >>> assert dzip([1, 2, 3], [4, 4, 4]) == {1: 4, 2: 4, 3: 4}
        >>> assert dzip([], [4]) == {}
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
        # value. This means that the equality check wont work for the case
        # where items1 and items2 are supposed to correspond, but the length of
        # items2 is 1.
        items2 = []
    if len(items2) == 1 and len(items1) > 1:
        items2 = items2 * len(items1)
    if len(items1) != len(items2):
        raise ValueError('out of alignment len(items1)=%r, len(items2)=%r' % (
            len(items1), len(items2)))
    return cls(zip(items1, items2))


def group_items(items, groupids):
    r"""
    Groups a list of items by group id.

    Args:
        items (Iterable): a list of items to group
        groupids (Iterable or Callable): a corresponding list of item groupids
            or a function mapping an item to a groupid.

    Returns:
        dict: groupid_to_items: maps a groupid to a list of items

    CommandLine:
        python -m ubelt.util_dict group_items

    Example:
        >>> import ubelt as ub
        >>> items    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'banana']
        >>> groupids = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
        >>> groupid_to_items = ub.group_items(items, groupids)
        >>> print(ub.repr2(groupid_to_items, nl=0))
        {'dairy': ['cheese'], 'fruit': ['jam', 'banana'], 'protein': ['ham', 'spam', 'eggs']}
    """
    if callable(groupids):
        keyfunc = groupids
        pair_list = ((keyfunc(item), item) for item in items)
    else:
        pair_list = zip(groupids, items)

    # Initialize a dict of lists
    groupid_to_items = defaultdict(list)
    # Insert each item into the correct group
    for key, item in pair_list:
        groupid_to_items[key].append(item)
    return groupid_to_items


def dict_hist(item_list, weight_list=None, ordered=False, labels=None):
    """
    Builds a histogram of items, counting the number of time each item appears
    in the input.

    Args:
        item_list (Iterable): hashable items (usually containing duplicates)
        weight_list (Iterable): corresponding weights for each item
        ordered (bool): if True the result is ordered by frequency
        labels (Iterable, optional): expected labels (default None)
            Allows this function to pre-initialize the histogram.
            If specified the frequency of each label is initialized to
            zero and item_list can only contain items specified in labels.

    Returns:
        dict : dictionary where the keys are items in item_list, and the values
          are the number of times the item appears in item_list.

    CommandLine:
        python -m ubelt.util_dict dict_hist

    Example:
        >>> import ubelt as ub
        >>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist = ub.dict_hist(item_list)
        >>> print(ub.repr2(hist, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}

    Example:
        >>> import ubelt as ub
        >>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist1 = ub.dict_hist(item_list)
        >>> hist2 = ub.dict_hist(item_list, ordered=True)
        >>> try:
        >>>     hist3 = ub.dict_hist(item_list, labels=[])
        >>> except KeyError:
        >>>     pass
        >>> else:
        >>>     raise AssertionError('expected key error')
        >>> #result = ub.repr2(hist_)
        >>> weight_list = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1]
        >>> hist4 = ub.dict_hist(item_list, weight_list=weight_list)
        >>> print(ub.repr2(hist1, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}
        >>> print(ub.repr2(hist4, nl=0))
        {1: 1, 2: 4, 39: 1, 900: 1, 1232: 0}
    """
    if labels is None:
        hist_ = defaultdict(lambda: 0)
    else:
        hist_ = {k: 0 for k in labels}
    if weight_list is None:
        weight_list = it.repeat(1)
    # Accumulate frequency
    for item, weight in zip(item_list, weight_list):
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

    Search for all items that appear more than `k` times and return a mapping
    from each (k)-duplicate item to the positions it appeared in.

    Args:
        items (Iterable): hashable items possibly containing duplicates
        k (int): only return items that appear at least `k` times (default=2)
        key (Callable, optional): Returns indices where `key(items[i])`
            maps to a particular value at least k times.

    Returns:
        dict: maps each duplicate item to the indices at which it appears

    CommandLine:
        python -m ubelt.util_dict find_duplicates

    Example:
        >>> import ubelt as ub
        >>> items = [0, 0, 1, 2, 3, 3, 0, 12, 2, 9]
        >>> duplicates = ub.find_duplicates(items)
        >>> print('items = %r' % (items,))
        >>> print('duplicates = %r' % (duplicates,))
        >>> assert duplicates == {0: [0, 1, 6], 2: [3, 8], 3: [4, 5]}
        >>> assert ub.find_duplicates(items, 3) == {0: [0, 1, 6]}

    Example:
        >>> import ubelt as ub
        >>> items = [0, 0, 1, 2, 3, 3, 0, 12, 2, 9]
        >>> # note: k can be 0
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
    # if key is not None:
    #     items = map(key, items)
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


def dict_subset(dict_, keys, default=util_const.NoParam):
    """
    Get a subset of a dictionary

    Args:
        dict_ (Mapping): superset dictionary
        keys (Iterable): keys to take from `dict_`
        default (object, optional): if specified uses default if keys are missing

    Returns:
        OrderedDict: subset dictionary

    SeeAlso:
        dict_isect - similar functionality, but will only take existing keys

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
        >>> keys = ['K', 'dcvs_clip_max']
        >>> subdict_ = ub.dict_subset(dict_, keys)
        >>> print(ub.repr2(subdict_, nl=0))
        {'K': 3, 'dcvs_clip_max': 0.2}
    """
    keys = list(keys)
    items = dict_take(dict_, keys, default)
    subdict_ = OrderedDict(list(zip(keys, items)))
    return subdict_


def dict_take(dict_, keys, default=util_const.NoParam):
    r"""
    Generates values from a dictionary

    Args:
        dict_ (Mapping): a dictionary to take from
        keys (Iterable): the keys to take
        default (object, optional): if specified uses default if keys are missing

    CommandLine:
        python -m ubelt.util_dict dict_take_gen

    Example:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> result = list(ub.dict_take(dict_, keys, None))
        >>> assert result == ['a', 'b', 'c', None, None]

    Example:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> try:
        >>>     print(list(ub.dict_take(dict_, keys)))
        >>>     raise AssertionError('did not get key error')
        >>> except KeyError:
        >>>     print('correctly got key error')
    """
    if default is util_const.NoParam:
        for key in keys:
            yield dict_[key]
    else:
        for key in keys:
            yield dict_.get(key, default)


def dict_union(*args):
    """
    Combines the disjoint keys in multiple dictionaries. For intersecting keys,
    dictionaries towards the end of the sequence are given precedence.

    Args:
        *args : a sequence of dictionaries

    Returns:
        Dict | OrderedDict :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    SeeAlso:
        collections.ChainMap - a standard python builtin data structure that
            provides a view that treats multiple dicts as a single dict.
            https://docs.python.org/3/library/collections.html#chainmap-objects

    Example:
        >>> result = dict_union({'a': 1, 'b': 1}, {'b': 2, 'c': 2})
        >>> assert result == {'a': 1, 'b': 2, 'c': 2}
        >>> dict_union(odict([('a', 1), ('b', 2)]), odict([('c', 3), ('d', 4)]))
        OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        >>> dict_union()
        {}
    """
    if not args:
        return {}
    else:
        dictclass = OrderedDict if isinstance(args[0], OrderedDict) else dict
        return dictclass(it.chain.from_iterable(d.items() for d in args))


def dict_diff(*args):
    """
    Constructs a dictionary that contains any of the keys in the first arg,
    which are not in any of the following args.

    Args:
        *args : a sequence of dictionaries (or sets of keys)

    Returns:
        Dict | OrderedDict :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    Ignore:
        python -c "import ubelt; print(len(ubelt.__all__))"

    Example:
        >>> dict_diff({'a': 1, 'b': 1}, {'a'}, {'c'})
        {'b': 1}
        >>> dict_diff(odict([('a', 1), ('b', 2)]), odict([('c', 3)]))
        OrderedDict([('a', 1), ('b', 2)])
        >>> dict_diff()
        {}
        >>> dict_diff({'a': 1, 'b': 2}, {'c'})
    """
    if not args:
        return {}
    else:
        first_dict = args[0]
        if isinstance(first_dict, OrderedDict):
            from ubelt import OrderedSet
            dictclass = OrderedDict
            keys = OrderedSet(first_dict)
        else:
            dictclass = dict
            keys = set(first_dict)
        keys.difference_update(*map(set, args[1:]))
        return dictclass((k, first_dict[k]) for k in keys)


def dict_isect(*args):
    """
    Constructs a dictionary that contains keys common between all inputs.
    The returned values will only belong to the first dictionary.

    Args:
        *args : a sequence of dictionaries (or sets of keys)

    Returns:
        Dict | OrderedDict :
            OrderedDict if the first argument is an OrderedDict, otherwise dict

    Notes:
        This function can be used as an alternative to `dict_subset` where any
        key not in the dictionary is ignored. See the following example:

        >>> dict_isect({'a': 1, 'b': 2, 'c': 3}, ['a', 'c', 'd'])
        {'a': 1, 'c': 3}

    Example:
        >>> dict_isect({'a': 1, 'b': 1}, {'b': 2, 'c': 2})
        {'b': 1}
        >>> dict_isect(odict([('a', 1), ('b', 2)]), odict([('c', 3)]))
        OrderedDict()
        >>> dict_isect()
        {}
    """
    if not args:
        return {}
    else:
        dictclass = OrderedDict if isinstance(args[0], OrderedDict) else dict
        common_keys = set.intersection(*map(set, args))
        first_dict = args[0]
        return dictclass((k, first_dict[k]) for k in common_keys)


def map_vals(func, dict_):
    """
    Transform a dictionary by applying a function to each value, while keeping
    the keys the same.

    Args:
        func (callable): a function or indexable object
        dict_ (dict): a dictionary

    Returns:
        newdict: transformed dictionary

    CommandLine:
        xdoctest -m ubelt.util_dict map_vals

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': [1, 2, 3], 'b': []}
        >>> func = len
        >>> newdict = ub.map_vals(func, dict_)
        >>> assert newdict ==  {'a': 3, 'b': 0}
        >>> print(newdict)
        >>> # Can also use indexables as `func`
        >>> dict_ = {'a': 0, 'b': 1}
        >>> func = [42, 21]
        >>> newdict = ub.map_vals(func, dict_)
        >>> assert newdict ==  {'a': 42, 'b': 21}
        >>> print(newdict)
    """
    if not hasattr(func, '__call__'):
        func = func.__getitem__
    keyval_list = [(key, func(val)) for key, val in six.iteritems(dict_)]
    dictclass = OrderedDict if isinstance(dict_, OrderedDict) else dict
    newdict = dictclass(keyval_list)
    # newdict = type(dict_)(keyval_list)
    return newdict


def map_keys(func, dict_):
    r"""
    Transform a dictionary by applying a function to each key, while keeping
    the values the same.

    Args:
        func (callable): a function or indexable object
        dict_ (dict): a dictionary

    Returns:
        newdict: transformed dictionary

    CommandLine:
        xdoctest -m ubelt.util_dict map_keys

    Example:
        >>> import ubelt as ub
        >>> dict_ = {'a': [1, 2, 3], 'b': []}
        >>> func = ord
        >>> newdict = ub.map_keys(func, dict_)
        >>> print(newdict)
        >>> assert newdict == {97: [1, 2, 3], 98: []}
        >>> #ut.assert_raises(AssertionError, map_keys, len, dict_)
        >>> dict_ = {0: [1, 2, 3], 1: []}
        >>> func = ['a', 'b']
        >>> newdict = ub.map_keys(func, dict_)
        >>> print(newdict)
        >>> assert newdict == {'a': [1, 2, 3], 'b': []}
        >>> #ut.assert_raises(AssertionError, map_keys, len, dict_)

    """
    if not hasattr(func, '__call__'):
        func = func.__getitem__
    keyval_list = [(func(key), val) for key, val in six.iteritems(dict_)]
    # newdict = type(dict_)(keyval_list)
    dictclass = OrderedDict if isinstance(dict_, OrderedDict) else dict
    newdict = dictclass(keyval_list)
    assert len(newdict) == len(dict_), (
        'multiple input keys were mapped to the same output key')
    return newdict


def invert_dict(dict_, unique_vals=True):
    r"""
    Swaps the keys and values in a dictionary.

    Args:
        dict_ (dict): dictionary to invert
        unique_vals (bool): if False, inverted keys are returned in a set.
            The default is True.

    Returns:
        dict: inverted

    Notes:
        The must values be hashable.

        If the original dictionary contains duplicate values, then only one of
        the corresponding keys will be returned and the others will be
        discarded.  This can be prevented by setting `unique_vals=True`,
        causing the inverted keys to be returned in a set.

    CommandLine:
        python -m ubelt.util_dict invert_dict

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
