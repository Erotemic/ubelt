import datetime
from typing import Union
from _typeshed import Incomplete


def timestamp(datetime: Union[datetime.datetime, datetime.date, None] = ...,
              precision: int = ...,
              default_timezone: Union[str, datetime.timezone] = ...,
              allow_dateutil: bool = ...) -> str:
    ...


def timeparse(stamp: str,
              default_timezone: str = ...,
              allow_dateutil: bool = ...) -> datetime.datetime:
    ...


class Timer:
    label: Incomplete
    verbose: Incomplete
    newline: Incomplete
    tstart: int
    elapsed: int
    write: Incomplete
    flush: Incomplete
    ns: Incomplete

    def __init__(self,
                 label: str = ...,
                 verbose: Incomplete | None = ...,
                 newline: bool = ...,
                 ns: bool = ...) -> None:
        ...

    def tic(self):
        ...

    def toc(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, ex_type, ex_value, trace):
        ...
