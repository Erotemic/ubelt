from os import PathLike
from typing import Tuple
from typing import Type
from types import TracebackType
from typing import List
from typing import Callable
from collections.abc import Generator


def augpath(path: str | PathLike,
            suffix: str = '',
            prefix: str = '',
            ext: str | None = None,
            tail: str | None = '',
            base: str | None = None,
            dpath: str | PathLike | None = None,
            relative: str | PathLike | None = None,
            multidot: bool = False) -> str:
    ...


def userhome(username: str | None = None) -> str:
    ...


def shrinkuser(path: str | PathLike, home: str = '~') -> str:
    ...


def expandpath(path: str | PathLike) -> str:
    ...


def ensuredir(dpath: str | PathLike | Tuple[str | PathLike],
              mode: int = 1023,
              verbose: int = 0,
              recreate: bool = False) -> str:
    ...


class ChDir:

    def __init__(self, dpath: str | PathLike | None) -> None:
        ...

    def __enter__(self) -> ChDir:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...


class TempDir:
    dpath: str | None

    def __init__(self) -> None:
        ...

    def __del__(self) -> None:
        ...

    def ensure(self) -> str:
        ...

    def cleanup(self) -> None:
        ...

    def start(self) -> TempDir:
        ...

    def __enter__(self) -> TempDir:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...


class Path:

    @classmethod
    def appdir(cls,
               appname: str | None = None,
               *args,
               type: str = 'cache') -> 'Path':
        ...

    def augment(self,
                prefix: str = '',
                stemsuffix: str = '',
                ext: str | None = None,
                stem: str | None = None,
                dpath: str | PathLike | None = None,
                tail: str | None = '',
                relative: str | PathLike | None = None,
                multidot: bool = False,
                suffix: str = ...) -> 'Path':
        ...

    def delete(self) -> 'Path':
        ...

    def ensuredir(self, mode: int = 511) -> 'Path':
        ...

    def mkdir(self,
              mode: int = 511,
              parents: bool = False,
              exist_ok: bool = False) -> 'Path':
        ...

    def expand(self) -> 'Path':
        ...

    def expandvars(self) -> 'Path':
        ...

    def ls(self, pattern: None | str = None) -> List['Path']:
        ...

    def shrinkuser(self, home: str = '~') -> 'Path':
        ...

    def touch(self, mode: int = ..., exist_ok: bool = ...) -> 'Path':
        ...

    def walk(
        self,
        topdown: bool = True,
        onerror: Callable[[OSError], None] | None = None,
        followlinks: bool = False
    ) -> Generator[Tuple['Path', List[str], List[str]], None, None]:
        ...

    def __add__(self, other) -> str:
        ...

    def __radd__(self, other) -> str:
        ...

    def endswith(self, suffix: str | Tuple[str, ...], *args) -> bool:
        ...

    def startswith(self, prefix: str | Tuple[str, ...], *args) -> bool:
        ...

    def copy(self,
             dst: str | PathLike,
             follow_file_symlinks: bool = False,
             follow_dir_symlinks: bool = False,
             meta: str | None = 'stats',
             overwrite: bool = False) -> 'Path':
        ...

    def move(self,
             dst: str | PathLike,
             follow_file_symlinks: bool = False,
             follow_dir_symlinks: bool = False,
             meta: str | None = 'stats') -> 'Path':
        ...
