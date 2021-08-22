# -*- coding: utf-8 -*-
"""
Utility functions for manipulating iterables, lists, and sequences.

The :func:`chunks` function splits a list into smaller parts. There are different strategies for how to do this.

The :func:`flatten` function take a list of lists and removees the inner lists. This
only removes one level of nesting.

The :func:`iterable` function checks if an object is iterable or not. Similar to the
:func:`callable` builtin function.

The :func:`argmax`, :func:`argmin`, and :func:`argsort` work similarly to the
analogous :mod:`numpy` functions, except they operate on dictionaries and other
Python builtin types.

The :func:`take` and :func:`compress` are generators, and also similar to their
lesser known, but very useful numpy equivalents.

There are also other numpy inspired functions: :func:`unique`,
:func:`argunique`, :func:`unique_flags`, and :func:`boolmask`.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import itertools as it
import sys
import math
import operator
from ubelt import util_const

__all__ = [
    'allsame', 'argmax', 'argmin', 'argsort', 'argunique', 'boolmask',
    'chunks', 'compress', 'flatten', 'iter_window', 'iterable', 'peek', 'take',
    'unique', 'unique_flags',
]

PY2 = sys.version_info[0] == 2

if PY2:
    import six
    import collections as collections_abc
    from six import next
    from six.moves import zip_longest
    string_types = six.string_types
else:
    from collections import abc as collections_abc
    from itertools import zip_longest
    string_types = (str,)


class chunks(object):
    """
    Generates successive n-sized chunks from ``items``.

    If the last chunk has less than n elements, ``bordermode`` is used to
    determine fill values.

    Args:
        items (Iterable[T]): input to iterate over

        chunksize (int): size of each sublist yielded

        nchunks (int): number of chunks to create (
            cannot be specified if chunksize is specified)

        bordermode (str): determines how to handle the last case if the
            length of the input is not divisible by chunksize valid values
            are: {'none', 'cycle', 'replicate'}

        total (int): hints about the length of the input

    Yields:
        List[T]: subsequent non-overlapping chunks of the input items

    References:
        http://stackoverflow.com/questions/434287/iterate-over-a-list-in-chunks

    Example:
        >>> import ubelt as ub
        >>> items = '1234567'
        >>> genresult = ub.chunks(items, chunksize=3)
        >>> list(genresult)
        [['1', '2', '3'], ['4', '5', '6'], ['7']]

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 3, 4, 5, 6, 7]
        >>> genresult = ub.chunks(items, chunksize=3, bordermode='none')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7]]
        >>> genresult = ub.chunks(items, chunksize=3, bordermode='cycle')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7, 1, 2]]
        >>> genresult = ub.chunks(items, chunksize=3, bordermode='replicate')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7, 7, 7]]

    Example:
        >>> import ubelt as ub
        >>> assert len(list(ub.chunks(range(2), nchunks=2))) == 2
        >>> assert len(list(ub.chunks(range(3), nchunks=2))) == 2
        >>> # Note: ub.chunks will not do the 2,1,1 split
        >>> assert len(list(ub.chunks(range(4), nchunks=3))) == 2
        >>> assert len(list(ub.chunks([], 2, None, 'none'))) == 0
        >>> assert len(list(ub.chunks([], 2, None, 'cycle'))) == 0
        >>> assert len(list(ub.chunks([], 2, None, 'replicate'))) == 0

    Example:
        >>> def _check_len(self):
        ...     assert len(self) == len(list(self))
        >>> _check_len(chunks(list(range(3)), nchunks=2))
        >>> _check_len(chunks(list(range(2)), nchunks=2))
        >>> _check_len(chunks(list(range(2)), nchunks=3))

    Example:
        >>> import pytest
        >>> assert pytest.raises(ValueError, chunks, range(9))
        >>> assert pytest.raises(ValueError, chunks, range(9), chunksize=2, nchunks=2)
        >>> assert pytest.raises(TypeError, len, chunks((_ for _ in range(2)), 2))

    """
    def __init__(self, items, chunksize=None, nchunks=None, total=None,
                 bordermode='none'):
        if nchunks is not None and chunksize is not None:  # nocover
            raise ValueError('Cannot specify both chunksize and nchunks')
        if nchunks is None and chunksize is None:  # nocover
            raise ValueError('Must specify either chunksize or nchunks')
        if nchunks is not None:
            if total is None:
                total = len(items)
            chunksize = int(math.ceil(total / nchunks))

        self.bordermode = bordermode
        self.items = items
        self.chunksize = chunksize
        self.total = total

    def __len__(self):
        if self.total is None:
            self.total = len(self.items)
        nchunks = int(math.ceil(self.total / self.chunksize))
        return nchunks

    def __iter__(self):
        bordermode = self.bordermode
        items = self.items
        chunksize = self.chunksize
        if bordermode is None or bordermode == 'none':
            return self.noborder(items, chunksize)
        elif bordermode == 'cycle':
            return self.cycle(items, chunksize)
        elif bordermode == 'replicate':
            return self.replicate(items, chunksize)
        else:
            raise ValueError('unknown bordermode=%r' % (bordermode,))

    @staticmethod
    def noborder(items, chunksize):
        # feed the same iter to zip_longest multiple times, this causes it to
        # consume successive values of the same sequence
        sentinal = object()
        copied_iters = [iter(items)] * chunksize
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        # Dont fill empty space in the last chunk, just return it as is
        for chunk in chunks_with_sentinals:
            yield [item for item in chunk if item is not sentinal]

    @staticmethod
    def cycle(items, chunksize):
        sentinal = object()
        copied_iters = [iter(items)] * chunksize
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        # Fill empty space in the last chunk with values from the beginning
        bordervalues = it.cycle(iter(items))
        for chunk in chunks_with_sentinals:
            yield [item if item is not sentinal else next(bordervalues)
                   for item in chunk]

    @staticmethod
    def replicate(items, chunksize):
        sentinal = object()
        copied_iters = [iter(items)] * chunksize
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
    for strings, which return False unless ``strok`` is True

    Args:
        obj (object): a scalar or iterable input

        strok (bool, default=False):
            if True allow strings to be interpreted as iterable

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
        return strok or not isinstance(obj, string_types)


def take(items, indices, default=util_const.NoParam):
    """
    Selects a subset of a list based on a list of indices.

    This is similar to ``np.take``, but pure python. This also supports
    specifying a default element if ``items`` is an iterable of dictionaries.

    Args:
        items (Sequence[V] | Mapping[K, V]):
            An indexable object to select items from

        indices (Iterable[int | K]):
            sequence of indexes into ``items``

        default (Any, default=NoParam):
            if specified ``items`` must support the ``get`` method.

    Yeilds:
        V: a selected item within the list

    SeeAlso:
        :func:`ub.dict_subset`

    Notes:
        ``ub.take(items, indices)`` is equivalent to
        ``(items[i] for i in indices)`` when ``default`` is unspecified.

    Example:
        >>> import ubelt as ub
        >>> items = [0, 1, 2, 3]
        >>> indices = [2, 0]
        >>> list(ub.take(items, indices))
        [2, 0]

    Example:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> result = list(ub.take(dict_, keys, None))
        >>> assert result == ['a', 'b', 'c', None, None]

    Example:
        >>> import ubelt as ub
        >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
        >>> keys = [1, 2, 3, 4, 5]
        >>> try:
        >>>     print(list(ub.take(dict_, keys)))
        >>>     raise AssertionError('did not get key error')
        >>> except KeyError:
        >>>     print('correctly got key error')
    """
    if default is util_const.NoParam:
        for index in indices:
            yield items[index]
    else:
        for index in indices:
            yield items.get(index, default)


def compress(items, flags):
    """
    Selects from ``items`` where the corresponding value in ``flags`` is True.
    This is similar to :func:`numpy.compress`.

    This is actually a simple alias for :func:`itertools.compress`.

    Args:
        items (Iterable[Any]): a sequence to select items from

        flags (Iterable[bool]): corresponding sequence of bools

    Returns:
        Iterable[Any]: a subset of masked items

    Example:
        >>> import ubelt as ub
        >>> items = [1, 2, 3, 4, 5]
        >>> flags = [False, True, True, False, True]
        >>> list(ub.compress(items, flags))
        [2, 3, 5]
    """
    return it.compress(items, flags)


def flatten(nested):
    """
    Transforms a nested iterable into a flat iterable.

    This is simply an alias for :func:`itertools.chain.from_iterable`.

    Args:
        nested (Iterable[Iterable[Any]]): list of lists

    Returns:
        Iterable[Any]: flattened items

    Example:
        >>> import ubelt as ub
        >>> nested = [['a', 'b'], ['c', 'd']]
        >>> list(ub.flatten(nested))
        ['a', 'b', 'c', 'd']
    """
    return it.chain.from_iterable(nested)


def unique(items, key=None):
    """
    Generates unique items in the order they appear.

    Args:
        items (Iterable[A]): list of items

        key (Callable[[A], B], default=None): custom normalization function.
            If specified returns items where ``key(item)`` is unique.

    Yields:
        A: a unique item from the input sequence

    Example:
        >>> import ubelt as ub
        >>> items = [4, 6, 6, 0, 6, 1, 0, 2, 2, 1]
        >>> unique_items = list(ub.unique(items))
        >>> assert unique_items == [4, 6, 0, 1, 2]

    Example:
        >>> import ubelt as ub
        >>> import six
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
        items (Sequence[V]): indexable collection of items

        key (Callable[[V], Any], default=None): custom normalization function.
            If specified returns items where ``key(item)`` is unique.

    Returns:
        Iterator[int] : indices of the unique items

    Example:
        >>> items = [0, 2, 5, 1, 1, 0, 2, 4]
        >>> indices = list(argunique(items))
        >>> assert indices == [0, 1, 2, 3, 7]
        >>> indices = list(argunique(items, key=lambda x: x % 2 == 0))
        >>> assert indices == [0, 2]
    """
    if key is None:
        return unique(range(len(items)), key=lambda i: items[i])
    else:
        return unique(range(len(items)), key=lambda i: key(items[i]))


def unique_flags(items, key=None):
    """
    Returns a list of booleans corresponding to the first instance of each
    unique item.

    Args:
        items (Sequence): indexable collection of items

        key (Callable[[V], Any], default=None): custom normalization function.
            If specified returns items where ``key(item)`` is unique.

    Returns:
        List[bool] : flags the items that are unique

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
    ``indices`` otherwise it is False.

    Args:
        indices (List[int]): list of integer indices

        maxval (int): length of the returned list. If not specified
            this is inferred using ``max(indices)``

    Returns:
        List[bool]:
            mask - a list of booleans. mask[idx] is True if idx in indices

    Note:
        In the future the arg ``maxval`` may change its name to ``shape``

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
        iterable (Iterable[T]): an iterable sequence

        size (int, default=2): sliding window size

        step (int, default=1): sliding step size

        wrap (bool, default=False): wraparound flag

    Returns:
        Iterable[T]: returns a possibly overlaping windows in a sequence

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
        >>> print('window_list = {!r}'.format(window_list))
        window_list = [(1, 2, 3), (3, 4, 5), (5, 6, 1)]

    Example:
        >>> iterable = [1, 2, 3, 4, 5, 6]
        >>> size, step, wrap = 3, 2, False
        >>> window_iter = iter_window(iterable, size, step, wrap)
        >>> window_list = list(window_iter)
        >>> print('window_list = {!r}'.format(window_list))
        window_list = [(1, 2, 3), (3, 4, 5)]

    Example:
        >>> iterable = []
        >>> size, step, wrap = 3, 2, False
        >>> window_iter = iter_window(iterable, size, step, wrap)
        >>> window_list = list(window_iter)
        >>> print('window_list = {!r}'.format(window_list))
        window_list = []
    """
    # it.tee may be slow, but works on all iterables
    iter_list = it.tee(iterable, size)
    if wrap:
        # Secondary iterables need to be cycled for wraparound
        iter_list = [iter_list[0]] + list(map(it.cycle, iter_list[1:]))
    # Step each iterator the appropriate number of times
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
        iterable (Iterable[A]):
            items to determine if they are all the same

        eq (Callable[[A, A], bool], default=operator.eq):
            function used to test for equality

    Returns:
        bool: True if all items are equal, otherwise False

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

    This is similar to :func:`numpy.argsort`, but it is written in pure python
    and works on both lists and dictionaries.

    Args:
        indexable (Iterable[B] | Mapping[A, B]): indexable to sort by

        key (Callable[[A], B], default=None):
            customizes the ordering of the indexable

        reverse (bool, default=False): if True returns in descending order

    Returns:
        List[int]: indices - list of indices such that sorts the indexable

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
    if isinstance(indexable, collections_abc.Mapping):
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

    This is similar to :func:`numpy.argmax`, but it is written in pure python
    and works on both lists and dictionaries.

    Args:
        indexable (Iterable[B] | Mapping[A, B]): indexable to sort by

        key (Callable[[A], B], default=None):
            customizes the ordering of the indexable

    Returns:
        int: the index of the item with the maximum value.

    Example:
        >>> assert argmax({'a': 3, 'b': 2, 'c': 100}) == 'c'
        >>> assert argmax(['a', 'c', 'b', 'z', 'f']) == 3
        >>> assert argmax([[0, 1], [2, 3, 4], [5]], key=len) == 1
        >>> assert argmax({'a': 3, 'b': 2, 3: 100, 4: 4}) == 3
        >>> assert argmax(iter(['a', 'c', 'b', 'z', 'f'])) == 3
    """
    if key is None and isinstance(indexable, collections_abc.Mapping):
        return max(indexable.items(), key=operator.itemgetter(1))[0]
    elif hasattr(indexable, 'index'):
        if key is None:
            return indexable.index(max(indexable))
        else:
            return indexable.index(max(indexable, key=key))
    else:
        # less efficient, but catch all solution
        return argsort(indexable, key=key)[-1]


