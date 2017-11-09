# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import itertools as it
import six
import math
from six.moves import zip_longest


class chunks(object):
    """
    Generates successive n-sized chunks from `sequence`.
    If the last chunk has less than n elements, `bordermode` is used to
    determine fill values.

    Args:
        sequence (list): input to iterate over
        chunksize (int): size of each sublist yielded
        nchunks (int): number of chunks to create (
            cannot be specified with chunksize)
        bordermode (str): determines how to handle the last case if the
            length of the sequence is not divisible by chunksize valid values
            are: {'none', 'cycle', 'replicate'}

    References:
        http://stackoverflow.com/questions/434287/iterate-over-a-list-in-chunks

    CommandLine:
        python -m ubelt.util_list chunks

    Example:
        >>> import ubelt as ub
        >>> sequence = [1, 2, 3, 4, 5, 6, 7]
        >>> genresult = ub.chunks(sequence, chunksize=3, bordermode='none')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7]]
        >>> genresult = ub.chunks(sequence, chunksize=3, bordermode='cycle')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7, 1, 2]]
        >>> genresult = ub.chunks(sequence, chunksize=3, bordermode='replicate')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7, 7, 7]]

    Doctest:
        >>> import ubelt as ub
        >>> assert len(list(ub.chunks(range(2), nchunks=2))) == 2
        >>> assert len(list(ub.chunks(range(3), nchunks=2))) == 2
        >>> assert len(list(ub.chunks([], 2, None, 'none'))) == 0
        >>> assert len(list(ub.chunks([], 2, None, 'cycle'))) == 0
        >>> assert len(list(ub.chunks([], 2, None, 'replicate'))) == 0
    """
    def __init__(self, sequence, chunksize=None, nchunks=None,
                 bordermode='none'):
        if nchunks is not None and chunksize is not None:  # nocover
            raise ValueError('Cannot specify both chunksize and nchunks')
        if nchunks is not None:
            chunksize = int(math.ceil(len(sequence) / nchunks))

        self.bordermode = bordermode
        self.sequence = sequence
        self.chunksize = chunksize

    def __iter__(self):
        bordermode = self.bordermode
        sequence = self.sequence
        chunksize = self.chunksize
        if bordermode is None or bordermode == 'none':
            return self.noborder(sequence, chunksize)
        elif bordermode == 'cycle':
            return self.cycle(sequence, chunksize)
        elif bordermode == 'replicate':
            return self.replicate(sequence, chunksize)
        else:
            raise ValueError('unknown bordermode=%r' % (bordermode,))

    @staticmethod
    def noborder(sequence, chunksize):
        # feed the same iter to zip_longest multiple times, this causes it to
        # consume successive values of the same sequence
        sentinal = object()
        copied_iters = [iter(sequence)] * chunksize
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        # Dont fill empty space in the last chunk, just return it as is
        for chunk in chunks_with_sentinals:
            yield [item for item in chunk if item is not sentinal]

    @staticmethod
    def cycle(sequence, chunksize):
        sentinal = object()
        copied_iters = [iter(sequence)] * chunksize
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        # Fill empty space in the last chunk with values from the beginning
        bordervalues = it.cycle(iter(sequence))
        for chunk in chunks_with_sentinals:
            yield [item if item is not sentinal else six.next(bordervalues)
                   for item in chunk]

    @staticmethod
    def replicate(sequence, chunksize):
        sentinal = object()
        copied_iters = [iter(sequence)] * chunksize
        # Fill empty space in the last chunk by replicating the last value
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        for chunk in chunks_with_sentinals:
            filt_chunk = [item for item in chunk if item is not sentinal]
            if len(filt_chunk) == chunksize:
                yield filt_chunk
            else:
                sizediff = (chunksize - len(filt_chunk))
                padded_chunk = filt_chunk + [filt_chunk[-1]] * sizediff
                yield padded_chunk


def iterable(obj, strok=False):
    """
    Checks if the input implements the iterator interface. An exception is made
    for strings, which return False unless `strok` is True

    Args:
        obj (object): a scalar or iterable input
        strok (bool): if True allow strings to be interpreted as iterable

    Returns:
        bool: True if the input is iterable

    Example:
        >>> import ubelt as ub
        >>> obj_list = [3, [3], '3', (3,), [3, 4, 5], {}]
        >>> result = [ub.iterable(obj) for obj in obj_list]
        >>> assert result == [False, True, False, True, True, True]
        >>> result = [ub.iterable(obj, strok=True) for obj in obj_list]
        >>> assert result == [False, True, True, True, True, True]
    """
    try:
        iter(obj)
    except:
        return False
    else:
        return strok or not isinstance(obj, six.string_types)


def take(items, indices):
    """
    Selects a subset of a list based on a list of indices.
    This is similar to np.take, but pure python.

    Args:
        items (list): some indexable object
        indices (sequence): sequence of indexing objects

    Returns:
        iter or scalar: subset of the list

    SeeAlso:
        ub.dict_subset

    Example:
        >>> import ubelt as ub
        >>> items = [0, 1, 2, 3]
        >>> indices = [2, 0]
        >>> list(ub.take(items, indices))
        [2, 0]
    """
    return (items[index] for index in indices)


def compress(items, flags):
    """
    Selects items where the corresponding value in flags is True
    This is similar to np.compress and it.compress

    Args:
        items (iterable): a sequence
        flags (iterable): corresponding sequence of bools

    Returns:
        list: a subset of masked items

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 3, 4, 5]
        >>> flags = [False, True, True, False, True]
        >>> list(ub.compress(items, flags))
        [2, 3, 5]
    """
    return it.compress(items, flags)


