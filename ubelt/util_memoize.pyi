from typing import Callable
from typing import Any


def memoize(func: Callable) -> Callable:
    ...


class memoize_method:
    im_func: Any
    __func__: Any

    def __init__(self, func) -> None:
        ...

    def __get__(self, instance: object, cls: type = ...):
        ...

    def __call__(self, *args, **kwargs):
        ...


def memoize_property(fget):
    ...
