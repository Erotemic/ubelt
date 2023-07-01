from typing import Type
from typing import Tuple
from typing import Callable
from typing import Any


def urepr(data: object, **kwargs) -> str:
    ...


class ReprExtensions:

    def __init__(self) -> None:
        ...

    def register(self, key: Type | Tuple[Type] | str) -> Callable:
        ...

    def lookup(self, data: Any) -> Callable:
        ...
