# -*- coding: utf-8 -*-
"""
This module defines simple functions to color your text and highlight your code
using `ANSI <https://en.wikipedia.org/wiki/ANSI_escape_code#Colors>`_ escape
sequences.  This works using the  `Pygments <http://pygments.org/>`_  library,
which is an optional requirement. Therefore, these functions only work properly
if Pygments is installed, otherwise these functions will return the unmodified
text and a warning will be printed.

The :func:`highlight_code` function uses pygments to highlight syntax of a programing
language.

The :func:`color_text` function colors text with a solid color.

Note the functions in this module require the optional :mod:`pygments`
library to work correctly. These functions will warn if :mod:`pygments` is
not installed.


Notes:
    In the future we may rename this module to ``util_ansi``.

Requirements:
    pip install pygments
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import sys


def highlight_code(text, lexer_name='python', **kwargs):
    """
    Highlights a block of text using ANSI tags based on language syntax.

    Args:
        text (str): plain text to highlight
        lexer_name (str): name of language. eg: python, docker, c++
        **kwargs: passed to pygments.lexers.get_lexer_by_name

    Returns:
        str: text - highlighted text
            If pygments is not installed, the plain text is returned.

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

        if sys.platform.startswith('win32'):  # nocover
            # Hack on win32 to support colored output
            import colorama
            colorama.init()

        formater = pygments.formatters.terminal.TerminalFormatter(bg='dark')
        lexer = pygments.lexers.get_lexer_by_name(lexer_name, **kwargs)
        new_text = pygments.highlight(text, lexer, formater)

    except ImportError:  # nocover
        import warnings
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
        str: text - colorized text.
            If pygments is not installed plain text is returned.

    Example:
        >>> text = 'raw text'
        >>> import pytest
        >>> import ubelt as ub
        >>> if ub.modname_to_modpath('pygments'):
        >>>     # Colors text only if pygments is installed
        >>>     ansi_text = ub.ensure_unicode(color_text(text, 'red'))
        >>>     prefix = ub.ensure_unicode('\x1b[31')
        >>>     print('prefix = {!r}'.format(prefix))
        >>>     print('ansi_text = {!r}'.format(ansi_text))
        >>>     assert ansi_text.startswith(prefix)
        >>>     assert color_text(text, None) == 'raw text'
        >>> else:
        >>>     # Otherwise text passes through unchanged
        >>>     assert color_text(text, 'red') == 'raw text'
        >>>     assert color_text(text, None) == 'raw text'
    """
    if color is None:
        return text
    try:
        import pygments
        import pygments.console

        if sys.platform.startswith('win32'):  # nocover
            # Hack on win32 to support colored output
            import colorama
            colorama.init()

        try:
            ansi_text = pygments.console.colorize(color, text)
        except KeyError:
            import warnings
            warnings.warn('unable to find color: {!r}'.format(color))
            return text
        except Exception as ex:  # nocover
            import warnings
            warnings.warn('some other issue with text color: {!r}'.format(ex))
            return text
        return ansi_text
    except ImportError:  # nocover
        import warnings
        warnings.warn('pygments is not installed, text will not be colored')
        return text
