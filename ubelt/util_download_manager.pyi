from os import PathLike
import concurrent
import concurrent.futures
from typing import Iterable


class DownloadManager:
    download_root: str | PathLike
    cache: bool

    def __init__(self,
                 download_root: str | PathLike | None = None,
                 mode: str = 'thread',
                 max_workers: int | None = None,
                 cache: bool = True) -> None:
        ...

    def submit(self,
               url: str | PathLike,
               dst: str | None = None,
               hash_prefix: str | None = None,
               hasher: str = 'sha256') -> concurrent.futures.Future:
        ...

    def as_completed(self,
                     prog: None | bool | type = None,
                     desc: str | None = None,
                     verbose: int = 1):
        ...

    def shutdown(self) -> None:
        ...

    def __iter__(self) -> Iterable:
        ...

    def __len__(self) -> int:
        ...
