from collections.abc import Generator
from typing import Any


class chunks:
    bordermode: Any
    items: Any
    chunksize: Any
    total: Any

    def __init__(self,
                 items,
                 chunksize: Any | None = ...,
                 nchunks: Any | None = ...,
                 total: Any | None = ...,
                 bordermode: str = ...) -> None:
        ...

    def __len__(self):
        ...

    def __iter__(self):
        ...

    @staticmethod
    def noborder(items, chunksize) -> Generator[Any, None, None]:
        ...

    @staticmethod
    def cycle(items, chunksize) -> Generator[Any, None, None]:
        ...

    @staticmethod
    def replicate(items, chunksize) -> Generator[Any, None, None]:
        ...


def iterable(obj, strok: bool = ...):
    ...


def take(items, indices, default=...) -> Generator[Any, None, None]:
    ...


def compress(items, flags):
    ...


def flatten(nested):
    ...


def unique(items, key: Any | None = ...) -> Generator[Any, None, None]:
    ...


def argunique(items, key: Any | None = ...):
    ...


def unique_flags(items, key: Any | None = ...):
    ...


def boolmask(indices, maxval: Any | None = ...):
    ...


def iter_window(iterable, size: int = ..., step: int = ..., wrap: bool = ...):
    ...


def allsame(iterable, eq=...):
    ...


def argsort(indexable, key: Any | None = ..., reverse: bool = ...):
    ...


def argmax(indexable, key: Any | None = ...):
    ...


def argmin(indexable, key: Any | None = ...):
    ...


def peek(iterable):
    ...
