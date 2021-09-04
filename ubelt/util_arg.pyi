from typing import Tuple
from typing import Union
from typing import List
from typing import Optional
from typing import TypeVar
from ubelt import util_const

T = TypeVar("T")


def argval(key: Union[str, Tuple[str, ...]],
           default: Union[T, util_const._NoParamType] = ...,
           argv: Optional[List[str]] = ...) -> str | T:
    ...


def argflag(key: Union[str, Tuple[str, ...]], argv: List[str] = ...) -> bool:
    ...
