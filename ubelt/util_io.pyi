from typing import Union
from os import PathLike
import io


def writeto(fpath: Union[str, PathLike],
            to_write: str,
            aslines: bool = ...,
            verbose: bool = ...) -> None:
    ...


def readfrom(fpath: Union[str, PathLike],
             aslines: bool = ...,
             errors: str = ...,
             verbose: bool = ...) -> str:
    ...


def touch(fpath: Union[str, PathLike],
          mode: int = ...,
          dir_fd: io.IOBase = ...,
          verbose: int = ...,
          **kwargs) -> str:
    ...


def delete(path: Union[str, PathLike], verbose: bool = ...) -> None:
    ...
