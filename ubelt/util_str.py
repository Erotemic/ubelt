# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
import codecs
import unicodedata
import textwrap
from six.moves import cStringIO
import six


class CaptureStdout(object):
    r"""
    Context manager that captures stdout and stores it in an internal stream

    Args:
        enabled (bool): (default = True)

    CommandLine:
        python -m ubelt.util_str CaptureStdout

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> self = CaptureStdout(enabled=True)
        >>> print('dont capture the table flip (╯°□°）╯︵ ┻━┻')
        >>> with self:
        >>>     print('capture the heart ♥')
        >>> print('dont capture look of disapproval ಠ_ಠ')
        >>> assert isinstance(self.text, six.text_type)
        >>> assert self.text == 'capture the heart ♥\n', 'failed capture text'
    """
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.orig_stdout = sys.stdout
        self.cap_stdout = cStringIO()
        if six.PY2:
            # http://stackoverflow.com/questions/1817695/stringio-accept-utf8
            import codecs
            codecinfo = codecs.lookup('utf8')
            self.cap_stdout = codecs.StreamReaderWriter(
                self.cap_stdout, codecinfo.streamreader,
                codecinfo.streamwriter)
        self.text = None

    def __enter__(self):
        if self.enabled:
            sys.stdout = self.cap_stdout
        return self

    def __exit__(self, type_, value, trace):
        if self.enabled:
            try:
                self.cap_stdout.seek(0)
                self.text = self.cap_stdout.read()
                if six.PY2:
                    self.text = self.text.decode('utf8')
            except Exception:  # nocover
                pass
            finally:
                self.cap_stdout.close()
                sys.stdout = self.orig_stdout
        if trace is not None:
            return False  # return a falsey value on error


def indent(text, prefix='    '):
    r"""
    Indents a block of text

    Args:
        text (str): text to indent
        prefix (str): prefix to add to each line (default = '    ')

    Returns:
        str: indented text

    CommandLine:
        python -m util_str indent

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> text = 'Lorem ipsum\ndolor sit amet'
        >>> prefix = '    '
        >>> result = indent(text, prefix)
        >>> assert all(t.startswith(prefix) for t in result.split('\n'))
    """
    return prefix + text.replace('\n', '\n' + prefix)


def codeblock(block_str):
    r"""
    Wraps multiline string blocks and returns unindented code.
    Useful for templated code defined in indented parts of code.

    Args:
        block_str (str): typically in the form of a multiline string

    Returns:
        str: the unindented string

    CommandLine:
        python -m ubelt.util_str codeblock

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> # Simulate an indented part of code
        >>> if True:
        >>>     # notice the indentation on this will be normal
        >>>     codeblock_version = codeblock(
        ...             '''
        ...             def foo():
        ...                 return 'bar'
        ...             '''
        ...         )
        >>>     # notice the indentation and newlines on this will be odd
        >>>     normal_version = ('''
        ...         def foo():
        ...             return 'bar'
        ...     ''')
        >>> assert normal_version != codeblock_version
        >>> print('Without codeblock')
        >>> print(normal_version)
        >>> print('With codeblock')
        >>> print(codeblock_version)
    """
    return textwrap.dedent(block_str).strip('\n')


def highlight_code(text, lexer_name='python', **kwargs):
    r"""
    Highlights a block of text using ansii tags based on language syntax.
    If pygments is not installed, the plain text is returned.

    Args:
        text (str): plain text to highlight
        lexer_name (str): name of language
        **kwargs: passed to pygments.lexers.get_lexer_by_name

    CommandLine:
        python -c "import pygments.formatters; print(list(pygments.formatters.get_all_formatters()))"

    Example:
        >>> import ubelt as ub
        >>> text = 'import ubelt as ub; print(ub)'
        >>> new_text = ub.highlight_code(text)
        >>> print(new_text)
    """
    # Resolve extensions to languages
    lexer_name = {
        'py': 'python',
        'h': 'cpp',
        'cpp': 'cpp',
        'cxx': 'cpp',
        'c': 'cpp',
    }.get(lexer_name.replace('.', ''), lexer_name)
    try:
        import pygments
        import pygments.lexers
        import pygments.formatters
        import pygments.formatters.terminal
        formater = pygments.formatters.terminal.TerminalFormatter(bg='dark')
        lexer = pygments.lexers.get_lexer_by_name(lexer_name, **kwargs)
        new_text = pygments.highlight(text, lexer, formater)
    except ImportError:  # nocover
        import warnings
        warnings.warn('pygments is not installed')
        new_text = text
    return new_text


