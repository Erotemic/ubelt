from typing import Union
from os import PathLike
import concurrent.futures
from typing import Any


class DownloadManager:
    pool: Any
    download_root: Any
    cache: Any
    dl_func: Any

    def __init__(self,
                 download_root: Any | None = ...,
                 mode: str = ...,
                 max_workers: Any | None = ...,
                 cache: bool = ...) -> None:
        ...

    def submit(self,
               url: Union[str, PathLike],
               dst: Union[str, None] = ...,
               hash_prefix: Union[str, None] = ...,
               hasher: str = ...) -> concurrent.futures.Future:
        ...

    def as_completed(self,
                     prog: Any | None = ...,
                     desc: Any | None = ...,
                     verbose: int = ...):
        ...

    def shutdown(self) -> None:
        ...

    def __iter__(self):
        ...

    def __len__(self):
        ...
