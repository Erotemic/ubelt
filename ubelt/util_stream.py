# -*- coding: utf-8 -*-
"""
Functions for capturing and redirecting IO streams.
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
import six
import io
# import codecs
# from six.moves import cStringIO


class TeeStringIO(io.StringIO):
    """
    An IO object that writes to itself and another IO stream.

    Attributes:
        redirect (io.IOBase): The other stream to write to.

    Example:
        >>> redirect = io.StringIO()
        >>> self = TeeStringIO(redirect)
    """
    def __init__(self, redirect=None):
        self.redirect = redirect
        super(TeeStringIO, self).__init__()

    def isatty(self):  # nocover
        """
        Returns true of the redirect is a terminal.

        Notes:
            Needed for IPython.embed to work properly when this class is used
            to override stdout / stderr.
        """
        return (self.redirect is not None and
                hasattr(self.redirect, 'isatty') and self.redirect.isatty())

    @property
    def encoding(self):
        """
        Gets the encoding of the `redirect` IO object

        Doctest:
            >>> redirect = io.StringIO()
            >>> assert TeeStringIO(redirect).encoding is None
            >>> assert TeeStringIO(None).encoding is None
            >>> assert TeeStringIO(sys.stdout).encoding is sys.stdout.encoding
            >>> redirect = io.TextIOWrapper(io.StringIO())
            >>> assert TeeStringIO(redirect).encoding is redirect.encoding
        """
        if self.redirect is not None:
            return self.redirect.encoding
        else:
            return super(TeeStringIO, self).encoding

    def write(self, msg):
        """
        Write to this and the redirected stream
        """
        if self.redirect is not None:
            self.redirect.write(msg)
        if six.PY2:
            from xdoctest.utils.util_str import ensure_unicode
            msg = ensure_unicode(msg)
        super(TeeStringIO, self).write(msg)

    def flush(self):  # nocover
        """
        Flush to this and the redirected stream
        """
        if self.redirect is not None:
            self.redirect.flush()
        super(TeeStringIO, self).flush()


class CaptureStream(object):
    """
    Generic class for capturing streaming output from stdout or stderr
    """


class CaptureStdout(CaptureStream):
    r"""
    Context manager that captures stdout and stores it in an internal stream

    Args:
        supress (bool, default=True):
            if True, stdout is not printed while captured
        enabled (bool, default=True):
            does nothing if this is False

    Example:
        >>> self = CaptureStdout(supress=True)
        >>> print('dont capture the table flip (╯°□°）╯︵ ┻━┻')
        >>> with self:
        ...     text = 'capture the heart ♥'
        ...     print(text)
        >>> print('dont capture look of disapproval ಠ_ಠ')
        >>> assert isinstance(self.text, six.text_type)
        >>> assert self.text == text + '\n', 'failed capture text'

    Example:
        >>> self = CaptureStdout(supress=False)
        >>> with self:
        ...     print('I am captured and printed in stdout')
        >>> assert self.text.strip() == 'I am captured and printed in stdout'

    Example:
        >>> self = CaptureStdout(supress=True, enabled=False)
        >>> with self:
        ...     print('dont capture')
        >>> assert self.text is None
    """
    def __init__(self, supress=True, enabled=True):
        self.enabled = enabled
        self.supress = supress
        self.orig_stdout = sys.stdout
        if supress:
            redirect = None
        else:
            redirect = self.orig_stdout
        self.cap_stdout = TeeStringIO(redirect)
        self.text = None

        self._pos = 0  # keep track of how much has been logged
        self.parts = []
        self.started = False

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
        Doctest:
            >>> CaptureStdout(enabled=False).stop()
            >>> CaptureStdout(enabled=True).stop()
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


# class CaptureStdoutOrig(object):
#     r"""
#     Context manager that captures stdout and stores it in an internal stream

#     Args:
#         enabled (bool): (default = True)

#     CommandLine:
#         python -m ubelt.util_str CaptureStdout

#     TODO:
#         - [ ] use version of this class coded in xdoctest.
#         - [ ] rework to handle stdout, stderr or any other stream.

#     Example:
#         >>> from ubelt.util_str import *  # NOQA
#         >>> self = CaptureStdout(enabled=True)
#         >>> print('dont capture the table flip (╯°□°）╯︵ ┻━┻')
#         >>> with self:
#         >>>     print('capture the heart ♥')
#         >>> print('dont capture look of disapproval ಠ_ಠ')
#         >>> assert isinstance(self.text, six.text_type)
#         >>> assert self.text == 'capture the heart ♥\n', 'failed capture text'
#     """
#     def __init__(self, enabled=True):
#         self.enabled = enabled
#         self.orig_stdout = sys.stdout
#         self.cap_stdout = cStringIO()
#         if six.PY2:
#             # http://stackoverflow.com/questions/1817695/stringio-accept-utf8
#             codecinfo = codecs.lookup('utf8')
#             self.cap_stdout = codecs.StreamReaderWriter(
#                 self.cap_stdout, codecinfo.streamreader,
#                 codecinfo.streamwriter)
#         self.text = None

#     def __enter__(self):
#         if self.enabled:
#             sys.stdout = self.cap_stdout
#         return self

#     def __exit__(self, type_, value, trace):
#         if self.enabled:
#             try:
#                 self.cap_stdout.seek(0)
#                 self.text = self.cap_stdout.read()
#                 if six.PY2:
#                     self.text = self.text.decode('utf8')
#             except Exception:  # nocover
#                 pass
#             finally:
#                 self.cap_stdout.close()
#                 sys.stdout = self.orig_stdout
#         if trace is not None:
#             return False  # return a falsey value on error
