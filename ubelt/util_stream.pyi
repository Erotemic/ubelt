import io
from typing import List
from typing import Type
from types import TracebackType
from _typeshed import Incomplete


class TeeStringIO(io.StringIO):
    redirect: io.IOBase | None
    buffer: Incomplete

    def __init__(self, redirect: io.IOBase | None = None) -> None:
        ...

    def isatty(self):
        ...

    def fileno(self):
        ...

    @property
    def encoding(self):
        ...

    def write(self, msg):
        ...

    def flush(self):
        ...


class CaptureStream:
    ...


class CaptureStdout(CaptureStream):
    text: str | None
    parts: List[str]
    cap_stdout: None | TeeStringIO
    orig_stdout: io.TextIOBase
    started: bool
    enabled: bool
    suppress: bool

    def __init__(self, suppress: bool = True, enabled: bool = True) -> None:
        ...

    def log_part(self) -> None:
        ...

    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

    def __enter__(self):
        ...

    def __del__(self) -> None:
        ...

    def close(self) -> None:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...
