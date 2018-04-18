# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import itertools as it
import six
import math
import operator
from six.moves import zip_longest
from six import next


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

        total (int): hints about the length of the sequence

    TODO:
        should this handle the case when sequence is a string?

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

    Doctest:
        >>> def _check_len(self):
        ...     assert len(self) == len(list(self))
        >>> _check_len(chunks(list(range(3)), nchunks=2))
        >>> _check_len(chunks(list(range(2)), nchunks=2))
        >>> _check_len(chunks(list(range(2)), nchunks=3))

    Doctest:
        >>> import pytest
        >>> assert pytest.raises(ValueError, chunks, range(9))
        >>> assert pytest.raises(ValueError, chunks, range(9), chunksize=2, nchunks=2)
        >>> assert pytest.raises(TypeError, len, chunks((_ for _ in range(2)), 2))

    """
    def __init__(self, sequence, chunksize=None, nchunks=None,
                 total=None, bordermode='none'):
        if nchunks is not None and chunksize is not None:  # nocover
            raise ValueError('Cannot specify both chunksize and nchunks')
        if nchunks is None and chunksize is None:  # nocover
            raise ValueError('Must specify either chunksize or nchunks')
        if nchunks is not None:
            if total is None:
                total = len(sequence)
            chunksize = int(math.ceil(total / nchunks))

        self.bordermode = bordermode
        self.sequence = sequence
        self.chunksize = chunksize
        self.total = total

    def __len__(self):
        if self.total is None:
            self.total = len(self.sequence)
        nchunks = int(math.ceil(self.total / self.chunksize))
        return nchunks

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
            yield [item if item is not sentinal else next(bordervalues)
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
        >>> obj_list = [3, [3], '3', (3,), [3, 4, 5], {}]
        >>> result = [iterable(obj) for obj in obj_list]
        >>> assert result == [False, True, False, True, True, True]
        >>> result = [iterable(obj, strok=True) for obj in obj_list]
        >>> assert result == [False, True, True, True, True, True]
    """
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return strok or not isinstance(obj, six.string_types)


