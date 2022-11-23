from typing import Union


def schedule_deprecation(modname: str,
                         name: str = ...,
                         type: str = ...,
                         migration: str = ...,
                         deprecate: Union[str, None] = ...,
                         error: Union[str, None] = ...,
                         remove: Union[str, None] = ...,
                         warncls: type = ...,
                         stacklevel: int = ...) -> str:
    ...
