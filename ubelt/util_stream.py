"""
Functions for capturing and redirecting IO streams with optional
tee-functionality.

The :class:`CaptureStdout` captures all text sent to stdout and optionally
prevents it from actually reaching stdout.

The :class:`TeeStringIO` does the same thing but for arbitrary streams. It is
how the former is implemented.

"""
from __future__ import annotations
import sys
import io
import typing

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import TextIO, Type

__all__ = [
    'TeeStringIO',
    'CaptureStdout',
    'CaptureStderr',
    'CaptureStream',
]


class TeeStringIO(io.StringIO):
    """
    An IO object that writes to itself and another IO stream.

    Attributes:
        redirect (io.IOBase | None): The other stream to write to.

    Example:
        >>> import ubelt as ub
        >>> import io
        >>> redirect = io.StringIO()
        >>> self = ub.TeeStringIO(redirect)
        >>> self.write('spam')
        >>> assert self.getvalue() == 'spam'
        >>> assert redirect.getvalue() == 'spam'
    """
    def __init__(self, redirect: io.IOBase | None = None) -> None:
        """
        Args:
            redirect (io.IOBase): The other stream to write to.
        """
        self.redirect = redirect  # type: io.IOBase
        super().__init__()

        # Logic taken from prompt_toolkit/output/vt100.py version 3.0.5 in
        # flush I don't have a full understanding of what the buffer
        # attribute is supposed to be capturing here, but this seems to
        # allow us to embed in IPython while still capturing and Teeing
        # stdout.
        if redirect is not None:
            self.buffer = getattr(redirect, 'buffer', redirect)
        else:
            self.buffer = None

        # Note: mypy doesn't like this type
        # buffer (io.BufferedIOBase | io.IOBase | None): the redirected buffer attribute

    def isatty(self) -> bool:  # nocover
        """
        Returns true of the redirect is a terminal.

        Note:
            Needed for ``IPython.embed`` to work properly when this class is
            used to override stdout / stderr.

        SeeAlso:
            :meth:`io.IOBase.isatty`

        Returns:
            bool
        """
        return (self.redirect is not None and
                hasattr(self.redirect, 'isatty') and self.redirect.isatty())

    def fileno(self) -> int:
        """
        Returns underlying file descriptor of the redirected IOBase object
        if one exists.

        Returns:
            int : the integer corresponding to the file descriptor

        SeeAlso:
            :meth:`io.IOBase.fileno`

        Example:
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('ubelt/tests/util_stream').ensuredir()
            >>> fpath = dpath / 'fileno-test.txt'
            >>> with open(fpath, 'w') as file:
            >>>     self = ub.TeeStringIO(file)
            >>>     descriptor = self.fileno()
            >>>     print(f'descriptor={descriptor}')
            >>>     assert isinstance(descriptor, int)

        Example:
            >>> # Test errors
            >>> # Not sure the best way to test, this func is important for
            >>> # capturing stdout when ipython embedding
            >>> import io
            >>> import pytest
            >>> import ubelt as ub
            >>> with pytest.raises(io.UnsupportedOperation):
            >>>     ub.TeeStringIO(redirect=io.StringIO()).fileno()
            >>> with pytest.raises(io.UnsupportedOperation):
            >>>     ub.TeeStringIO(None).fileno()
        """
        if self.redirect is not None:
            return self.redirect.fileno()
        else:
            return super().fileno()

    @property
    def encoding(self):
        """
        Gets the encoding of the `redirect` IO object

        FIXME:
            Mypy complains that this violates the Liskov substitution principle
            because the return type can be str or None, whereas the parent
            class always returns a None. In the future we may raise an exception
            instead of returning None.

        SeeAlso:
            :py:obj:`io.TextIOBase.encoding`

        Example:
            >>> import ubelt as ub
            >>> redirect = io.StringIO()
            >>> assert ub.TeeStringIO(redirect).encoding is None
            >>> assert ub.TeeStringIO(None).encoding is None
            >>> assert ub.TeeStringIO(sys.stdout).encoding is sys.stdout.encoding
            >>> redirect = io.TextIOWrapper(io.StringIO())
            >>> assert ub.TeeStringIO(redirect).encoding is redirect.encoding
        """
        # mypy correctly complains if we include the return type, but we need
        # to keep this buggy behavior for legacy reasons.
        # Returns:
        #     None | str
        if self.redirect is not None:
            return self.redirect.encoding
        else:
            return super().encoding

    @encoding.setter
    def encoding(self, value):
        # Adding a setter to make mypy happy
        raise AttributeError('encoding is read-only on TeeStringIO')

    def write(self, msg: str):
        """
        Write to this and the redirected stream

        Args:
            msg (str): the data to write

        SeeAlso:
            :meth:`io.TextIOBase.write`

        Example:
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('ubelt/tests/util_stream').ensuredir()
            >>> fpath = dpath / 'write-test.txt'
            >>> with open(fpath, 'w') as file:
            >>>     self = ub.TeeStringIO(file)
            >>>     n = self.write('hello world')
            >>>     assert n == 11
            >>> assert self.getvalue() == 'hello world'
            >>> assert fpath.read_text() == 'hello world'
        """
        if self.redirect is not None:
            self.redirect.write(msg)
        return super().write(msg)

    def flush(self):
        """
        Flush to this and the redirected stream

        SeeAlso:
            :meth:`io.IOBase.flush`
        """
        if self.redirect is not None:
            self.redirect.flush()
        return super().flush()


