from typing import Union
from os import PathLike
from typing import Callable
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any


class Cacher:
    VERBOSE: int
    FORCE_DISABLE: bool
    dpath: Incomplete
    fname: Incomplete
    depends: Incomplete
    cfgstr: Incomplete
    verbose: Incomplete
    ext: Incomplete
    meta: Incomplete
    enabled: Incomplete
    protocol: Incomplete
    hasher: Incomplete
    log: Incomplete
    backend: Incomplete

    def __init__(self,
                 fname,
                 depends: Incomplete | None = ...,
                 dpath: Incomplete | None = ...,
                 appname: str = ...,
                 ext: str = ...,
                 meta: Incomplete | None = ...,
                 verbose: Incomplete | None = ...,
                 enabled: bool = ...,
                 log: Incomplete | None = ...,
                 hasher: str = ...,
                 protocol: int = ...,
                 cfgstr: Incomplete | None = ...,
                 backend: str = ...) -> None:
        ...

    @property
    def fpath(self):
        ...

    def get_fpath(self, cfgstr: Union[str, None] = ...) -> str | PathLike:
        ...

    def exists(self, cfgstr: Union[str, None] = ...) -> bool:
        ...

    def existing_versions(self) -> Generator[str, None, None]:
        ...

    def clear(self, cfgstr: Union[str, None] = ...) -> None:
        ...

    def tryload(self,
                cfgstr: Union[str, None] = ...,
                on_error: str = ...) -> None | object:
        ...

    def load(self, cfgstr: Union[str, None] = ...) -> object:
        ...

    def save(self, data: object, cfgstr: Union[str, None] = ...) -> None:
        ...

    def ensure(self, func: Callable, *args, **kwargs):
        ...

    def __call__(self, func: Callable):
        ...


class CacheStamp:
    cacher: Incomplete
    product: Incomplete
    hasher: Incomplete
    expires: Incomplete
    hash_prefix: Incomplete

    def __init__(self,
                 fname,
                 dpath,
                 cfgstr: Incomplete | None = ...,
                 product: Incomplete | None = ...,
                 hasher: str = ...,
                 verbose: Incomplete | None = ...,
                 enabled: bool = ...,
                 depends: Incomplete | None = ...,
                 meta: Incomplete | None = ...,
                 hash_prefix: Incomplete | None = ...,
                 expires: Incomplete | None = ...,
                 ext: str = ...) -> None:
        ...

    @property
    def fpath(self):
        ...

    def clear(self):
        ...

    def expired(self, cfgstr: Any = ..., product: Any = ...) -> bool | str:
        ...

    def renew(self,
              cfgstr: Incomplete | None = ...,
              product: Incomplete | None = ...) -> None | dict:
        ...
