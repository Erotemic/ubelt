# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from six.moves import zip, range
from six import next
import itertools as it
import collections
import weakref


class _Link(object):
    __slots__ = ('prev', 'next', 'key', '__weakref__')


class OrderedSet(collections.MutableSet):
    """
    Set the remembers the order elements were added

     Big-O running times for all methods are the same as for regular sets.
     The internal self._map dictionary maps keys to links in a doubly linked list.
     The circular doubly linked list starts and ends with a sentinel element.
     The sentinel element never gets deleted (this simplifies the algorithm).
     The prev/next links are weakref proxies (to prevent circular references).
     Individual links are kept alive by the hard reference in self._map.
     Those hard references disappear when a key is deleted from an OrderedSet.

    References:
        http://code.activestate.com/recipes/576696/
        http://code.activestate.com/recipes/576694/
        http://stackoverflow.com/questions/1653970/does-python-have-an-ordered-set

    Example:
        >>> from ubelt.orderedset import *
        >>> oset([1, 2, 3])
        OrderedSet([1, 2, 3])
    """

    def __init__(self, iterable=None):
        self._root = root = _Link()  # sentinel node for doubly linked list
        root.prev = root.next = root
        self._map = {}  # key --> link
        if iterable is not None:
            self |= iterable

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __len__(self):
        """
        Returns the number of unique elements in the ordered set

        Example:
            >>> assert len(OrderedSet([])) == 0
            >>> assert len(OrderedSet([1, 2])) == 2
        """
        return len(self._map)

    def __contains__(self, key):
        """
        Test if the item is in this ordered set

        Example:
            >>> assert 1 in OrderedSet([1, 3, 2])
            >>> assert 5 not in OrderedSet([1, 3, 2])
        """
        return key in self._map

    def __eq__(self, other):
        """
        Returns true if the containers have the same items regardless of order.

        Example:
            >>> self = OrderedSet([1, 3, 2])
            >>> assert self == [1, 3, 2]
            >>> assert self == [1, 2, 3]
            >>> assert self != [2, 3]
            >>> assert self == OrderedSet([3, 2, 1])
        """
        if len(self) == len(other):
            return set(self) == set(other)
        return False

    def isdisjoint(self, other):
        # Hack because apparently the inherited disjoint is now working
        return len(self.intersection(other)) == 0

    def __iter__(self):
        """
        Example:
            >>> list(iter(OrderedSet([1, 2, 3])))
            [1, 2, 3]
        """
        # Traverse the linked list in order.
        root = self._root
        curr = root.next
        while curr is not root:
            yield curr.key
            curr = curr.next

    def __reversed__(self):
        """
        Example:
            >>> list(reversed(OrderedSet([1, 2, 3])))
            [3, 2, 1]
        """
        # Traverse the linked list in reverse order.
        root = self._root
        curr = root.prev
        while curr is not root:
            yield curr.key
            curr = curr.prev

    def _iterslice(self, sl):
        """
        Iterate over items at indices specified by a slice

        Example:
            >>> self = oset([1, 2, 3, 4, 5, 6, 7, 8])
            >>> items = list(self._iterslice(slice(1, None, 2)))
            >>> assert items == [2, 4, 6, 8]
        """
        indices = iter(range(*sl.indices(len(self))))
        target = next(indices)
        for index, item in enumerate(self):  # pragma: nobranch
            if index == target:
                yield item
                target = next(indices)

    def __getitem__(self, index):
        """
        Access an item within the ordered set.

        Note:
            Lookup time is O(n)

        Example:
            >>> import pytest
            >>> self = oset([1, 2, 3])
            >>> assert self[0] == 1
            >>> assert self[1] == 2
            >>> assert self[2] == 3
            >>> with pytest.raises(IndexError):
            ...     self[3]
            >>> assert self[-1] == 3
            >>> assert self[-2] == 2
            >>> assert self[-3] == 1
            >>> with pytest.raises(IndexError):
            ...     self[-4]
            >>> assert self[::2] == [1, 3]
            >>> assert self[0:2] == [1, 2]
            >>> assert self[-1:] == [3]
            >>> assert self[:] == self
            >>> assert self[:] is not self
        """
        if isinstance(index, slice):
            return self.__class__(self._iterslice(index))
        else:
            if index < 0:
                iter_ = self.__reversed__
                index_ = -1 - index
            else:
                index_ = index
                iter_ = self.__iter__
            if index_ >= len(self):
                raise IndexError('index %r out of range %r' % (
                    index, len(self)))
            for count, item in zip(range(index_ + 1), iter_()):
                pass
            return item

    def add(self, key):
        """
        Adds an element to the ends of the ordered set if it.
        This has no effect if the element is already present.

        Example:
            >>> self = OrderedSet()
            >>> self.append(3)
            >>> print(self)
            OrderedSet([3])
        """
        # Store new key in a new link at the end of the linked list
        if key not in self._map:
            self._map[key] = link = _Link()
            root = self._root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = root.prev = weakref.proxy(link)

    def append(self, key):
        """
        Adds an element to the ends of the ordered set if it.
        This has no effect if the element is already present.

        Notes:
            This is an alias of `add` for API compatibility with list

        Example:
            >>> self = OrderedSet()
            >>> self.append(3)
            >>> self.append(2)
            >>> self.append(5)
            >>> print(self)
            OrderedSet([3, 2, 5])
        """
        return self.add(key)

    def discard(self, key):
        """
        Remove an element from a set if it is a member.
        If the element is not a member, do nothing.

        Example:
            >>> self = OrderedSet([1, 2, 3])
            >>> self.discard(2)
            >>> print(self)
            OrderedSet([1, 3])
            >>> self.discard(2)
            >>> print(self)
            OrderedSet([1, 3])
        """
        # Remove an existing item using self._map to find the link which is
        # then removed by updating the links in the predecessor and successors.
        if key in self._map:
            link = self._map.pop(key)
            link.prev.next = link.next
            link.next.prev = link.prev

    def pop(self, last=True):
        """
        Remove and return a the first or last element in the ordered set.
        Raises KeyError if the set is empty.

        Args:
            last (bool): if True return the last element otherwise the first
                (defaults to True).

        Example:
            >>> import pytest
            >>> self = oset([2, 3, 1])
            >>> assert self.pop(last=True) == 1
            >>> assert self.pop(last=False) == 2
            >>> assert self.pop() == 3
            >>> with pytest.raises(KeyError):
            ...     self.pop()
        """
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def union(self, *sets):
        """
        Combines all unique items.
        Each items order is defined by its first appearance.

        Example:
            >>> self = OrderedSet.union(oset([3, 1, 4, 1, 5]), [1, 3], [2, 0])
            >>> print(self)
            OrderedSet([3, 1, 4, 5, 2, 0])
            >>> self.union([8, 9])
            OrderedSet([3, 1, 4, 5, 2, 0, 8, 9])
            >>> self | {10}
            OrderedSet([3, 1, 4, 5, 2, 0, 10])
        """
        cls = self.__class__ if isinstance(self, OrderedSet) else OrderedSet
        containers = map(list, it.chain([self], sets))
        items = it.chain.from_iterable(containers)
        return cls(items)

    def intersection(self, *sets):
        """
        Returns elements in common between all sets. Order is defined only
        by the first set.

        Example:
            >>> self = OrderedSet.intersection(oset([0, 1, 2, 3]), [1, 2, 3])
            >>> print(self)
            OrderedSet([1, 2, 3])
            >>> self.intersection([2, 4, 5], [1, 2, 3, 4])
            OrderedSet([2])
        """
        cls = self.__class__ if isinstance(self, OrderedSet) else OrderedSet
        common = set.intersection(*map(set, sets))
        items = (item for item in self if item in common)
        return cls(items)

    def update(self, other):
        """
        Update a set with the union of itself and others.
        Preserves ordering of `other`.

        Example:
            >>> self = OrderedSet([1, 2, 3])
            >>> self.update([3, 1, 5, 1, 4])
            >>> print(self)
            OrderedSet([1, 2, 3, 5, 4])
        """
        for item in other:
            self.add(item)

    extend = update  # alias of update

    def index(self, item):
        """
        Find the index of `item` in the OrderedSet

        Example:
            >>> import pytest
            >>> self = oset([1, 2, 3])
            >>> assert self.index(1) == 0
            >>> assert self.index(2) == 1
            >>> assert self.index(3) == 2
            >>> with pytest.raises(IndexError):
            ...     self[4]
        """
        for count, other in enumerate(self):
            if item == other:
                return count
        raise ValueError('%r is not in OrderedSet' % (item,))

    def copy(self):
        """
        Return a shallow copy of the ordered set.

        Example:
            >>> self = OrderedSet([1, 2, 3])
            >>> other = self.copy()
            >>> assert self == other and self is not other
        """
        return self.__class__(self)

    def difference(self, *sets):
        """
        Returns all elements that are in this set but not the others.

        Example:
            >>> OrderedSet([1, 2, 3]).difference(OrderedSet([2]))
            OrderedSet([1, 3])
            >>> OrderedSet([1, 2, 3]) - OrderedSet([2])
            OrderedSet([1, 3])
        """
        cls = self.__class__
        other = set.intersection(*map(set, sets))
        return cls(item for item in self if item not in other)

    def issubset(self, other):
        """
        Report whether another set contains this set.

        Example:
            >>> OrderedSet([1, 2, 3]).issubset({1, 2})
            False
            >>> OrderedSet([1, 2, 3]).issubset({1, 2, 3, 4})
            True
            >>> OrderedSet([1, 2, 3]).issubset({1, 4, 3, 5})
            False
        """
        if len(self) > len(other):  # Fast check for obvious cases
            return False
        return all(item in other for item in self)

    def issuperset(self, other):
        """
        Report whether this set contains another set.

        Example:
            >>> OrderedSet([1, 2]).issuperset([1, 2, 3])
            False
            >>> OrderedSet([1, 2, 3, 4]).issuperset({1, 2, 3})
            True
            >>> OrderedSet([1, 4, 3, 5]).issuperset({1, 2, 3})
            False
        """
        if len(self) < len(other):  # Fast check for obvious cases
            return False
        return all(item in self for item in other)

    def symmetric_difference(self, other):
        """
        Return the symmetric difference of two sets as a new set.
        (I.e. all elements that are in exactly one of the sets.)

        Example:
            >>> self = OrderedSet([1, 4, 3, 5, 7])
            >>> other = OrderedSet([9, 7, 1, 3, 2])
            >>> self.symmetric_difference(other)
            OrderedSet([4, 5, 9, 2])
        """
        cls = self.__class__ if isinstance(self, OrderedSet) else OrderedSet
        diff1 = cls(self).difference(other)
        diff2 = cls(other).difference(self)
        return diff1.union(diff2)

    def difference_update(self, *sets):
        """
        Returns a copy of self with items from other removed

        Example:
            >>> self = OrderedSet([1, 2, 3])
            >>> self.difference_update(OrderedSet([2]))
            >>> print(self)
            OrderedSet([1, 3])
        """
        for item in it.chain.from_iterable(sets):
            self.discard(item)

    def intersection_update(self, other):
        """
        Update a set with the intersection of itself and another.
        Order depends only on the first element

        Example:
            >>> self = OrderedSet([1, 4, 3, 5, 7])
            >>> other = OrderedSet([9, 7, 1, 3, 2])
            >>> self.intersection_update(other)
            >>> print(self)
            OrderedSet([1, 3, 7])
        """
        to_remove = [item for item in self if item not in other]
        for item in to_remove:
            self.discard(item)

    def symmetric_difference_update(self, other):
        """
        Update a set with the intersection of itself and another.
        Order depends only on the first element

        Example:
            >>> self = OrderedSet([1, 4, 3, 5, 7])
            >>> other = OrderedSet([9, 7, 1, 3, 2])
            >>> self.symmetric_difference_update(other)
            >>> print(self)
            OrderedSet([4, 5, 9, 2])
        """
        cls = self.__class__ if isinstance(self, OrderedSet) else OrderedSet
        diff2 = cls(other).difference(self)
        self.difference_update(other)
        self.update(diff2)


# alias
oset = OrderedSet


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.orderedset all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
