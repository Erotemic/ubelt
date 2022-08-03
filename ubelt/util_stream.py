"""
Functions for capturing and redirecting IO streams.

The :class:`CaptureStdout` captures all text sent to stdout and optionally
prevents it from actually reaching stdout.

The :class:`TeeStringIO` does the same thing but for arbitrary streams. It is
how the former is implemented.

"""
import sys
import io

__all__ = [
    'TeeStringIO',
    'CaptureStdout',
    'CaptureStream',
]


class TeeStringIO(io.StringIO):
    """
    An IO object that writes to itself and another IO stream.

    Attributes:
        redirect (io.IOBase): The other stream to write to.

    Example:
        >>> import ubelt as ub
        >>> redirect = io.StringIO()
        >>> self = ub.TeeStringIO(redirect)
    """
    def __init__(self, redirect=None):
        self.redirect = redirect  # type: io.IOBase
        super().__init__()

        # Logic taken from prompt_toolkit/output/vt100.py version 3.0.5 in
        # flush I don't have a full understanding of what the buffer
        # attribute is supposed to be capturing here, but this seems to
        # allow us to embed in IPython while still capturing and Teeing
        # stdout
        if hasattr(redirect, 'buffer'):
            self.buffer = redirect.buffer  # Py3.
        else:
            self.buffer = redirect

    def isatty(self):  # nocover
        """
        Returns true of the redirect is a terminal.

        Note:
            Needed for ``IPython.embed`` to work properly when this class is
            used to override stdout / stderr.
        """
        return (self.redirect is not None and
                hasattr(self.redirect, 'isatty') and self.redirect.isatty())

    def fileno(self):
        """
        Returns underlying file descriptor of the redirected IOBase object
        if one exists.

        Example:
            >>> # Not sure the best way to test, this func is important for
            >>> # capturing stdout when ipython embedding
            >>> import pytest
            >>> with pytest.raises(io.UnsupportedOperation):
            >>>     TeeStringIO(redirect=io.StringIO()).fileno()
            >>> with pytest.raises(io.UnsupportedOperation):
            >>>     TeeStringIO(None).fileno()
        """
        if self.redirect is not None:
            return self.redirect.fileno()
        else:
            return super().fileno()

    @property
    def encoding(self):
        """
        Gets the encoding of the `redirect` IO object

        Example:
            >>> import ubelt as ub
            >>> redirect = io.StringIO()
            >>> assert ub.TeeStringIO(redirect).encoding is None
            >>> assert ub.TeeStringIO(None).encoding is None
            >>> assert ub.TeeStringIO(sys.stdout).encoding is sys.stdout.encoding
            >>> redirect = io.TextIOWrapper(io.StringIO())
            >>> assert ub.TeeStringIO(redirect).encoding is redirect.encoding
        """
        if self.redirect is not None:
            return self.redirect.encoding
        else:
            return super().encoding

    def write(self, msg):
        """
        Write to this and the redirected stream
        """
        if self.redirect is not None:
            self.redirect.write(msg)
        return super().write(msg)

    def flush(self):  # nocover
        """
        Flush to this and the redirected stream
        """
        if self.redirect is not None:
            self.redirect.flush()
        return super().flush()


class CaptureStream(object):
    """
    Generic class for capturing streaming output from stdout or stderr
    """


class CaptureStdout(CaptureStream):
    r"""
    Context manager that captures stdout and stores it in an internal stream

    Args:
        suppress (bool, default=True):
            if True, stdout is not printed while captured
        enabled (bool, default=True):
            does nothing if this is False
        **kwargs : used for backwards compatibility with misspelled
            deprecated params.

    SeeAlso:
        :func:`contextlib.redirect_stdout`

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
    def __init__(self, suppress=True, enabled=True):
        self.text = None
        self._pos = 0  # keep track of how much has been logged
        self.parts = []
        self.started = False
        self.cap_stdout = None
        self.enabled = enabled
        self.suppress = suppress
        self.orig_stdout = sys.stdout

        if suppress:
            redirect = None
        else:
            redirect = self.orig_stdout
        self.cap_stdout = TeeStringIO(redirect)

    def log_part(self):
        """ Log what has been captured so far """
        self.cap_stdout.seek(self._pos)
        text = self.cap_stdout.read()
        self._pos = self.cap_stdout.tell()
        self.parts.append(text)
        self.text = text

    def start(self):
        if self.enabled:
            self.text = ''
            self.started = True
            sys.stdout = self.cap_stdout

    def stop(self):
        """
        Example:
            >>> import ubelt as ub
            >>> ub.CaptureStdout(enabled=False).stop()
            >>> ub.CaptureStdout(enabled=True).stop()
        """
        if self.enabled:
            self.started = False
            sys.stdout = self.orig_stdout

    def __enter__(self):
        self.start()
        return self

    def __del__(self):  # nocover
        if self.started:
            self.stop()
        if self.cap_stdout is not None:
            self.close()

    def close(self):
        self.cap_stdout.close()
        self.cap_stdout = None

    def __exit__(self, type_, value, trace):
        if self.enabled:
            try:
                self.log_part()
            except Exception:  # nocover
                raise
            finally:
                self.stop()
        if trace is not None:
            return False  # return a falsey value on error
