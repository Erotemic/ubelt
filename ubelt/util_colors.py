# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals


def highlight_code(text, lexer_name='python', **kwargs):
    r"""
    Highlights a block of text using ansii tags based on language syntax.

    Args:
        text (str): plain text to highlight
        lexer_name (str): name of language
        **kwargs: passed to pygments.lexers.get_lexer_by_name

    Returns:
        str: text : highlighted text
            If pygments is not installed, the plain text is returned.

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
    r"""
    Colorizes text a single color using ansii tags.

    Args:
        text (str): text to colorize
        color (str): may be one of the following: yellow, blink, lightgray,
            underline, darkyellow, blue, darkblue, faint, fuchsia, black,
            white, red, brown, turquoise, bold, darkred, darkgreen, reset,
            standout, darkteal, darkgray, overline, purple, green, teal, fuscia

    Returns:
        str: text : colorized text.
            If pygments is not installed plain text is returned.

    CommandLine:
        python -c "import pygments.console; print(sorted(pygments.console.codes.keys()))"
        python -m ubelt.util_colors color_text

    Example:
        >>> from ubelt.util_colors import *  # NOQA
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

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_colors all
    """
    import ubelt as ub  # NOQ
    xdoc.doctest_module()
