def schedule_deprecation(modname: str,
                         name: str = '?',
                         type: str = '?',
                         migration: str = '',
                         deprecate: str | None = None,
                         error: str | None = None,
                         remove: str | None = None,
                         warncls: type = DeprecationWarning,
                         stacklevel: int = 1) -> str:
    ...
