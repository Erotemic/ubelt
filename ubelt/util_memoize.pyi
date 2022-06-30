from typing import Callable
from _typeshed import Incomplete


def memoize(func: Callable) -> Callable:
    ...


class memoize_method:
    __func__: Incomplete

    def __init__(self, func) -> None:
        ...

    def __get__(self, instance: object, cls: type = None):
        ...

    def __call__(self, *args, **kwargs):
        ...


def memoize_property(fget):
    ...
