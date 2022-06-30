from typing import List
from typing import Tuple
from typing import Any
from typing import Dict
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any


class IndexableWalker(Generator):
    data: Incomplete
    dict_cls: Incomplete
    list_cls: Incomplete
    indexable_cls: Incomplete

    def __init__(self, data, dict_cls=..., list_cls=...) -> None:
        ...

    def __iter__(self) -> Generator[Tuple[List, Any], Any, Any]:
        ...

    def __next__(self) -> Any:
        ...

    def send(self, arg) -> None:
        ...

    def throw(self,
              type: Incomplete | None = ...,
              value: Incomplete | None = ...,
              traceback: Incomplete | None = ...) -> None:
        ...

    def __setitem__(self, path: List, value: Any) -> None:
        ...

    def __getitem__(self, path: List) -> Any:
        ...

    def __delitem__(self, path: List) -> None:
        ...


def indexable_allclose(dct1: dict,
                       dct2: dict,
                       rel_tol: float = 1e-09,
                       abs_tol: float = 0.0,
                       return_info: bool = False) -> bool | Tuple[bool, Dict]:
    ...
