from typing import Any


class PythonPathContext:
    dpath: Any
    index: Any

    def __init__(self, dpath, index: int = ...) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, type, value, trace) -> None:
        ...


def import_module_from_path(modpath, index: int = ...):
    ...


def import_module_from_name(modname):
    ...


def modname_to_modpath(modname,
                       hide_init: bool = ...,
                       hide_main: bool = ...,
                       sys_path: Any | None = ...):
    ...


def normalize_modpath(modpath, hide_init: bool = ..., hide_main: bool = ...):
    ...


def modpath_to_modname(modpath,
                       hide_init: bool = ...,
                       hide_main: bool = ...,
                       check: bool = ...,
                       relativeto: Any | None = ...):
    ...


def split_modpath(modpath, check: bool = ...):
    ...


def is_modname_importable(modname,
                          sys_path: Any | None = ...,
                          exclude: Any | None = ...):
    ...
