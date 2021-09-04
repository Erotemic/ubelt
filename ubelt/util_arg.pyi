from typing import Tuple
from typing import Union
from typing import Optional
from typing import List


def argval(key: Union[str, Tuple[str, ...]],
           default: object = ...,
           argv: Optional[list] = ...) -> str:
    ...


def argflag(key: Union[str, Tuple[str, ...]], argv: List[str] = ...) -> bool:
    ...
