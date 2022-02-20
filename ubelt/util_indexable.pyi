from typing import List
from typing import Tuple
from typing import Dict
from collections.abc import Generator
from typing import Any


class IndexableWalker(Generator):
    data: Any
    dict_cls: Any
    list_cls: Any
    indexable_cls: Any

    def __init__(self, data, dict_cls=..., list_cls=...) -> None:
        ...

    def __iter__(self) -> Generator[Tuple[List, Any], Any, Any]:
        ...

    def __next__(self):
        ...

    def send(self, arg) -> None:
        ...

    def throw(self,
              type: Any | None = ...,
              value: Any | None = ...,
              traceback: Any | None = ...) -> None:
        ...

    def __setitem__(self, path: List, value: object) -> None:
        ...

    def __getitem__(self, path: List):
        ...

    def __delitem__(self, path: List) -> None:
        ...


def indexable_allclose(dct1: dict,
                       dct2: dict,
                       rel_tol: float = ...,
                       abs_tol: float = ...,
                       return_info: bool = ...) -> bool | Tuple[bool, Dict]:
    ...
