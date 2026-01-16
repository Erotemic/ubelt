from typing import Iterable
from typing import Mapping
from typing import Sequence
from typing import Any
from typing import Callable
from typing import Iterator
from typing import List
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any, TypeVar

VT = TypeVar("VT")
T = TypeVar("T")
KT = TypeVar("KT")


class chunks:
    remainder: int
    legacy: bool
    items: Iterable
    total: int | None
    nchunks: int | None
    chunksize: int | None
    bordermode: str

    def __init__(self,
                 items: Iterable,
                 chunksize: int | None = None,
                 nchunks: int | None = None,
                 total: int | None = None,
                 bordermode: str = 'none',
                 legacy: bool = False) -> None:
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


def iterable(obj: object, strok: bool = False) -> bool:
    ...


def take(items: Sequence[VT] | Mapping[KT, VT],
         indices: Iterable[int | KT],
         default: Any = ...) -> Generator[VT, None, None]:
    ...


def compress(items: Iterable[Any], flags: Iterable[bool]) -> Iterable[Any]:
    ...


def flatten(nested: Iterable[Iterable[Any]]) -> Iterable[Any]:
    ...


def unique(items: Iterable[T],
           key: Callable[[T], Any] | None = None) -> Generator[T, None, None]:
    ...


def argunique(items: Sequence[VT],
              key: Callable[[VT], Any] | None = None) -> Iterator[int]:
    ...


def unique_flags(items: Sequence[VT],
                 key: Callable[[VT], Any] | None = None) -> List[bool]:
    ...


def boolmask(indices: List[int], maxval: int | None = None) -> List[bool]:
    ...


def iter_window(iterable: Iterable[T],
                size: int = 2,
                step: int = 1,
                wrap: bool = False) -> Iterable[T]:
    ...


def allsame(iterable: Iterable[T], eq: Callable[[T, T], bool] = ...) -> bool:
    ...


def argsort(indexable: Iterable[VT] | Mapping[KT, VT],
            key: Callable[[VT], VT] | None = None,
            reverse: bool = False) -> List[int] | List[KT]:
    ...


def argmax(indexable: Iterable[VT] | Mapping[KT, VT],
           key: Callable[[VT], Any] | None = None) -> int | KT:
    ...


def argmin(indexable: Iterable[VT] | Mapping[KT, VT],
           key: Callable[[VT], VT] | None = None) -> int | KT:
    ...


def peek(iterable: Iterable[T], default: T = ...) -> T:
    ...


class IterableMixin:
    unique = unique
    histogram: Incomplete
    duplicates: Incomplete
    group: Incomplete

    def chunks(self,
               size: Incomplete | None = ...,
               num: Incomplete | None = ...,
               bordermode: str = ...):
        ...


class OrderedIterableMixin(IterableMixin):
    compress = compress
    argunique = argunique
    window = iter_window


class UList(list, OrderedIterableMixin):
    peek = peek
    take = take
    flatten = flatten
    allsame = allsame
    argsort = argsort
    argmax = argmax
    argmin = argmin
