from typing import List
from os import PathLike
from typing import Callable
from typing import Any
from typing import Sequence
import datetime
import os
from collections.abc import Generator


class Cacher:
    VERBOSE: int
    FORCE_DISABLE: bool
    dpath: str | PathLike | None
    fname: str
    depends: str | List[str] | None
    cfgstr: str | None
    verbose: int
    ext: str
    meta: object | None
    enabled: bool
    protocol: int
    hasher: str
    log: Callable[[str], Any]
    backend: str

    def __init__(self,
                 fname: str,
                 depends: str | List[str] | None = None,
                 dpath: str | PathLike | None = None,
                 appname: str = 'ubelt',
                 ext: str = '.pkl',
                 meta: object | None = None,
                 verbose: int | None = None,
                 enabled: bool = True,
                 log: Callable[[str], Any] | None = None,
                 hasher: str = 'sha1',
                 protocol: int = ...,
                 cfgstr: str | None = None,
                 backend: str = 'auto') -> None:
        ...

    @property
    def fpath(self) -> os.PathLike:
        ...

    def get_fpath(self, cfgstr: str | None = None) -> str | PathLike:
        ...

    def exists(self, cfgstr: str | None = None) -> bool:
        ...

    def existing_versions(self) -> Generator[str, None, None]:
        ...

    def clear(self, cfgstr: str | None = None) -> None:
        ...

    def tryload(self,
                cfgstr: str | None = None,
                on_error: str = 'raise') -> None | object:
        ...

    def load(self, cfgstr: str | None = None) -> object:
        ...

    def save(self, data: object, cfgstr: str | None = None) -> None:
        ...

    def ensure(self, func: Callable, *args, **kwargs):
        ...

    def __call__(self, func: Callable):
        ...


class CacheStamp:
    cacher: Cacher
    product: str | PathLike | Sequence[str | PathLike] | None
    hasher: str
    expires: str | int | datetime.datetime | datetime.timedelta | None
    hash_prefix: None | str | List[str]

    def __init__(self,
                 fname: str,
                 dpath: str | PathLike | None,
                 cfgstr: str | None = None,
                 product: str | PathLike | Sequence[str | PathLike]
                 | None = None,
                 hasher: str = 'sha1',
                 verbose: bool | None = None,
                 enabled: bool = True,
                 depends: str | List[str] | None = None,
                 meta: object | None = None,
                 hash_prefix: None | str | List[str] = None,
                 expires: str | int | datetime.datetime | datetime.timedelta
                 | None = None,
                 ext: str = '.pkl') -> None:
        ...

    @property
    def fpath(self):
        ...

    def clear(self):
        ...

    def expired(self,
                cfgstr: Any | None = None,
                product: Any | None = None) -> bool | str:
        ...

    def renew(self,
              cfgstr: None | str = None,
              product: None | str | List = None) -> None | dict:
        ...
