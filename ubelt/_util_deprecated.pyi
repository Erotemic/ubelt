from typing import Union
from _typeshed import Incomplete


def schedule_deprecation2(migration: str = ...,
                          name: str = ...,
                          type: str = ...,
                          deprecate: Incomplete | None = ...,
                          error: Incomplete | None = ...,
                          remove: Incomplete | None = ...) -> None:
    ...


def schedule_deprecation(modname: str,
                         name: str = '?',
                         type: str = '?',
                         migration: str = '',
                         deprecate: Union[str, None] = None,
                         error: Union[str, None] = None,
                         remove: Union[str, None] = None) -> None:
    ...
