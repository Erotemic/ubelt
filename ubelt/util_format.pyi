from typing import Type
from typing import Tuple
from typing import Union
from typing import Callable


def urepr(data: object, **kwargs) -> str:
    ...


def repr2(data, **kwargs):
    ...


class FormatterExtensions:

    def __init__(self) -> None:
        ...

    def register(self, key: Union[Type, Tuple[Type], str]) -> Callable:
        ...

    def lookup(self, data):
        ...
