"""
This module defines simple functions to color your text and highlight your code
using `ANSI <https://en.wikipedia.org/wiki/ANSI_escape_code#Colors>`_ escape
sequences.  This works using the  `Pygments <http://pygments.org/>`_  library,
which is an optional requirement. Therefore, these functions only work properly
if Pygments is installed, otherwise these functions will return the unmodified
text and a warning will be printed.

The :func:`highlight_code` function uses pygments to highlight syntax of a
programming language.

The :func:`color_text` function colors text with a solid color.

Note the functions in this module require the optional :mod:`pygments`
library to work correctly. These functions will warn if :mod:`pygments` is
not installed.


This module contains a global variable ``NO_COLOR``, which if set to True will
force all ANSI text coloring functions to become no-ops. This defaults to the
value of the ``bool(os.environ.get('NO_COLOR'))`` flag, which is compliant with
[NoColor]_.


Related work:
    https://github.com/Textualize/rich

References:
    .. [NoColor] https://no-color.org/

Requirements:
    pip install pygments
"""
import sys
import warnings
import os


# Global state that determines if ANSI-coloring text is allowed
# (which is mainly to address non-ANSI compliant windows consoles)
# compliant with https://no-color.org/
NO_COLOR = bool(os.environ.get('NO_COLOR'))  # type: bool


def highlight_code(text, lexer_name='python', **kwargs):
    """
    Highlights a block of text using ANSI tags based on language syntax.

    Args:
        text (str): plain text to highlight
        lexer_name (str): name of language. eg: python, docker, c++
        **kwargs: passed to pygments.lexers.get_lexer_by_name

    Returns:
        str:
            text - highlighted text If pygments is not installed, the plain
            text is returned.

    Example:
        >>> import ubelt as ub
        >>> text = 'import ubelt as ub; print(ub)'
        >>> new_text = ub.highlight_code(text)
        >>> print(new_text)
    """
    if NO_COLOR:
        return text
    # Resolve extensions to languages
    lexer_name = {
        'py': 'python',
        'h': 'cpp',
        'cpp': 'cpp',
        'cxx': 'cpp',
        'c': 'cpp',
    }.get(lexer_name.replace('.', ''), lexer_name)
    try:

        if sys.platform.startswith('win32'):  # nocover
            # Hack on win32 to support colored output
            try:
                import colorama
                if not colorama.initialise.atexit_done:
                    # Only init if it hasn't been done
                    colorama.init()
            except ImportError:
                warnings.warn(
                    'colorama is not installed, ansi colors may not work')

        import pygments  # type: ignore
        import pygments.lexers  # type: ignore
        import pygments.formatters  # type: ignore
        import pygments.formatters.terminal  # type: ignore

        formatter = pygments.formatters.terminal.TerminalFormatter(bg='dark')
        lexer = pygments.lexers.get_lexer_by_name(lexer_name, **kwargs)
        new_text = pygments.highlight(text, lexer, formatter)

    except ImportError:  # nocover
        warnings.warn('pygments is not installed, code will not be highlighted')
        new_text = text
    return new_text


def color_text(text, color):
    r"""
    Colorizes text a single color using ansi tags.

    Args:
        text (str): text to colorize

        color (str): color code. different systems may have different colors.
            commonly available colors are: 'red', 'brown', 'yellow', 'green',
            'blue', 'black', and 'white'.

    Returns:
        str:
            text - colorized text.  If pygments is not installed plain text is
            returned.

    Example:
        >>> text = 'raw text'
        >>> import pytest
        >>> import ubelt as ub
        >>> if ub.modname_to_modpath('pygments'):
        >>>     # Colors text only if pygments is installed
        >>>     ansi_text = ub.color_text(text, 'red')
        >>>     prefix = '\x1b[31'
        >>>     print('prefix = {!r}'.format(prefix))
        >>>     print('ansi_text = {!r}'.format(ansi_text))
        >>>     assert ansi_text.startswith(prefix)
        >>>     assert ub.color_text(text, None) == 'raw text'
        >>> else:
        >>>     # Otherwise text passes through unchanged
        >>>     assert ub.color_text(text, 'red') == 'raw text'
        >>>     assert ub.color_text(text, None) == 'raw text'

    Example:
        >>> # xdoctest: +REQUIRES(module:pygments)
        >>> import pygments.console
        >>> import ubelt as ub
        >>> known_colors = pygments.console.codes.keys()
        >>> for color in known_colors:
        ...     print(ub.color_text(color, color))
    """
    if NO_COLOR or color is None:
        return text
    try:

        if sys.platform.startswith('win32'):  # nocover
            # Hack on win32 to support colored output
            try:
                import colorama
                if not colorama.initialise.atexit_done:
                    # Only init if it hasn't been done
                    colorama.init()
            except ImportError:
                warnings.warn(
                    'colorama is not installed, ansi colors may not work')

        import pygments  # type: ignore
        import pygments.console  # type: ignore
        try:
            ansi_text = pygments.console.colorize(color, text)
        except KeyError:
            warnings.warn('unable to find color: {!r}'.format(color))
            return text
        except Exception as ex:  # nocover
            warnings.warn('some other issue with text color: {!r}'.format(ex))
            return text
        return ansi_text
    except ImportError:  # nocover
        warnings.warn('pygments is not installed, text will not be colored')
        return text