def argmin(indexable, key=None):
    """
    Returns index / key of the item with the smallest value.

    This is similar to :func:`numpy.argmin`, but it is written in pure python
    and works on both lists and dictionaries.

    Args:
        indexable (Iterable[B] | Mapping[A, B]): indexable to sort by

        key (Callable[[A], B], default=None):
            customizes the ordering of the indexable

    Returns:
        int: the index of the item with the minimum value.

    Example:
        >>> assert argmin({'a': 3, 'b': 2, 'c': 100}) == 'b'
        >>> assert argmin(['a', 'c', 'b', 'z', 'f']) == 0
        >>> assert argmin([[0, 1], [2, 3, 4], [5]], key=len) == 2
        >>> assert argmin({'a': 3, 'b': 2, 3: 100, 4: 4}) == 'b'
        >>> assert argmin(iter(['a', 'c', 'A', 'z', 'f'])) == 2
    """
    if key is None and isinstance(indexable, collections_abc.Mapping):
        return min(indexable.items(), key=operator.itemgetter(1))[0]
    elif hasattr(indexable, 'index'):
        if key is None:
            return indexable.index(min(indexable))
        else:
            return indexable.index(min(indexable, key=key))
    else:
        # less efficient, but catch all solution
        return argsort(indexable, key=key)[0]


def peek(iterable):
    """
    Look at the first item of an iterable. If the input is an iterator, then
    the next element is exhausted (i.e. a pop operation).

    Args:
        iterable (List[T]): an iterable

    Returns:
        T: item - the first item of ordered sequence, a popped item from an
                 iterator, or an arbitrary item from an unordered collection.

    Example:
        >>> import ubelt as ub
        >>> data = [0, 1, 2]
        >>> ub.peek(data)
        0
        >>> iterator = iter(data)
        >>> print(ub.peek(iterator))
        0
        >>> print(ub.peek(iterator))
        1
        >>> print(ub.peek(iterator))
        2
        >>> ub.peek(range(3))
        0
    """
    return next(iter(iterable))
