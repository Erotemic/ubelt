from os import PathLike
from typing import Type
from types import TracebackType
from types import ModuleType
from typing import List
from typing import Tuple

IS_PY_GE_308: bool


class PythonPathContext:
    dpath: str | PathLike
    index: int

    def __init__(self, dpath: str | PathLike, index: int = 0) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...


def import_module_from_path(modpath: str | PathLike,
                            index: int = ...) -> ModuleType:
    ...


def import_module_from_name(modname: str) -> ModuleType:
    ...


def modname_to_modpath(
        modname: str,
        hide_init: bool = True,
        hide_main: bool = False,
        sys_path: None | List[str | PathLike] = None) -> str | None:
    ...


def normalize_modpath(modpath: str | PathLike,
                      hide_init: bool = True,
                      hide_main: bool = False) -> str | PathLike:
    ...


def modpath_to_modname(modpath: str,
                       hide_init: bool = True,
                       hide_main: bool = False,
                       check: bool = True,
                       relativeto: str | None = None) -> str:
    ...


def split_modpath(modpath: str, check: bool = True) -> Tuple[str, str]:
    ...


def is_modname_importable(modname: str,
                          sys_path: list | None = None,
                          exclude: list | None = None) -> bool:
    ...
