import datetime
from typing import Callable
from typing import Type
from types import TracebackType


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
    write: Callable
    flush: Callable
    label: str
    verbose: int | None
    newline: bool
    ns: bool

    def __init__(self,
                 label: str = '',
                 verbose: int | None = None,
                 newline: bool = True,
                 ns: bool = False) -> None:
        ...

    def tic(self) -> Timer:
        ...

    def toc(self) -> float | int:
        ...

    def __enter__(self) -> Timer:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...
