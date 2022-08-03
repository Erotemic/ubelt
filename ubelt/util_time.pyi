from typing import Union
import datetime
from _typeshed import Incomplete


def timestamp(datetime: Union[datetime.datetime, datetime.date, None] = None,
              precision: int = 0,
              default_timezone: Union[str, datetime.timezone] = 'local',
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

    def __init__(self,
                 label: str = ...,
                 verbose: Incomplete | None = ...,
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
