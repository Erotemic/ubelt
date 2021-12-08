from typing import Union
from typing import Any

default_time: Any


class Timer:
    label: Any
    verbose: Any
    newline: Any
    tstart: int
    elapsed: int
    write: Any
    flush: Any

    def __init__(self,
                 label: str = ...,
                 verbose: Any | None = ...,
                 newline: bool = ...) -> None:
        ...

    def tic(self):
        ...

    def toc(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, ex_type, ex_value, trace):
        ...


class Timerit:
    num: Any
    label: Any
    bestof: Any
    unit: Any
    verbose: Any
    times: Any
    n_loops: Any
    total_time: Any
    measures: Any

    def __init__(self,
                 num: int = ...,
                 label: Any | None = ...,
                 bestof: int = ...,
                 unit: Any | None = ...,
                 verbose: Any | None = ...) -> None:
        ...

    def reset(self, label: Union[str, None] = ..., measures: bool = ...):
        ...

    def call(self, func, *args, **kwargs) -> 'Timerit':
        ...

    def __iter__(self):
        ...

    @property
    def rankings(self):
        ...

    @property
    def consistency(self):
        ...

    def min(self) -> float:
        ...

    def mean(self) -> float:
        ...

    def std(self) -> float:
        ...

    def report(self, verbose: int = ...) -> str:
        ...

    def print(self, verbose: int = ...) -> None:
        ...


class _ToggleGC:
    flag: Any
    prev: Any

    def __init__(self, flag) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, ex_type, ex_value, trace) -> None:
        ...
