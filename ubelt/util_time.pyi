import datetime
from typing import Type
from types import TracebackType
from _typeshed import Incomplete


def timestamp(datetime: datetime.datetime | datetime.date | None = None,
              precision: int = 0,
              default_timezone: str | datetime.timezone = 'local',
              allow_dateutil: bool = True) -> str:
    ...


def timeparse(stamp: str,
              default_timezone: str = 'local',
              allow_dateutil: bool = True) -> datetime.datetime:
    ...


class Timer:
    elapsed: float
    tstart: float
    label: Incomplete
    verbose: Incomplete
    newline: Incomplete
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

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...
