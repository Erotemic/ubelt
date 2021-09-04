from typing import Tuple
from typing import Union
from typing import Callable
from typing import List
from os import PathLike
from typing import Any, TypeVar

Hasher = TypeVar("Hasher")
HASH_VERSION: int
DEFAULT_ALPHABET: Any
PY2: bool
b: Any
binary_type: Any
binary_type = bytes
DEFAULT_HASHER: Any


class _Hashers:
    algos: Any

    def __init__(self) -> None:
        ...

    def __contains__(self, key):
        ...

    def lookup(self, hasher):
        ...


class HashableExtensions:
    keyed_extensions: Any
    iterable_checks: Any

    def __init__(self) -> None:
        ...

    def register(self, hash_types: Union[type, Tuple[type]]) -> Callable:
        ...

    def add_iterable_check(self, func):
        ...

    def lookup(self, data):
        ...


class _HashTracer:
    sequence: Any

    def __init__(self) -> None:
        ...

    def update(self, bytes) -> None:
        ...


def hash_data(data: object,
              hasher: Union[str, Hasher] = ...,
              base: Union[List[str], str] = ...,
              types: bool = ...,
              hashlen: int = ...,
              convert: bool = ...,
              extensions: HashableExtensions = ...) -> str:
    ...


def hash_file(fpath: PathLike,
              blocksize: int = ...,
              stride: int = ...,
              maxbytes: Union[int, None] = ...,
              hasher: Union[str, Hasher] = ...,
              hashlen: int = ...,
              base: Union[List[str], str] = ...):
    ...
