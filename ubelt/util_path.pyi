from typing import Union
from os import PathLike
from typing import Tuple
from typing import Any


def augpath(path: Union[str, PathLike],
            suffix: str = ...,
            prefix: str = ...,
            ext: Union[str, None] = ...,
            base: Union[str, None] = ...,
            dpath: Union[str, PathLike, None] = ...,
            relative: Union[str, PathLike, None] = ...,
            multidot: bool = ...) -> str:
    ...


def userhome(username: Union[str, None] = ...) -> str:
    ...


def shrinkuser(path: Union[str, PathLike], home: str = ...) -> str:
    ...


def expandpath(path: Union[str, PathLike]) -> str:
    ...


def ensuredir(dpath: Union[str, PathLike, Tuple[Union[str, PathLike]]],
              mode: int = ...,
              verbose: int = ...,
              recreate: bool = ...) -> str:
    ...


class TempDir:
    dpath: Any

    def __init__(self) -> None:
        ...

    def __del__(self) -> None:
        ...

    def ensure(self):
        ...

    def cleanup(self) -> None:
        ...

    def start(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, type_, value, trace) -> None:
        ...