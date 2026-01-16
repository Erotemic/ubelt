from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable


def identity(arg: Any | None = None, *args, **kwargs) -> Any:
    ...


def inject_method(self,
                  func: Callable[..., Any],
                  name: str | None = None) -> None:
    ...


def compatible(config: Dict[str, Any],
               func: Callable,
               start: int = 0,
               keywords: bool | Iterable[str] = True) -> Dict[str, Any]:
    ...
