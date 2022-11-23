from typing import Mapping
from typing import Sequence
from typing import Union
from typing import Iterable
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
    legacy: Incomplete
    remainder: Incomplete
    items: Incomplete
    total: Incomplete
    nchunks: Incomplete
    chunksize: Incomplete
    bordermode: Incomplete

    def __init__(self,
                 items,
                 chunksize: Incomplete | None = ...,
                 nchunks: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 bordermode: str = ...,
                 legacy: bool = ...) -> None:
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


def iterable(obj: object, strok: bool = ...) -> bool:
    ...


def take(items: Union[Sequence[VT], Mapping[KT, VT]],
         indices: Iterable[Union[int, KT]],
         default: Any = ...) -> Generator[VT, None, None]:
    ...


def compress(items: Iterable[Any], flags: Iterable[bool]) -> Iterable[Any]:
    ...


def flatten(nested: Iterable[Iterable[Any]]) -> Iterable[Any]:
    ...


def unique(items: Iterable[T],
           key: Callable[[T], Any] = ...) -> Generator[T, None, None]:
    ...


def argunique(items: Sequence[VT],
              key: Callable[[VT], Any] = ...) -> Iterator[int]:
    ...


def unique_flags(items: Sequence[VT],
                 key: Union[Callable[[VT], Any], None] = ...) -> List[bool]:
    ...


def boolmask(indices: List[int], maxval: int = ...) -> List[bool]:
    ...


def iter_window(iterable: Iterable[T],
                size: int = ...,
                step: int = ...,
                wrap: bool = ...) -> Iterable[T]:
    ...


def allsame(iterable: Iterable[T], eq: Callable[[T, T], bool] = ...) -> bool:
    ...


def argsort(indexable: Union[Iterable[VT], Mapping[KT, VT]],
            key: Union[Callable[[VT], VT], None] = ...,
            reverse: bool = ...) -> List[int] | List[KT]:
    ...


def argmax(indexable: Union[Iterable[VT], Mapping[KT, VT]],
           key: Callable[[VT], Any] = ...) -> int | KT:
    ...


def argmin(indexable: Union[Iterable[VT], Mapping[KT, VT]],
           key: Callable[[VT], VT] = ...) -> int | KT:
    ...


def peek(iterable: Iterable[T], default: T = ...) -> T:
    ...