def take(items, indices):
    """
    Selects a subset of a list based on a list of indices.
    This is similar to np.take, but pure python.

    Args:
        items (list): an indexable object to select items from

        indices (Sequence): sequence of indexing objects

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
        items (Sequence): a sequence to select items from

        flags (Sequence): corresponding sequence of bools

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


def unique(items, key=None):
    """
    Generates unique items in the order they appear.

    Args:
        items (Sequence): list of items

        key (Function, optional): custom normalization function.
            If specified returns items where `key(item)` is unique.

    Yields:
        object: a unique item from the input sequence

    CommandLine:
        python -m utool.util_list --exec-unique_ordered

    Example:
        >>> import ubelt as ub
        >>> items = [4, 6, 6, 0, 6, 1, 0, 2, 2, 1]
        >>> unique_items = list(ub.unique(items))
        >>> assert unique_items == [4, 6, 0, 1, 2]

    Example:
        >>> import ubelt as ub
        >>> items = ['A', 'a', 'b', 'B', 'C', 'c', 'D', 'e', 'D', 'E']
        >>> unique_items = list(ub.unique(items, key=six.text_type.lower))
        >>> assert unique_items == ['A', 'b', 'C', 'D', 'e']
        >>> unique_items = list(ub.unique(items))
        >>> assert unique_items == ['A', 'a', 'b', 'B', 'C', 'c', 'D', 'e', 'E']
    """
    seen = set()
    if key is None:
        for item in items:
            if item not in seen:
                seen.add(item)
                yield item
    else:
        for item in items:
            norm = key(item)
            if norm not in seen:
                seen.add(norm)
                yield item


def argunique(items, key=None):
    """
    Returns indices corresponding to the first instance of each unique item.

    Args:
        items (list): list of items

        key (Function, optional): custom normalization function.
            If specified returns items where `key(item)` is unique.

    Yields:
        int : indices of the unique items

    Example:
        >>> items = [0, 2, 5, 1, 1, 0, 2, 4]
        >>> indices = list(argunique(items))
        >>> assert indices == [0, 1, 2, 3, 7]
        >>> indices = list(argunique(items, key=lambda x: x % 2 == 0))
        >>> assert indices == [0, 2]
    """
    # yield from unique(range(len(items)), key=lambda i: items[i])
    if key is None:
        return unique(range(len(items)), key=lambda i: items[i])
    else:
        return unique(range(len(items)), key=lambda i: key(items[i]))


def unique_flags(items, key=None):
    """
    Returns a list of booleans corresponding to the first instance of each
    unique item.

    Args:
        items (list): list of items

        key (Function, optional): custom normalization function.
            If specified returns items where `key(item)` is unique.

    Returns:
        list of bools : flags the items that are unique

    Example:
        >>> import ubelt as ub
        >>> items = [0, 2, 1, 1, 0, 9, 2]
        >>> flags = unique_flags(items)
        >>> assert flags == [True, True, True, False, False, True, False]
        >>> flags = unique_flags(items, key=lambda x: x % 2 == 0)
        >>> assert flags == [True, False, True, False, False, False, False]
    """
    len_ = len(items)
    if key is None:
        item_to_index = dict(zip(reversed(items), reversed(range(len_))))
        indices = item_to_index.values()
    else:
        indices = argunique(items, key=key)
    flags = boolmask(indices, len_)
    return flags


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


def iter_window(iterable, size=2, step=1, wrap=False):
    """
    Iterates through iterable with a window size. This is essentially a 1D
    sliding window.

    Args:
        iterable (iter): an iterable sequence

        size (int): sliding window size (default = 2)

        step (int): sliding step size (default = 1)

        wrap (bool): wraparound (default = False)

    Returns:
        iter: returns windows in a sequence

    Example:
        >>> iterable = [1, 2, 3, 4, 5, 6]
        >>> size, step, wrap = 3, 1, True
        >>> window_iter = iter_window(iterable, size, step, wrap)
        >>> window_list = list(window_iter)
        >>> print('window_list = %r' % (window_list,))
        window_list = [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 1), (6, 1, 2)]

    Example:
        >>> iterable = [1, 2, 3, 4, 5, 6]
        >>> size, step, wrap = 3, 2, True
        >>> window_iter = iter_window(iterable, size, step, wrap)
        >>> window_list = list(window_iter)
        >>> print('window_list = %r' % (window_list,))
        window_list = [(1, 2, 3), (3, 4, 5), (5, 6, 1)]

    Example:
        >>> iterable = [1, 2, 3, 4, 5, 6]
        >>> size, step, wrap = 3, 2, False
        >>> window_iter = iter_window(iterable, size, step, wrap)
        >>> window_list = list(window_iter)
        >>> print('window_list = %r' % (window_list,))
        window_list = [(1, 2, 3), (3, 4, 5)]

    Example:
        >>> iterable = []
        >>> size, step, wrap = 3, 2, False
        >>> window_iter = iter_window(iterable, size, step, wrap)
        >>> window_list = list(window_iter)
        >>> print('window_list = %r' % (window_list,))
        window_list = []
    """
    # it.tee may be slow, but works on all iterables
    iter_list = it.tee(iterable, size)
    if wrap:
        # Secondary iterables need to be cycled for wraparound
        iter_list = [iter_list[0]] + list(map(it.cycle, iter_list[1:]))
    # Step each iterator the approprate number of times
    try:
        for count, iter_ in enumerate(iter_list[1:], start=1):
            for _ in range(count):
                next(iter_)
    except StopIteration:
        return iter(())
    else:
        _window_iter = zip(*iter_list)
        # Account for the step size
        window_iter = it.islice(_window_iter, 0, None, step)
        return window_iter


def allsame(iterable, eq=operator.eq):
    """
    Determine if all items in a sequence are the same

    Args:
        iterable (iter): an iterable sequence

        eq (Function, optional): function to determine equality
            (default: operator.eq)

    Example:
        >>> allsame([1, 1, 1, 1])
        True
        >>> allsame([])
        True
        >>> allsame([0, 1])
        False
        >>> iterable = iter([0, 1, 1, 1])
        >>> next(iterable)
        >>> allsame(iterable)
        True
        >>> allsame(range(10))
        False
        >>> allsame(range(10), lambda a, b: True)
        True
    """
    iter_ = iter(iterable)
    try:
        first = next(iter_)
    except StopIteration:
        return True
    return all(eq(first, item) for item in iter_)


def argsort(indexable, key=None, reverse=False):
    """
    Returns the indices that would sort a indexable object.

    This is similar to np.argsort, but it is written in pure python and works
    on both lists and dictionaries.

    Args:
        indexable (list or dict): indexable to sort by

        key (Function, optional): customizes the ordering of the indexable

        reverse (bool, optional): if True returns in descending order

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


def argmax(indexable, key=None):
    """
    Returns index / key of the item with the largest value.

    The current implementation is simply a convinience wrapper around
    `ub.argsort`, a more efficient version will be written in the future.

    Args:
        indexable (list or dict): indexable to sort by

        key (Function, optional): customizes the ordering of the indexable

    Example:
        >>> assert argmax({'a': 3, 'b': 2, 'c': 100}) == 'c'
        >>> assert argmax(['a', 'c', 'b', 'z', 'f']) == 3
        >>> assert argmax([[0, 1], [2, 3, 4], [5]], key=len) == 1
        >>> assert argmax({'a': 3, 'b': 2, 3: 100, 4: 4}) == 3
        >>> #import pytest
        >>> #with pytest.raises(TypeError):
        >>> #    argmax({'a': 3, 'b': 2, 3: 100, 4: 'd'})
    """
    return argsort(indexable, key=key)[-1]


def argmin(indexable, key=None):
    """
    Returns index / key of the item with the smallest value.

    The current implementation is simply a convinience wrapper around
    `ub.argsort`, a more efficient version will be written in the future.

    Args:
        indexable (list or dict): indexable to sort by

        key (Function, optional): customizes the ordering of the indexable

    Example:
        >>> assert argmin({'a': 3, 'b': 2, 'c': 100}) == 'b'
        >>> assert argmin(['a', 'c', 'b', 'z', 'f']) == 0
        >>> assert argmin([[0, 1], [2, 3, 4], [5]], key=len) == 2
        >>> assert argmin({'a': 3, 'b': 2, 3: 100, 4: 4}) == 'b'
        >>> #import pytest
        >>> #assert pytest.raises(TypeError):
        >>> #    argmax({'a': 3, 'b': 2, 3: 100, 4: 'd'})
    """
    return argsort(indexable, key=key)[0]


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
