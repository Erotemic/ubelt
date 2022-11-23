from typing import Union
from os import PathLike
import concurrent.futures
from _typeshed import Incomplete


class DownloadManager:
    pool: Incomplete
    download_root: Incomplete
    cache: Incomplete
    dl_func: Incomplete

    def __init__(self,
                 download_root: Incomplete | None = ...,
                 mode: str = ...,
                 max_workers: Incomplete | None = ...,
                 cache: bool = ...) -> None:
        ...

    def submit(self,
               url: Union[str, PathLike],
               dst: Union[str, None] = ...,
               hash_prefix: Union[str, None] = ...,
               hasher: str = ...) -> concurrent.futures.Future:
        ...

    def as_completed(self,
                     prog: Incomplete | None = ...,
                     desc: Incomplete | None = ...,
                     verbose: int = ...):
        ...

    def shutdown(self) -> None:
        ...

    def __iter__(self):
        ...

    def __len__(self):
        ...
