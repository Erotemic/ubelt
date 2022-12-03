from typing import Union
from os import PathLike
import io


def writeto(fpath: Union[str, PathLike],
            to_write: str,
            aslines: bool = False,
            verbose: Union[int, None] = None) -> None:
    ...


def readfrom(fpath: Union[str, PathLike],
             aslines: bool = False,
             errors: str = 'replace',
             verbose: Union[int, None] = None) -> str:
    ...


def touch(fpath: Union[str, PathLike],
          mode: int = 438,
          dir_fd: Union[io.IOBase, None] = None,
          verbose: int = 0,
          **kwargs) -> str:
    ...


def delete(path: Union[str, PathLike], verbose: bool = False) -> None:
    ...
