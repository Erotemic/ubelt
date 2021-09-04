from typing import Tuple
from typing import Union
from typing import Callable
from typing import Any

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


def hash_data(data,
              hasher=...,
              base=...,
              types: bool = ...,
              hashlen=...,
              convert: bool = ...,
              extensions: Any | None = ...):
    ...


def hash_file(fpath,
              blocksize: int = ...,
              stride: int = ...,
              maxbytes: Any | None = ...,
              hasher=...,
              hashlen=...,
              base=...):
    ...
