from typing import Tuple
from typing import List
from typing import Any
from typing import Optional
from types import TracebackType
from typing import Dict
from collections.abc import Generator


class IndexableWalker(Generator):
    data: dict | list | tuple
    dict_cls: Tuple[type]
    list_cls: Tuple[type]
    indexable_cls: Tuple[type]

    def __init__(self, data, dict_cls=..., list_cls=...) -> None:
        ...

    def __iter__(self) -> Generator[Tuple[List, Any], Any, Any]:
        ...

    def __next__(self) -> Any:
        ...

    def send(self, arg) -> None:
        ...

    def throw(self,
              typ: Any,
              val: Optional[object] = None,
              tb: Optional[TracebackType] = None) -> Any:
        ...

    def __setitem__(self, path: List, value: Any) -> None:
        ...

    def __getitem__(self, path: List) -> Any:
        ...

    def __delitem__(self, path: List) -> None:
        ...

    def allclose(self,
                 other: IndexableWalker | List | Dict,
                 rel_tol: float = 1e-09,
                 abs_tol: float = 0.0,
                 return_info: bool = False) -> bool | Tuple[bool, Dict]:
        ...


def indexable_allclose(items1: dict | list | tuple,
                       items2: dict | list | tuple,
                       rel_tol: float = 1e-09,
                       abs_tol: float = 0.0,
                       return_info: bool = False) -> bool | Tuple[bool, Dict]:
    ...