def flatten(nested_list):
    """
    Args:
        nested_list (list): list of lists

    Returns:
        list: flat list

    Example:
        >>> import ubelt as ub
        >>> nested_list = [['a', 'b'], ['c', 'd']]
        >>> list(ub.flatten(nested_list))
        ['a', 'b', 'c', 'd']
    """
    return it.chain.from_iterable(nested_list)


def unique(items):
    """
    Generates unique items in the order they appear.

    Args:
        items (sequence): list of hashable items

    Yields:
        hashable: a unique item from the input sequence

    CommandLine:
        python -m utool.util_list --exec-unique_ordered

    Example:
        >>> import ubelt as ub
        >>> items = [4, 6, 6, 0, 6, 1, 0, 2, 2, 1]
        >>> unique_items = list(ub.unique(items))
        >>> assert unique_items == [4, 6, 0, 1, 2]
    """
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            yield item


def boolmask(indices, maxval=None):
    """
    Constructs a list of booleans where an item is True if its position is in
    `indices` otherwise it is False.

    Args:
        indices (list): list of integer indices
        maxval (int): length of the returned list. If not specified
            this is inverred from `indices`

    Returns:
        list: mask: list of booleans. mask[idx] is True if idx in indices

    Example:
        >>> import ubelt as ub
        >>> indices = [0, 1, 4]
        >>> mask = ub.boolmask(indices, maxval=6)
        >>> assert mask == [True, True, False, False, True, False]
        >>> mask = ub.boolmask(indices)
        >>> assert mask == [True, True, False, False, True]
    """
    if maxval is None:
        indices = list(indices)
        maxval = max(indices) + 1
    mask = [False] * maxval
    for index in indices:
        mask[index] = True
    return mask


def unique_flags(items):
    """
    Returns a list of booleans corresponding to the first instance of each
    unique item.

    Args:
        items (list): list of items

    Returns:
        flags : list of bools : flags the items that are unique

    Example:
        >>> import ubelt as ub
        >>> indices = [0, 5, 1, 1, 0, 2, 4]
        >>> flags = ub.unique_flags(indices)
        >>> assert flags == [True, True, True, False, False, True, True]
    """
    len_ = len(items)
    unique_indices = dict(zip(reversed(items), reversed(range(len_))))
    flags = boolmask(unique_indices.values(), len_)
    return flags


def argsort(indexable, key=None, reverse=False):
    """
    Returns the indices that would sort a indexable object.

    This is similar to np.argsort, but it is written in pure python and works
    on both lists and dictionaries.

    Args:
        indexable (list or dict): indexable to sort by
        key (None or func): key to customize the ordering of the indexable
        reverse (bool): if True returns in descending order

    Returns:
        list: indices: list of indices such that sorts the indexable

    Example:
        >>> import ubelt as ub
        >>> # argsort works on dicts by returning keys
        >>> dict_ = {'a': 3, 'b': 2, 'c': 100}
        >>> indices = ub.argsort(dict_)
        >>> assert list(ub.take(dict_, indices)) == sorted(dict_.values())
        >>> # argsort works on lists by returning indices
        >>> indexable = [100, 2, 432, 10]
        >>> indices = ub.argsort(indexable)
        >>> assert list(ub.take(indexable, indices)) == sorted(indexable)
        >>> # Can use iterators, but be careful. It exhausts them.
        >>> indexable = reversed(range(100))
        >>> indices = ub.argsort(indexable)
        >>> assert indices[0] == 99
        >>> # Can use key just like sorted
        >>> indexable = [[0, 1, 2], [3, 4], [5]]
        >>> indices = ub.argsort(indexable, key=len)
        >>> assert indices == [2, 1, 0]
        >>> # Can use reverse just like sorted
        >>> indexable = [0, 2, 1]
        >>> indices = ub.argsort(indexable, reverse=True)
        >>> assert indices == [1, 2, 0]
    """
    # Create an iterator of value/key pairs
    if isinstance(indexable, dict):
        vk_iter = ((v, k) for k, v in indexable.items())
    else:
        vk_iter = ((v, k) for k, v in enumerate(indexable))
    # Sort by values and extract the indices
    if key is None:
        indices = [k for v, k in sorted(vk_iter, reverse=reverse)]
    else:
        # If key is provided, call it using the value as input
        indices = [k for v, k in sorted(vk_iter, key=lambda vk: key(vk[0]),
                                        reverse=reverse)]
    return indices


# if False:
#     import operator as op
#     def argmax(indexable, key=None):
#         """
#         Returns index / key of the item with the largest value.
#
#         Args:
#             indexable (dict or list):
#             key (None or func): key to customize the ordering of the indexable
#
#         References:
#             http://stackoverflow.com/questions/16945518/python-argmin-argmax
#         """
#         if isinstance(indexable, dict):
#             return max(input_.items(), key=op.itemgetter(1))[0]
#         elif hasattr(indexable, 'index'):
#             return indexable.index(max(indexable, key=key))
#         elif key is None:
#             return max(enumerate(indexable), key=op.itemgetter(1))[0]
#         else:
#             return max(enumerate(indexable), key=key=lambda kv: key(kv[1]))[0]


if __name__ == '__main__':
    """
    CommandLine:
        python -m ubelt.util_list all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
