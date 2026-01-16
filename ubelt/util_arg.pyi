from typing import Tuple
from ubelt.util_const import NoParamType
from typing import List
from typing import TypeVar

T = TypeVar("T")


def argval(key: str | Tuple[str, ...],
           default: T | NoParamType = ...,
           argv: List[str] | None = None) -> str | T:
    ...


def argflag(key: str | Tuple[str, ...], argv: List[str] | None = None) -> bool:
    ...
