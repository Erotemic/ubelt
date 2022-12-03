from typing import Union
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Any


def identity(arg: Union[Any, None] = None, *args, **kwargs) -> Any:
    ...


def inject_method(self,
                  func: Callable[..., Any],
                  name: Union[str, None] = None) -> None:
    ...


def compatible(config: Dict[str, Any],
               func: Callable,
               start: int = 0,
               keywords: Union[bool, Iterable[str]] = True) -> Dict[str, Any]:
    ...
