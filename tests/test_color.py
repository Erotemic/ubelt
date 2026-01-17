def test_unable_to_find_color():
    import ubelt as ub
    import pytest
    if ub.util_colors.NO_COLOR:
        pytest.skip()

    with pytest.warns(UserWarning):
        text = ub.color_text('text', 'wizbang')
        assert text == 'text', 'bad colors should pass the text back'


def test_global_color_disable():
    """
    CommandLine:
        xdoctest -m /home/joncrall/code/ubelt/tests/test_color.py test_global_color_disable
    """
    import ubelt as ub
    import pytest

    if ub.util_colors.NO_COLOR:
        pytest.skip()

    text = 'text = "hi"'

    has_color = ub.color_text(text, 'red') != ub.color_text(text, None)

    text1a = ub.color_text(text, 'red')
    text1b = ub.highlight_code(text)
    if has_color:
        assert text != text1a
        assert text != text1b

    # Force colors to be disabled
    prev = ub.util_colors.NO_COLOR

    try:
        ub.util_colors.NO_COLOR = True

        text2a = ub.color_text(text, 'red')
        text2b = ub.highlight_code(text)
        assert text == text2a
        assert text == text2b
    finally:
        # Re-enable coloration
        ub.util_colors.NO_COLOR = prev

    text3a = ub.color_text(text, 'red')
    text3b = ub.highlight_code(text)
    if has_color:
        assert text != text3a
        assert text != text3b


def test_highlight_code_pygments_backend(monkeypatch):
    import types
    import sys
    import ubelt as ub
    import pytest

    prev_no_color = ub.util_colors.NO_COLOR
    monkeypatch.setattr(ub.util_colors, 'NO_COLOR', False)

    pygments = types.ModuleType('pygments')
    def highlight(text, lexer, formatter):
        return f'highlight:{text}'
    pygments.highlight = highlight

    lexers = types.ModuleType('pygments.lexers')
    def get_lexer_by_name(name, **kwargs):
        return ('lexer', name)
    lexers.get_lexer_by_name = get_lexer_by_name

    formatters = types.ModuleType('pygments.formatters')
    terminal = types.ModuleType('pygments.formatters.terminal')
    class TerminalFormatter:
        def __init__(self, bg='dark'):
            self.bg = bg
    terminal.TerminalFormatter = TerminalFormatter

    monkeypatch.setitem(sys.modules, 'pygments', pygments)
    monkeypatch.setitem(sys.modules, 'pygments.lexers', lexers)
    monkeypatch.setitem(sys.modules, 'pygments.formatters', formatters)
    monkeypatch.setitem(sys.modules, 'pygments.formatters.terminal', terminal)

    text = 'print("hello")'
    highlighted = ub.highlight_code(text, backend='pygments')
    assert highlighted == f'highlight:{text}'
    monkeypatch.setattr(ub.util_colors, 'NO_COLOR', prev_no_color)


def test_color_text_missing_color_warns(monkeypatch):
    import types
    import sys
    import ubelt as ub
    import pytest

    prev_no_color = ub.util_colors.NO_COLOR
    monkeypatch.setattr(ub.util_colors, 'NO_COLOR', False)

    pygments = types.ModuleType('pygments')
    console = types.ModuleType('pygments.console')
    def colorize(color, text):
        raise KeyError(color)
    console.colorize = colorize
    pygments.console = console

    monkeypatch.setitem(sys.modules, 'pygments', pygments)
    monkeypatch.setitem(sys.modules, 'pygments.console', console)

    with pytest.warns(UserWarning):
        assert ub.color_text('text', 'missing') == 'text'
    monkeypatch.setattr(ub.util_colors, 'NO_COLOR', prev_no_color)


def test_highlight_code_rich_backend(monkeypatch):
    import types
    import sys
    import ubelt as ub

    monkeypatch.setattr(ub.util_colors, 'NO_COLOR', False)

    rich_syntax = types.ModuleType('rich.syntax')
    class Syntax:
        def __init__(self, text, lexer_name, background_color='default'):
            self.text = text
    rich_syntax.Syntax = Syntax

    rich_console = types.ModuleType('rich.console')
    class Console:
        def __init__(self, file, soft_wrap=True, color_system='standard'):
            self.file = file
        def print(self, syntax):
            self.file.write(syntax.text)
    rich_console.Console = Console

    monkeypatch.setitem(sys.modules, 'rich.syntax', rich_syntax)
    monkeypatch.setitem(sys.modules, 'rich.console', rich_console)

    text = 'print("rich")'
    highlighted = ub.highlight_code(text, backend='rich')
    assert highlighted == text
