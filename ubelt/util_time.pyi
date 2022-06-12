from typing import Union
import datetime
from typing import Any


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