def color_text(text, color):
    """
    Colorizes text a single color using ansii tags.

    Args:
        text (str): text to colorize
        color (str): may be one of the following: yellow, blink, lightgray,
            underline, darkyellow, blue, darkblue, faint, fuchsia, black,
            white, red, brown, turquoise, bold, darkred, darkgreen, reset,
            standout, darkteal, darkgray, overline, purple, green, teal, fuscia

    Returns:
        str: text : colorized text

    CommandLine:
        python -m ubelt.util_str color_text
        python -c "import pygments.console; print(sorted(pygments.console.codes.keys()))"

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> text = 'raw text'
        >>> assert color_text(text, 'red') == '\x1b[31;01mraw text\x1b[39;49;00m'
        >>> assert color_text(text, None) == 'raw text'
    """
    if color is None:
        return text
    try:
        import pygments
        import pygments.console
        ansi_text = pygments.console.colorize(color, text)
        return ansi_text
    except ImportError:  # nocover
        import warnings
        warnings.warn('pygments is not installed')
        return text


def hzcat(args, sep=''):
    """
    Horizontally concatenates strings preserving indentation

    Concats a list of objects ensuring that the next item in the list
    is all the way to the right of any previous items.

    Args:
        args (list): strings to concat
        sep (str): separator (defaults to '')

    CommandLine:
        python -m ubelt.util_str hzcat

    Example1:
        >>> import ubelt as ub
        >>> B = ub.repr2([[1, 2], [3, 457]], nl=1, cbr=True, trailsep=False)
        >>> C = ub.repr2([[5, 6], [7, 8]], nl=1, cbr=True, trailsep=False)
        >>> args = ['A = ', B, ' * ', C]
        >>> print(ub.hzcat(args))
        A = [[1, 2], * [[5, 6],
             [3, 4]]    [7, 8]]

    Example2:
        >>> from ubelt.util_str import *
        >>> import ubelt as ub
        >>> aa = unicodedata.normalize('NFD', 'á')  # a unicode char with len2
        >>> B = ub.repr2([['θ', aa], [aa, aa, aa]], nl=1, cbr=True, trailsep=False)
        >>> C = ub.repr2([[5, 6], [7, 'θ']], nl=1, cbr=True, trailsep=False)
        >>> args = ['A', '=', B, '*', C]
        >>> print(ub.hzcat(args, sep='｜'))
        A｜=｜[['θ', 'á'],     ｜*｜[[5, 6],
         ｜ ｜ ['á', 'á', 'á']]｜ ｜ [7, 'θ']]
    """
    # TODO: ensure unicode data works correctly for python2
    args = [unicodedata.normalize('NFC', ensure_unicode(val)) for val in args]
    arglines = [a.split('\n') for a in args]
    height = max(map(len, arglines))
    # Do vertical padding
    arglines = [lines + [''] * (height - len(lines)) for lines in arglines]
    # Initialize output
    all_lines = ['' for _ in range(height)]
    width = 0
    n_args = len(args)
    for sx, lines in enumerate(arglines):
        # Concatenate the new string
        for lx, line in enumerate(lines):
            all_lines[lx] += line
        # Find the new maximum horiztonal width
        width = max(width, max(map(len, all_lines)))
        if sx < n_args - 1:
            # Horizontal padding on all but last iter
            for lx, line in list(enumerate(all_lines)):
                residual = width - len(line)
                all_lines[lx] = line + (' ' * residual) + sep
            width += len(sep)
    # Clean up trailing whitespace
    all_lines = [line.rstrip(' ') for line in all_lines]
    ret = '\n'.join(all_lines)
    return ret


def ensure_unicode(text):
    """
    Casts bytes into utf8 (mostly for python2 compatibility)

    References:
        http://stackoverflow.com/questions/12561063/python-extract-data-from-file
    """
    if isinstance(text, six.text_type):
        return text
    else:
        try:
            return six.text_type(text)
        except UnicodeDecodeError:
            if text.startswith(codecs.BOM_UTF8):
                # Can safely remove the utf8 marker
                text = text[len(codecs.BOM_UTF8):]
            return text.decode('utf-8')


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_str
        python -m ubelt.util_str all
    """
    import ubelt as ub  # NOQ
    ub.doctest_package()
