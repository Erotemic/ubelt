from typing import List


def indent(text: str, prefix: str = '    ') -> str:
    ...


def codeblock(text: str) -> str:
    ...


def paragraph(text: str) -> str:
    ...


def hzcat(args: List[str], sep: str = ''):
    ...


def ensure_unicode(text: str | bytes) -> str:
    ...
