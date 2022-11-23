from typing import Union
from os import PathLike
from typing import Tuple
from typing import List
from typing import Callable
from _typeshed import Incomplete
from collections.abc import Generator


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
    dpath: Incomplete

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

    @classmethod
    def appdir(cls,
               appname: Union[str, None] = ...,
               *args,
               type: str = ...) -> 'Path':
        ...

    def augment(self,
                prefix: str = ...,
                stemsuffix: str = ...,
                ext: Union[str, None] = ...,
                stem: Union[str, None] = ...,
                dpath: Union[str, PathLike, None] = ...,
                tail: Union[str, None] = ...,
                relative: Union[str, PathLike, None] = ...,
                multidot: bool = ...,
                suffix: str = ...) -> 'Path':
        ...

    def delete(self) -> 'Path':
        ...

    def ensuredir(self, mode: int = ...) -> 'Path':
        ...

    def mkdir(self,
              mode: int = ...,
              parents: bool = ...,
              exist_ok: bool = ...) -> 'Path':
        ...

    def expand(self) -> 'Path':
        ...

    def expandvars(self) -> 'Path':
        ...

    def ls(self) -> List[Path]:
        ...

    def shrinkuser(self, home: str = ...) -> 'Path':
        ...

    def touch(self, mode: int = ..., exist_ok: bool = ...) -> 'Path':
        ...

    def walk(
        self,
        topdown: bool = ...,
        onerror: Callable[[OSError], None] = ...,
        followlinks: bool = ...
    ) -> Generator[Tuple['Path', List[str], List[str]], None, None]:
        ...

    def __add__(self, other) -> str:
        ...

    def __radd__(self, other) -> str:
        ...

    def endswith(self, suffix: Union[str, Tuple[str, ...]], *args) -> bool:
        ...

    def startswith(self, prefix: Union[str, Tuple[str, ...]], *args) -> bool:
        ...

    def copy(self,
             dst: Union[str, PathLike],
             follow_file_symlinks: bool = ...,
             follow_dir_symlinks: bool = ...,
             meta: Union[str, None] = ...,
             overwrite: bool = ...) -> 'Path':
        ...

    def move(self,
             dst: Union[str, PathLike],
             follow_file_symlinks: bool = ...,
             follow_dir_symlinks: bool = ...,
             meta: Union[str, None] = ...) -> 'Path':
        ...
