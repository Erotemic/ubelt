from typing import List
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Iterator
from collections.abc import MutableSet, Sequence

SLICE_ALL: slice


def is_iterable(obj):
    ...


class OrderedSet(MutableSet, Sequence):
    items: List[Any]
    map: Dict[Any, int]

    def __init__(self, iterable: None | Iterable = None) -> None:
        ...

    def __len__(self):
        ...

    def __getitem__(self, index):
        ...

    def copy(self) -> OrderedSet:
        ...

    def __contains__(self, key) -> bool:
        ...

    def add(self, key):
        ...

    append = add

    def update(self, sequence):
        ...

    def index(self, key):
        ...

    get_loc = index
    get_indexer = index

    def pop(self) -> Any:
        ...

    def discard(self, key) -> None:
        ...

    def clear(self) -> None:
        ...

    def __iter__(self) -> Iterator:
        ...

    def __reversed__(self) -> Iterator:
        ...

    def __eq__(self, other) -> bool:
        ...

    def union(self, *sets) -> OrderedSet:
        ...

    def __and__(self, other):
        ...

    def intersection(self, *sets) -> OrderedSet:
        ...

    def difference(self, *sets) -> OrderedSet:
        ...

    def issubset(self, other) -> bool:
        ...

    def issuperset(self, other) -> bool:
        ...

    def symmetric_difference(self, other) -> OrderedSet:
        ...

    def difference_update(self, *sets) -> None:
        ...

    def intersection_update(self, other) -> None:
        ...

    def symmetric_difference_update(self, other) -> None:
        ...


oset = OrderedSet