class CaptureStream:
    """
    Generic context manager for capturing a global text stream (stdout/stderr),
    with optional tee/suppress behavior and incremental reads.

    Subclasses must override ``_get_stream()`` and ``_set_stream(value)`` to
    read/write the process-global stream they manage.

    Attributes:
        text (str | None): most recent captured chunk from :meth:`log_part`.
        parts (list[str]): all captured chunks appended by :meth:`log_part`.
        cap_stream (None | TeeStringIO): proxy stream used while capturing.
        orig_stream (TextIO | None): original global stream restored on stop.
        suppress (bool): if True, do not tee to the original stream while capturing.
        enabled (bool): if False, acts as a no-op context manager.
        started (bool): True while the capture is active.
    """
    # ----- hooks required by subclasses -----
    def _get_stream(self) -> TextIO:  # pragma: no cover - abstract-ish
        raise NotImplementedError

    def _set_stream(self, value: TextIO) -> None:  # pragma: no cover
        raise NotImplementedError

    # ----- implementation -----
    def __init__(self, suppress: bool = True, enabled: bool = True) -> None:
        self.text: str | None = None
        self._pos: int = 0
        self.parts: list[str] = []
        self.started: bool = False
        self.enabled: bool = enabled
        self.suppress: bool = suppress
        self.cap_stream: TeeStringIO | None = None
        self.orig_stream: TextIO | None = None

    def _make_proxy(self) -> TeeStringIO:
        """
        Create a fresh `TeeStringIO` proxy with appropriate redirect target
        depending on `suppress`. Called at start of each capture.
        """
        redirect = None if self.suppress else self._get_stream()
        return TeeStringIO(redirect)

    def log_part(self) -> None:
        """Log what has been captured since the last call to :meth:`log_part`."""
        if self.cap_stream is None:  # nocover
            return
        self.cap_stream.seek(self._pos)
        text = self.cap_stream.read()
        self._pos = self.cap_stream.tell()
        self.parts.append(text)
        self.text = text

    def start(self) -> None:
        """
        Begin capturing. Swaps the global stream to our `TeeStringIO`.
        """
        if not self.enabled or self.started:  # pragma: nobranch
            return
        self.text = ''
        self.started = True
        self.orig_stream = self._get_stream()
        self.cap_stream = self._make_proxy()
        self._set_stream(self.cap_stream)

    def stop(self) -> None:
        """
        Stop capturing. Restores the original global stream.
        """
        if not self.enabled or not self.started:  # nocover
            return
        self.started = False
        if self.orig_stream is not None:  # pragma: nobranch
            self._set_stream(self.orig_stream)
        # keep cap_stream alive for reading until close/__exit__

    def close(self) -> None:
        """Close and drop the proxy buffer to release memory."""
        if self.cap_stream is not None:  # pragma: nobranch
            try:
                self.cap_stream.close()
            finally:
                self.cap_stream = None

    def __enter__(self) -> CaptureStream:
        self.start()
        return self

    def __exit__(
        self,
        ex_type: Type[BaseException] | None,
        ex_value: BaseException | None,
        ex_traceback: TracebackType | None,
    ) -> bool | None:
        """
        On exit, append the final part, stop, and close the proxy.

        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        if self.enabled:
            try:
                self.log_part()
            finally:
                self.stop()
                self.close()
        if ex_traceback is not None:
            return False  # propagate exception

    def __del__(self):  # nocover
        # Be robust during interpreter shutdown
        try:
            if getattr(self, 'started', False):
                self.stop()
            if getattr(self, 'cap_stream', None) is not None:
                self.close()
        except Exception:
            pass


class CaptureStdout(CaptureStream):
    r"""
    Context manager that captures stdout and stores it in an internal stream.

    Depending on the value of ``suppress``, the user can control if stdout is
    printed (i.e. if stdout is tee-ed or suppressed) while it is being captured.

    SeeAlso:
        :func:`contextlib.redirect_stdout` - similar, but does not have the
            ability to print stdout while it is being captured.

    Attributes:
        text (str | None): internal storage for the most recent part

        parts (List[str]): internal storage for all parts

        cap_stdout (None | TeeStringIO): internal stream proxy

        orig_stdout (io.TextIOBase):
            internal pointer to the original stdout stream

    Example:
        >>> import ubelt as ub
        >>> self = ub.CaptureStdout(suppress=True)
        >>> print('dont capture the table flip (╯°□°）╯︵ ┻━┻')
        >>> with self:
        ...     text = 'capture the heart ♥'
        ...     print(text)
        >>> print('dont capture look of disapproval ಠ_ಠ')
        >>> assert isinstance(self.text, str)
        >>> assert self.text == text + '\n', 'failed capture text'

    Example:
        >>> import ubelt as ub
        >>> self = ub.CaptureStdout(suppress=False)
        >>> with self:
        ...     print('I am captured and printed in stdout')
        >>> assert self.text.strip() == 'I am captured and printed in stdout'

    Example:
        >>> import ubelt as ub
        >>> self = ub.CaptureStdout(suppress=True, enabled=False)
        >>> with self:
        ...     print('dont capture')
        >>> assert self.text is None
    """
    # ---- required hooks for CaptureStream ----
    def _get_stream(self) -> TextIO:
        return sys.stdout

    def _set_stream(self, value: TextIO) -> None:
        sys.stdout = value

    # Backward-compat aliases expected by existing code/tests

    @property
    def cap_stdout(self) -> TeeStringIO | None:
        """Backward-compatibility alias for cap_stream."""
        return self.cap_stream

    @property
    def orig_stdout(self) -> TextIO | None:
        """Backward-compatibility alias for orig_stream."""
        return self.orig_stream


class CaptureStderr(CaptureStream):
    r"""
    Context manager that captures **stderr** and stores it in an internal stream.

    Behavior mirrors :class:`CaptureStdout`, but for ``sys.stderr``.

    Example:
        >>> import sys
        >>> self = CaptureStderr(suppress=True)
        >>> with self:
        ...     print('to stdout (not captured)')
        ...     print('to stderr (captured)', file=sys.stderr)
        >>> assert 'to stderr (captured)' in (self.text or '')
    """
    def _get_stream(self) -> TextIO:
        return sys.stderr

    def _set_stream(self, value: TextIO) -> None:
        sys.stderr = value
