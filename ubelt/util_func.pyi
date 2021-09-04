from typing import Callable
from typing import Dict
from typing import Any


def identity(arg: object = ..., *args, **kwargs) -> object:
    ...


def inject_method(self, func: Callable[..., Any], name: str = ...) -> None:
    ...


def compatible(config: Dict[str, Any],
               func: Callable,
               start: int = ...) -> Dict[str, Any]:
    ...
