from typing import List
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Iterator
from collections.abc import MutableSet, Sequence

SLICE_ALL: slice


def is_iterable(obj) -> bool:
    ...


class OrderedSet(MutableSet, Sequence):
    items: List[Any]
    map: Dict[Any, int]

    def __init__(self, iterable: None | Iterable = None) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, index: int | slice | Any) -> List | OrderedSet | Any:
        ...

    def copy(self) -> OrderedSet:
        ...

    def __contains__(self, key: Any) -> bool:
        ...

    def add(self, key: Any):
        ...

    append = add

    def update(self, sequence: Iterable):
        ...

    def index(self, key: Any, start: int = 0, stop: int | None = None) -> int:
        ...

    get_loc = index
    get_indexer = index

    def pop(self) -> Any:
        ...

    def discard(self, key: Any) -> None:
        ...

    def clear(self) -> None:
        ...

    def __iter__(self) -> Iterator:
        ...

    def __reversed__(self) -> Iterator:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def union(self, *sets) -> OrderedSet:
        ...

    def __and__(self, other):
        ...

    def intersection(self, *sets) -> OrderedSet:
        ...

    def difference(self, *sets) -> OrderedSet:
        ...

    def issubset(self, other: Iterable) -> bool:
        ...

    def issuperset(self, other: Iterable) -> bool:
        ...

    def symmetric_difference(self, other: Iterable) -> OrderedSet:
        ...

    def difference_update(self, *sets) -> None:
        ...

    def intersection_update(self, other: Iterable) -> None:
        ...

    def symmetric_difference_update(self, other: Iterable) -> None:
        ...


oset = OrderedSet
