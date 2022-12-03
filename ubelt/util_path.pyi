from typing import Union
from os import PathLike
from typing import Tuple
from typing import List
from typing import Callable
from _typeshed import Incomplete
from collections.abc import Generator


def augpath(path: Union[str, PathLike],
            suffix: str = '',
            prefix: str = '',
            ext: Union[str, None] = None,
            tail: Union[str, None] = '',
            base: Union[str, None] = None,
            dpath: Union[str, PathLike, None] = None,
            relative: Union[str, PathLike, None] = None,
            multidot: bool = False) -> str:
    ...


def userhome(username: Union[str, None] = None) -> str:
    ...


def shrinkuser(path: Union[str, PathLike], home: str = '~') -> str:
    ...


def expandpath(path: Union[str, PathLike]) -> str:
    ...


def ensuredir(dpath: Union[str, PathLike, Tuple[Union[str, PathLike]]],
              mode: int = 1023,
              verbose: int = 0,
              recreate: bool = False) -> str:
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
               appname: Union[str, None] = None,
               *args,
               type: str = 'cache') -> 'Path':
        ...

    def augment(self,
                prefix: str = '',
                stemsuffix: str = '',
                ext: Union[str, None] = None,
                stem: Union[str, None] = None,
                dpath: Union[str, PathLike, None] = None,
                tail: Union[str, None] = '',
                relative: Union[str, PathLike, None] = None,
                multidot: bool = False,
                suffix: str = '') -> 'Path':
        ...

    def delete(self) -> 'Path':
        ...

    def ensuredir(self, mode: int = ...) -> 'Path':
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

    def ls(self) -> List[Path]:
        ...

    def shrinkuser(self, home: str = '~') -> 'Path':
        ...

    def touch(self, mode: int = ..., exist_ok: bool = ...) -> 'Path':
        ...

    def walk(
        self,
        topdown: bool = True,
        onerror: Union[Callable[[OSError], None], None] = None,
        followlinks: bool = False
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
             follow_file_symlinks: bool = False,
             follow_dir_symlinks: bool = False,
             meta: Union[str, None] = 'stats',
             overwrite: bool = False) -> 'Path':
        ...

    def move(self,
             dst: Union[str, PathLike],
             follow_file_symlinks: bool = False,
             follow_dir_symlinks: bool = False,
             meta: Union[str, None] = 'stats') -> 'Path':
        ...
