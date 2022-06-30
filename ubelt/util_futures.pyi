import concurrent
import concurrent.futures
from typing import Callable
from typing import Any
from typing import Union
from typing import List
import concurrent.futures
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any


class SerialFuture(concurrent.futures.Future):
    func: Incomplete
    args: Incomplete
    kw: Incomplete

    def __init__(self, func, *args, **kw) -> None:
        ...

    def set_result(self, result) -> None:
        ...


class SerialExecutor:
    max_workers: int

    def __enter__(self):
        ...

    def __exit__(self, ex_type, ex_value, tb) -> None:
        ...

    def submit(self, func, *args, **kw) -> concurrent.futures.Future:
        ...

    def shutdown(self) -> None:
        ...

    def map(self, fn: Callable[..., Any], *iterables,
            **kwargs) -> Generator[Any, None, None]:
        ...


class Executor:
    backend: Incomplete

    def __init__(self, mode: str = ..., max_workers: int = ...) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, ex_type, ex_value, tb):
        ...

    def submit(self, func, *args, **kw) -> concurrent.futures.Future:
        ...

    def shutdown(self):
        ...

    def map(self, fn, *iterables, **kwargs):
        ...


class JobPool:
    executor: Incomplete
    jobs: Incomplete

    def __init__(self, mode: str = ..., max_workers: int = ...) -> None:
        ...

    def __len__(self):
        ...

    def submit(self, func: Callable[..., Any], *args,
               **kwargs) -> concurrent.futures.Future:
        ...

    def shutdown(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, a, b, c) -> None:
        ...

    def as_completed(
        self,
        timeout: Union[float, None] = None,
        desc: Union[str, None] = None,
        progkw: Union[dict, None] = None
    ) -> Generator[concurrent.futures.Future, None, None]:
        ...

    def join(self, **kwargs) -> List[Any]:
        ...

    def __iter__(self):
        ...
