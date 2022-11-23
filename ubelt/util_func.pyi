from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Union
from typing import Any


def identity(arg: Any = ..., *args, **kwargs) -> Any:
    ...


def inject_method(self, func: Callable[..., Any], name: str = ...) -> None:
    ...


def compatible(config: Dict[str, Any],
               func: Callable,
               start: int = ...,
               keywords: Union[bool, Iterable[str]] = ...) -> Dict[str, Any]:
    ...
