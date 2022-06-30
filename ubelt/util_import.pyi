from typing import Union
from os import PathLike
from types import ModuleType
from typing import List
from typing import Tuple
from _typeshed import Incomplete


class PythonPathContext:
    dpath: Incomplete
    index: Incomplete

    def __init__(self, dpath, index: int = ...) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, type, value, trace) -> None:
        ...


def import_module_from_path(modpath: Union[str, PathLike],
                            index: int = ...) -> ModuleType:
    ...


def import_module_from_name(modname: str) -> ModuleType:
    ...


def modname_to_modpath(
        modname: str,
        hide_init: bool = True,
        hide_main: bool = False,
        sys_path: Union[None, List[Union[str,
                                         PathLike]]] = None) -> str | None:
    ...


def normalize_modpath(modpath: Union[str, PathLike],
                      hide_init: bool = True,
                      hide_main: bool = False) -> str | PathLike:
    ...


def modpath_to_modname(modpath: str,
                       hide_init: bool = True,
                       hide_main: bool = False,
                       check: bool = True,
                       relativeto: str = None) -> str:
    ...


def split_modpath(modpath: str, check: bool = True) -> Tuple[str, str]:
    ...


def is_modname_importable(modname: str,
                          sys_path: list = None,
                          exclude: list = None) -> bool:
    ...
