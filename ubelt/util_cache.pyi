from typing import Union
from typing import Callable
from typing import Sequence
from os import PathLike
from collections.abc import Generator
from typing import Any


class Cacher:
    VERBOSE: int
    FORCE_DISABLE: bool
    dpath: Any
    fname: Any
    depends: Any
    cfgstr: Any
    verbose: Any
    ext: Any
    meta: Any
    enabled: Any
    protocol: Any
    hasher: Any
    log: Any
    backend: Any

    def __init__(self,
                 fname,
                 depends: Any | None = ...,
                 dpath: Any | None = ...,
                 appname: str = ...,
                 ext: str = ...,
                 meta: Any | None = ...,
                 verbose: Any | None = ...,
                 enabled: bool = ...,
                 log: Any | None = ...,
                 hasher: str = ...,
                 protocol: int = ...,
                 cfgstr: Any | None = ...,
                 backend: str = ...) -> None:
        ...

    def get_fpath(self, cfgstr: Union[str, None] = ...):
        ...

    def exists(self, cfgstr: Union[str, None] = ...):
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
    cacher: Any
    product: Any
    hasher: Any
    expires: Any
    hash_prefix: Any

    def __init__(self,
                 fname,
                 dpath,
                 cfgstr: Any | None = ...,
                 product: Any | None = ...,
                 hasher: str = ...,
                 verbose: Any | None = ...,
                 enabled: bool = ...,
                 depends: Any | None = ...,
                 meta: Any | None = ...,
                 hash_prefix: Any | None = ...,
                 expires: Any | None = ...,
                 ext: str = ...) -> None:
        ...

    def expired(
        self,
        cfgstr: Union[str, None] = ...,
        product: Union[str, PathLike, Sequence[Union[str, PathLike]],
                       None] = ...
    ) -> bool | str:
        ...

    def renew(self,
              cfgstr: Any | None = ...,
              product: Any | None = ...) -> dict:
        ...
