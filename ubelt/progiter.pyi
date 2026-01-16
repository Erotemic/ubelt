from typing import Iterable
from _typeshed import SupportsWrite
from typing import List
import typing
from typing import Callable
from typing import Type
from types import TracebackType
from typing import Tuple
from _typeshed import Incomplete
from typing import NamedTuple

default_timer: Callable


class Measurement(NamedTuple):
    idx: Incomplete
    time: Incomplete


CLEAR_BEFORE: str
AT_END: str


class _TQDMCompat:

    @classmethod
    def write(cls,
              s: str,
              file: None | SupportsWrite = None,
              end: str = '\n',
              nolock: bool = False) -> None:
        ...

    desc: str | None

    def set_description(self,
                        desc: str | None = None,
                        refresh: bool = ...) -> None:
        ...

    def set_description_str(self,
                            desc: str | None = None,
                            refresh: bool = ...) -> None:
        ...

    def update(self, n: int = ...) -> None:
        ...

    def close(self) -> None:
        ...

    def unpause(self) -> None:
        ...

    def moveto(self, n) -> None:
        ...

    def clear(self, nolock: bool = ...) -> None:
        ...

    def refresh(self, nolock: bool = ...) -> None:
        ...

    @property
    def pos(self) -> int:
        ...

    @classmethod
    def set_lock(cls, lock) -> None:
        ...

    @classmethod
    def get_lock(cls) -> None:
        ...

    def set_postfix_dict(self,
                         ordered_dict: None | dict = None,
                         refresh: bool = True,
                         **kwargs) -> None:
        ...

    def set_postfix(self, postfix, **kwargs) -> None:
        ...

    def set_postfix_str(self, s: str = ..., refresh: bool = ...) -> None:
        ...


class _BackwardsCompat:

    @property
    def length(self):
        ...

    @property
    def label(self):
        ...

    def start(self):
        ...

    def stop(self):
        ...


class ProgIter(_TQDMCompat, _BackwardsCompat):
    stream: typing.IO
    iterable: List | Iterable
    desc: str | None
    total: int | None
    freq: int
    initial: int
    enabled: bool
    adjust: bool
    show_percent: bool
    show_times: bool
    show_rate: bool
    show_eta: bool
    show_total: bool
    show_wall: bool
    eta_window: int
    time_thresh: float
    clearline: bool
    chunksize: int | None
    rel_adjust_limit: float
    extra: str
    started: bool
    finished: bool
    homogeneous: bool | str

    def __init__(self,
                 iterable: List | Iterable | None = None,
                 desc: str | None = None,
                 total: int | None = None,
                 freq: int = 1,
                 initial: int = 0,
                 eta_window: int = 64,
                 clearline: bool = True,
                 adjust: bool = True,
                 time_thresh: float = 2.0,
                 show_percent: bool = True,
                 show_times: bool = True,
                 show_rate: bool = True,
                 show_eta: bool = True,
                 show_total: bool = True,
                 show_wall: bool = False,
                 enabled: bool = True,
                 verbose: int | None = None,
                 stream: typing.IO | None = None,
                 chunksize: int | None = None,
                 rel_adjust_limit: float = 4.0,
                 homogeneous: bool | str = 'auto',
                 timer: Callable | None = None,
                 **kwargs) -> None:
        ...

    def __call__(self, iterable: Iterable) -> Iterable:
        ...

    def __enter__(self) -> ProgIter:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...

    def __iter__(self) -> Iterable:
        ...

    def set_extra(self, extra: str | Callable) -> None:
        ...

    def begin(self) -> ProgIter:
        ...

    def end(self) -> None:
        ...

    def step(self, inc: int = 1, force: bool = False) -> None:
        ...

    def format_message(self) -> str:
        ...

    def format_message_parts(self) -> Tuple[str, str, str]:
        ...

    def ensure_newline(self) -> None:
        ...

    def display_message(self) -> None:
        ...
