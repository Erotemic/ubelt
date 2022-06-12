from typing import Callable
from typing import Dict
from typing import Any


def identity(arg: Any = None, *args, **kwargs) -> Any:
    ...


def inject_method(self, func: Callable[..., Any], name: str = None) -> None:
    ...


def compatible(config: Dict[str, Any],
               func: Callable,
               start: int = 0) -> Dict[str, Any]:
    ...
