# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import itertools as it
import six
from six.moves import zip_longest


class chunks(object):
    r"""
    Generates successive n-sized chunks from `iterable`.
    If the last chunk has less than n elements, `bordermode` is used to
    determine fill values.

    Args:
        iterable (list): input to iterate over
        chunksize (int): size of each sublist yielded
        bordermode (str): determines how to handle the last case if the
            length of the iterable is not divisible by chunksize valid values
            are: {'none', 'cycle', 'replicate'}

    References:
        http://stackoverflow.com/questions/434287/iterate-over-a-list-in-chunks

    CommandLine:
        python -m ubelt.util_list chunks

    Example:
        >>> import ubelt as ub
        >>> iterable = [1, 2, 3, 4, 5, 6, 7]
        >>> genresult = ub.chunks(iterable, chunksize=3, bordermode='none')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7]]
        >>> genresult = ub.chunks(iterable, chunksize=3, bordermode='cycle')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7, 1, 2]]
        >>> genresult = ub.chunks(iterable, chunksize=3, bordermode='replicate')
        >>> assert list(genresult) == [[1, 2, 3], [4, 5, 6], [7, 7, 7]]
    """
    def __init__(self, iterable, chunksize, bordermode='none'):
        self.bordermode = bordermode
        self.iterable = iterable
        self.chunksize = chunksize

    def __iter__(self):
        bordermode = self.bordermode
        iterable = self.iterable
        chunksize = self.chunksize
        if bordermode is None or bordermode == 'none':
            return self.noborder(iterable, chunksize)
        elif bordermode == 'cycle':
            return self.cycle(iterable, chunksize)
        elif bordermode == 'replicate':
            return self.replicate(iterable, chunksize)
        else:
            raise ValueError('unknown bordermode=%r' % (bordermode,))

    @staticmethod
    def noborder(iterable, chunksize):
        # feed the same iter to zip_longest multiple times, this causes it to
        # consume successive values of the same sequence
        sentinal = object()
        copied_iters = [iter(iterable)] * chunksize
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        # Dont fill empty space in the last chunk, just return it as is
        for chunk in chunks_with_sentinals:
            if len(chunk) > 0:
                yield [item for item in chunk if item is not sentinal]

    @staticmethod
    def cycle(iterable, chunksize):
        sentinal = object()
        copied_iters = [iter(iterable)] * chunksize
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        # Fill empty space in the last chunk with values from the beginning
        bordervalues = it.cycle(iter(iterable))
        for chunk in chunks_with_sentinals:
            if len(chunk) > 0:
                yield [item if item is not sentinal else six.next(bordervalues)
                       for item in chunk]

    @staticmethod
    def replicate(iterable, chunksize):
        sentinal = object()
        copied_iters = [iter(iterable)] * chunksize
        # Fill empty space in the last chunk by replicating the last value
        chunks_with_sentinals = zip_longest(*copied_iters, fillvalue=sentinal)
        for chunk in chunks_with_sentinals:
            if len(chunk) > 0:
                filt_chunk = [item for item in chunk if item is not sentinal]
                if len(filt_chunk) == chunksize:
                    yield filt_chunk
                else:
                    sizediff = (chunksize - len(filt_chunk))
                    padded_chunk = filt_chunk + [filt_chunk[-1]] * sizediff
                    yield padded_chunk


def take(items, indices):
    r"""
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
    r"""
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
    r"""
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


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_list
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
