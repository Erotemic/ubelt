from typing import Callable
from typing import Tuple
from typing import Dict
from typing import Type
from types import TracebackType
import concurrent
import concurrent.futures
from concurrent.futures import Future
from typing import Any
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from typing import List
from collections.abc import Generator


class SerialFuture(concurrent.futures.Future):
    func: Callable
    args: Tuple
    kw: Dict

    def __init__(self, func, *args, **kw) -> None:
        ...

    def set_result(self, result) -> None:
        ...


class SerialExecutor:
    max_workers: int

    def __enter__(self):
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...

    def submit(self, func, *args, **kw) -> concurrent.futures.Future:
        ...

    def shutdown(self) -> None:
        ...

    def map(self, fn: Callable[..., Any], *iterables,
            **kwargs) -> Generator[Any, None, None]:
        ...


class Executor:
    backend: SerialExecutor | ThreadPoolExecutor | ProcessPoolExecutor

    def __init__(self, mode: str = 'thread', max_workers: int = 0) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...

    def submit(self, func, *args, **kw) -> concurrent.futures.Future:
        ...

    def shutdown(self):
        ...

    def map(self, fn, *iterables, **kwargs):
        ...


class JobPool:
    executor: Executor
    jobs: List[Future]
    transient: bool

    def __init__(self,
                 mode: str = 'thread',
                 max_workers: int = 0,
                 transient: bool = False) -> None:
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

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...

    def as_completed(
        self,
        timeout: float | None = None,
        desc: str | None = None,
        progkw: dict | None = None
    ) -> Generator[concurrent.futures.Future, None, None]:
        ...

    def join(self, **kwargs) -> List[Any]:
        ...

    def __iter__(self) -> concurrent.futures.Future:
        ...
