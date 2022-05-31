import datetime
from typing import Union
from typing import Any


def timestamp(datetime: Union[datetime.datetime, None] = ...,
              precision: int = ...,
              method: str = ...) -> str:
    ...


def timeparse(stamp: str, allow_dateutil: bool = ...) -> datetime.datetime:
    ...


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
