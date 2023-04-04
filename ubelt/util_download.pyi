from typing import Optional
import io
from os import PathLike
from ubelt.util_const import NoParam
from ubelt.util_const import NoParamType
from typing import Dict
import datetime
from typing import TypeVar

Hasher = TypeVar("Hasher")


def download(url: str,
             fpath: Optional[str | PathLike | io.BytesIO] = None,
             dpath: Optional[PathLike] = None,
             fname: Optional[str] = None,
             appname: str | None = None,
             hash_prefix: None | str = None,
             hasher: str | Hasher = 'sha512',
             chunksize: int = 8192,
             filesize: int | None = None,
             verbose: int | bool = 1,
             timeout: float | NoParamType = NoParam,
             progkw: Dict | NoParamType | None = None) -> str | PathLike:
    ...


def grabdata(url: str,
             fpath: Optional[str | PathLike] = None,
             dpath: Optional[str | PathLike] = None,
             fname: Optional[str] = None,
             redo: bool = False,
             verbose: int = 1,
             appname: str | None = None,
             hash_prefix: None | str = None,
             hasher: str | Hasher = 'sha512',
             expires: str | int | datetime.datetime | None = None,
             **download_kw) -> str | PathLike:
    ...
