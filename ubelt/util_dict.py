# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import collections
import operator as op
import itertools as it
from ubelt import util_const
from six.moves import zip


def group_items(item_list, groupid_list, sorted_=True):
    r"""
    Groups a list of items by group id.

    Args:
        item_list (list): a list of items to group
        groupid_list (list): a corresponding list of item groupids
        sorted_ (bool): if True preserves the ordering of items within groups
            (default = True)

    Returns:
        dict: groupid_to_items: maps a groupid to a list of items

    Example:
        >>> import ubelt as ub
        >>> item_list    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'bannana']
        >>> groupid_list = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
        >>> ub.group_items(item_list, iter(groupid_list))
        >>> #groupid_to_items = ub.group_items(item_list, iter(groupid_list))
        >>> #result = ub.dict_str(groupid_to_items, nl=False, strvals=False)
        >>> #print(result)
        {'dairy': ['cheese'], 'fruit': ['jam', 'bannana'], 'protein': ['ham', 'spam', 'eggs']}
    """
    pair_list_ = list(zip(groupid_list, item_list))
    if sorted_:
        # Sort by groupid for cache efficiency
        try:
            pair_list = sorted(pair_list_, key=op.itemgetter(0))
        except TypeError:
            # Python 3 does not allow sorting mixed types
            pair_list = sorted(pair_list_, key=lambda tup: str(tup[0]))
    else:
        pair_list = pair_list_

    # Initialize a dict of lists
    groupid_to_items = collections.defaultdict(list)
    # Insert each item into the correct group
    for groupid, item in pair_list:
        groupid_to_items[groupid].append(item)
    return groupid_to_items


def dict_hist(item_list, weight_list=None, ordered=False, labels=None):
    r"""
    Builds a histogram of items

    Args:
        item_list (list): list with hashable items
            (usually containing duplicates)
        weight_list (list): list of weights for each items
        ordered (bool): if True the result is ordered by frequency
        labels (list): expected labels (default None)
            if specified the frequency of each label is initialized to
            zero and item_list can only contain items specified in labels.

    Returns:
        dict : dictionary where the keys are items in item_list, and the values
          are the number of times the item appears in item_list.

    CommandLine:
        python -m ubelt.util_dict --test-dict_hist

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ubelt.util_dict import *  # NOQA
        >>> import ubelt as ub
        >>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
        >>> hist_ = dict_hist(item_list)
        >>> result = ub.repr2(hist_)
        >>> print(result)
        {1: 1, 2: 4, 39: 1, 900: 3, 1232: 2}
    """
    if labels is None:
        hist_ = collections.defaultdict(lambda: 0)
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
        key_order = (key for (key, value) in sorted(hist_.items(), key=getval))
        hist_ = dict_subset(hist_, key_order)
    else:
        # Cast to a normal dictionary
        hist_ = dict(hist_)
    return hist_


def dict_subset(dict_, keys, default=util_const.NoParam):
    r"""
    Get a subset of a dictionary

    Args:
        dict_ (dict): superset dictionary
        keys (list): keys to take from `dict_`

    Returns:
        dict: subset dictionary

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ubelt.util_dict import *  # NOQA
        >>> import ubelt as ub
        >>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
        >>> keys = ['K', 'dcvs_clip_max']
        >>> d = tuple([])
        >>> subdict_ = dict_subset(dict_, keys)
        >>> result = ub.dict_str(subdict_, sorted_=True, newlines=False)
        >>> print(result)
        {'K': 3, 'dcvs_clip_max': 0.2}
    """
    items = dict_take(dict_, keys, default)
    subdict_ = collections.OrderedDict(list(zip(keys, items)))
    return subdict_


def dict_take(dict_, keys, default=util_const.NoParam):
    r"""
    Generates values from a dictionary

    Args:
        dict_ (dict):
        keys (list):
        default (Optional): if specified uses default if keys are missing

    CommandLine:
        python -m ubelt.util_dict dict_take_gen

    Example1:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> result = list(ub.dict_take(dict_, keys, None))
        >>> assert result == ['a', 'b', 'c', None, None]

    Example2:
        >>> from ubelt.util_dict import *  # NOQA
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
