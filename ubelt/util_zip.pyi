from typing import Any
from ubelt.util_mixins import NiceRepr


def split_archive(fpath, ext: str = ...):
    ...


class zopen(NiceRepr):
    fpath: Any
    ext: Any
    name: Any
    mode: Any

    def __init__(self,
                 fpath,
                 mode: str = ...,
                 seekable: bool = ...,
                 ext: str = ...) -> None:
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

    def __exit__(self, *args) -> None:
        ...
