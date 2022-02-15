from typing import Any

default_timer: Any
CLEAR_BEFORE: str
AT_END: str
CLEAR_AFTER: str


class _TQDMCompat:

    @classmethod
    def write(cls,
              s,
              file: Any | None = ...,
              end: str = ...,
              nolock: bool = ...) -> None:
        ...

    desc: Any

    def set_description(self,
                        desc: Any | None = ...,
                        refresh: bool = ...) -> None:
        ...

    def set_description_str(self,
                            desc: Any | None = ...,
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
                    ordered_dict: Any | None = ...,
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


class ProgIter(_TQDMCompat, _BackwardsCompat):
    stream: Any
    iterable: Any
    desc: Any
    total: Any
    freq: Any
    initial: Any
    enabled: Any
    adjust: Any
    show_times: Any
    show_wall: Any
    eta_window: Any
    time_thresh: Any
    clearline: Any
    chunksize: Any
    rel_adjust_limit: Any
    extra: str
    started: bool
    finished: bool

    def __init__(self,
                 iterable: Any | None = ...,
                 desc: Any | None = ...,
                 total: Any | None = ...,
                 freq: int = ...,
                 initial: int = ...,
                 eta_window: int = ...,
                 clearline: bool = ...,
                 adjust: bool = ...,
                 time_thresh: float = ...,
                 show_times: bool = ...,
                 show_wall: bool = ...,
                 enabled: bool = ...,
                 verbose: Any | None = ...,
                 stream: Any | None = ...,
                 chunksize: Any | None = ...,
                 rel_adjust_limit: float = ...,
                 **kwargs) -> None:
        ...

    def __call__(self, iterable):
        ...

    def __enter__(self):
        ...

    def __exit__(self, type, value, trace):
        ...

    def __iter__(self):
        ...

    def set_extra(self, extra) -> None:
        ...

    def step(self, inc: int = ..., force: bool = ...) -> None:
        ...

    def start(self):
        ...

    def begin(self) -> ProgIter:
        ...

    def end(self) -> None:
        ...

    def format_message(self):
        ...

    def ensure_newline(self) -> None:
        ...

    def display_message(self) -> None:
        ...
