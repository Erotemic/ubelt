from typing import Tuple
from typing import Union
from ubelt.util_const import NoParamType
from typing import List
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


def argval(key: Union[str, Tuple[str, ...]],
           default: Union[T, NoParamType] = ...,
           argv: Optional[List[str]] = ...) -> str | T:
    ...


def argflag(key: Union[str, Tuple[str, ...]], argv: List[str] = ...) -> bool:
    ...
