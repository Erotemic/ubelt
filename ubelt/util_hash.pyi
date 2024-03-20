from typing import Dict
from typing import List
from ubelt.util_const import NoParam
from ubelt.util_const import NoParamType
from typing import Any
from typing import Callable
from typing import Tuple
from os import PathLike
from typing import Any, TypeVar

Hasher = TypeVar("Hasher")
HASH_VERSION: int
DEFAULT_ALPHABET: List[str]


def b(s: str) -> bytes:
    ...


DEFAULT_HASHER: Callable


class _Hashers:
    algos: Dict[str, object]
    aliases: Dict[str, str]

    def __init__(self) -> None:
        ...

    def available(self) -> List[str]:
        ...

    def __contains__(self, key: str) -> bool:
        ...

    def lookup(self, hasher: NoParamType | str | Any) -> Callable:
        ...


class HashableExtensions:
    iterable_checks: List[Callable]

    def __init__(self) -> None:
        ...

    def register(self, hash_types: type | Tuple[type]) -> Callable:
        ...

    def lookup(self, data: object) -> Callable:
        ...

    def add_iterable_check(self, func: Callable) -> Callable:
        ...


class _HashTracer:
    sequence: List[bytes]

    def __init__(self) -> None:
        ...

    def update(self, item: bytes) -> None:
        ...

    def hexdigest(self) -> bytes:
        ...


def hash_data(data: object,
              hasher: str | Hasher | NoParamType = NoParam,
              base: List[str] | str | NoParamType = NoParam,
              types: bool = False,
              convert: bool = False,
              extensions: HashableExtensions | None = None) -> str:
    ...


def hash_file(fpath: PathLike,
              blocksize: int = 1048576,
              stride: int = 1,
              maxbytes: int | None = None,
              hasher: str | Hasher | NoParamType = NoParam,
              base: List[str] | int | str | NoParamType = NoParam) -> str:
    ...
