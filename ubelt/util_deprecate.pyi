from typing import Union


def schedule_deprecation(modname: str,
                         name: str = '?',
                         type: str = '?',
                         migration: str = '',
                         deprecate: Union[str, None] = None,
                         error: Union[str, None] = None,
                         remove: Union[str, None] = None,
                         warncls: type = DeprecationWarning) -> None:
    ...
