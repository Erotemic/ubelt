from typing import Iterable
from typing import List
import typing
from typing import Callable
from _typeshed import Incomplete
from typing import NamedTuple

default_timer: Incomplete


class Measurement(NamedTuple):
    idx: Incomplete
    time: Incomplete


CLEAR_BEFORE: str
AT_END: str


class _TQDMCompat:

    @classmethod
    def write(cls,
              s,
              file: Incomplete | None = ...,
              end: str = ...,
              nolock: bool = ...) -> None:
        ...

    desc: Incomplete

    def set_description(self,
                        desc: Incomplete | None = ...,
                        refresh: bool = ...) -> None:
        ...

    def set_description_str(self,
                            desc: Incomplete | None = ...,
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
    def pos(self):
        ...

    @classmethod
    def set_lock(cls, lock) -> None:
        ...

    @classmethod
    def get_lock(cls) -> None:
        ...

    def set_postfix(self,
                    ordered_dict: Incomplete | None = ...,
                    refresh: bool = ...,
                    **kwargs) -> None:
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
    iterable: List | Iterable
    desc: str
    total: int
    freq: int
    eta_window: int
    clearline: bool
    adjust: bool
    time_thresh: float
    show_percent: bool
    show_times: bool
    show_rate: bool
    show_eta: bool
    show_wall: bool
    initial: int
    stream: typing.IO
    timer: Callable
    enabled: bool
    chunksize: int | None
    rel_adjust_limit: float
    verbose: int
    homogeneous: bool | str
    show_total: Incomplete
    extra: str
    started: bool
    finished: bool

    def __init__(self,
                 iterable: Incomplete | None = ...,
                 desc: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 freq: int = ...,
                 initial: int = ...,
                 eta_window: int = ...,
                 clearline: bool = ...,
                 adjust: bool = ...,
                 time_thresh: float = ...,
                 show_percent: bool = ...,
                 show_times: bool = ...,
                 show_rate: bool = ...,
                 show_eta: bool = ...,
                 show_total: bool = ...,
                 show_wall: bool = ...,
                 enabled: bool = ...,
                 verbose: Incomplete | None = ...,
                 stream: Incomplete | None = ...,
                 chunksize: Incomplete | None = ...,
                 rel_adjust_limit: float = ...,
                 homogeneous: str = ...,
                 timer: Incomplete | None = ...,
                 **kwargs) -> None:
        ...

    def __call__(self, iterable):
        ...

    def __enter__(self):
        ...

    def __exit__(self, type_, value, trace):
        ...

    def __iter__(self):
        ...

    def set_extra(self, extra: str | Callable) -> None:
        ...

    def begin(self) -> ProgIter:
        ...

    def end(self) -> None:
        ...

    def step(self, inc: int = 1, force: bool = False) -> None:
        ...

    def format_message(self):
        ...

    def format_message_parts(self):
        ...

    def ensure_newline(self) -> None:
        ...

    def display_message(self) -> None:
        ...
