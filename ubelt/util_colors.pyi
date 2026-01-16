NO_COLOR: bool


def highlight_code(text: str,
                   lexer_name: str = 'python',
                   backend: str = 'pygments',
                   **kwargs) -> str:
    ...


def color_text(text: str, color: str) -> str:
    ...
