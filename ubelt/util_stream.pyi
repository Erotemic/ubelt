import io
from typing import Any


class TeeStringIO(io.StringIO):
    redirect: Any
    buffer: Any

    def __init__(self, redirect: Any | None = ...) -> None:
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
    text: Any
    parts: Any
    started: bool
    cap_stdout: Any
    enabled: Any
    suppress: Any
    orig_stdout: Any

    def __init__(self, suppress: bool = ..., enabled: bool = ...) -> None:
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

    def __exit__(self, type_, value, trace):
        ...
