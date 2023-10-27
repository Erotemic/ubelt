"""
Test if pygments or rich is faster when it comes to highlighting.

Results:
    pygments is a lot faster
"""
import sys
import ubelt as ub
import warnings


def _pygments_highlight(text, lexer_name, **kwargs):
    """
    Original pygments highlight logic
    """
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
    return new_text


def _rich_highlight(text, lexer_name):
    """
    Alternative rich-based highlighter

    References:
        https://github.com/Textualize/rich/discussions/3076
    """
    from rich.syntax import Syntax
    from rich.console import Console
    import io
    syntax = Syntax(text, lexer_name, background_color='default')
    stream = io.StringIO()
    write_console = Console(file=stream, soft_wrap=True, color_system='standard')
    write_console.print(syntax)
    new_text = write_console.file.getvalue()
    return new_text


def main():
    # Benchmark which is faster
    import timerit

    lexer_name = 'python'
    ti = timerit.Timerit(100, bestof=10, verbose=2)

    text = 'import ubelt as ub; print(ub)'
    for timer in ti.reset('small-pygments'):
        pygments_text = _pygments_highlight(text, lexer_name)

    for timer in ti.reset('small-rich'):
        rich_text = _rich_highlight(text, lexer_name)

    print(pygments_text)
    print(rich_text)

    # Use bigger text
    try:
        text = ub.Path(__file__).read_text()
    except NameError:
        text = ub.Path('~/code/ubelt/dev/bench/bench_highlight.py').expand().read_text()

    for timer in ti.reset('big-pygments'):
        pygments_text = _pygments_highlight(text, lexer_name)

    for timer in ti.reset('big-rich'):
        rich_text = _rich_highlight(text, lexer_name)

    print(pygments_text)
    print(rich_text)

    print(ub.urepr(ti.measures['mean'], align=':', precision=8))
    print(ub.urepr(ti.measures['min'], align=':', precision=8))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench/bench_highlight.py
    """
    main()
