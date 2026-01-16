from typing import Callable


def memoize(func: Callable) -> Callable:
    ...


class memoize_method:
    __func__: Callable

    def __init__(self, func: Callable) -> None:
        ...

    def __get__(self, instance: object, cls: type | None = None):
        ...

    def __call__(self, *args, **kwargs):
        ...


def memoize_property(fget: property | Callable):
    ...
