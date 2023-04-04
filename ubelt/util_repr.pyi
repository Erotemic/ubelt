from typing import Type
from typing import Tuple
from typing import Callable


def urepr(data: object, **kwargs) -> str:
    ...


class ReprExtensions:

    def __init__(self) -> None:
        ...

    def register(self, key: Type | Tuple[Type] | str) -> Callable:
        ...

    def lookup(self, data):
        ...
