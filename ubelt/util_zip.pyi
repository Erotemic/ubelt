from os import PathLike
from typing import Tuple
from typing import Type
from types import TracebackType
from ubelt.util_mixins import NiceRepr


def split_archive(fpath: str | PathLike,
                  ext: str = '.zip') -> Tuple[str, str | None]:
    ...


class zopen(NiceRepr):
    name: str | PathLike
    fpath: str | PathLike
    ext: str
    mode: str

    def __init__(self,
                 fpath: str | PathLike,
                 mode: str = 'r',
                 seekable: bool = False,
                 ext: str = '.zip') -> None:
        ...

    @property
    def zfile(self):
        ...

    def namelist(self):
        ...

    def __nice__(self):
        ...

    def __getattr__(self, key):
        ...

    def __dir__(self):
        ...

    def __del__(self) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...
