from typing import List
from typing import Tuple
from typing import Dict
from typing import Union
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

    def allclose(self,
                 other: IndexableWalker,
                 rel_tol: float = ...,
                 abs_tol: float = ...,
                 return_info: bool = ...) -> bool | Tuple[bool, Dict]:
        ...


def indexable_allclose(items1: Union[dict, list, tuple],
                       items2: Union[dict, list, tuple],
                       rel_tol: float = ...,
                       abs_tol: float = ...,
                       return_info: bool = ...) -> bool | Tuple[bool, Dict]:
    ...
