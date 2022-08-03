from typing import Union
from typing import Mapping
from typing import Sequence
from typing import Iterable
from typing import Any
from typing import Callable
from typing import Iterator
from typing import List
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any, TypeVar

VT = TypeVar("VT")
KT = TypeVar("KT")
T = TypeVar("T")


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


def iterable(obj: object, strok: bool = False) -> bool:
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
           key: Callable[[T], Any] = None) -> Generator[T, None, None]:
    ...


def argunique(items: Sequence[VT],
              key: Callable[[VT], Any] = None) -> Iterator[int]:
    ...


def unique_flags(items: Sequence[VT],
                 key: Union[Callable[[VT], Any], None] = None) -> List[bool]:
    ...


def boolmask(indices: List[int], maxval: int = None) -> List[bool]:
    ...


def iter_window(iterable: Iterable[T],
                size: int = 2,
                step: int = 1,
                wrap: bool = False) -> Iterable[T]:
    ...


def allsame(iterable: Iterable[T], eq: Callable[[T, T], bool] = ...) -> bool:
    ...


def argsort(indexable: Union[Iterable[VT], Mapping[KT, VT]],
            key: Union[Callable[[VT], VT], None] = None,
            reverse: bool = False) -> List[int] | List[KT]:
    ...


def argmax(indexable: Union[Iterable[VT], Mapping[KT, VT]],
           key: Callable[[VT], Any] = None) -> int | KT:
    ...


def argmin(indexable: Union[Iterable[VT], Mapping[KT, VT]],
           key: Callable[[VT], VT] = None) -> int | KT:
    ...


def peek(iterable: Iterable[T], default: T = ...) -> T:
    ...
