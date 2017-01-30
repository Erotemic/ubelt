# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import collections
import operator as op
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
        >>> #result = ut.dict_str(groupid_to_items, nl=False, strvals=False)
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
