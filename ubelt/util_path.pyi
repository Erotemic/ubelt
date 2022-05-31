from typing import Union
from os import PathLike
from typing import Tuple
from typing import Callable
from collections.abc import Generator
from typing import Any


def augpath(path: Union[str, PathLike],
            suffix: str = ...,
            prefix: str = ...,
            ext: Union[str, None] = ...,
            tail: Union[str, None] = ...,
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


class Path:

    def touch(self, mode: int = ..., exist_ok: bool = ...) -> 'Path':
        ...

    def ensuredir(self, mode: int = ...) -> 'Path':
        ...

    def expandvars(self) -> 'Path':
        ...

    def expand(self) -> 'Path':
        ...

    def shrinkuser(self, home: str = ...) -> 'Path':
        ...

    def augment(self,
                suffix: str = ...,
                prefix: str = ...,
                ext: Union[str, None] = ...,
                stem: Union[str, None] = ...,
                dpath: Union[str, PathLike, None] = ...,
                tail: Union[str, None] = ...,
                relative: Union[str, PathLike, None] = ...,
                multidot: bool = ...) -> 'Path':
        ...

    def delete(self) -> 'Path':
        ...

    @classmethod
    def appdir(cls, appname: str, *args, type: str = ...) -> 'Path':
        ...

    def ls(self):
        ...

    def walk(
        self,
        topdown: bool = ...,
        onerror: Callable[[OSError], None] = ...,
        followlinks: bool = ...
    ) -> Generator[Tuple['Path', str, str], None, None]:
        ...
