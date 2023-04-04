from os import PathLike
import io


def writeto(fpath: str | PathLike,
            to_write: str,
            aslines: bool = False,
            verbose: int | None = None) -> None:
    ...


def readfrom(fpath: str | PathLike,
             aslines: bool = False,
             errors: str = 'replace',
             verbose: int | None = None) -> str:
    ...


def touch(fpath: str | PathLike,
          mode: int = 438,
          dir_fd: io.IOBase | None = None,
          verbose: int = 0,
          **kwargs) -> str:
    ...


def delete(path: str | PathLike, verbose: bool = False) -> None:
    ...
