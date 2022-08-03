from typing import Union
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
             fpath: Optional[Union[str, PathLike, io.BytesIO]] = None,
             dpath: Optional[PathLike] = None,
             fname: Optional[str] = None,
             appname: str = None,
             hash_prefix: Union[None, str] = None,
             hasher: Union[str, Hasher] = 'sha512',
             chunksize: int = 8192,
             verbose: Union[int, bool] = 1,
             timeout: Union[float, NoParamType] = NoParam,
             progkw: Union[Dict, NoParamType] = None) -> str | PathLike:
    ...


def grabdata(url: str,
             fpath: Optional[Union[str, PathLike]] = None,
             dpath: Optional[Union[str, PathLike]] = None,
             fname: Optional[str] = None,
             redo: bool = False,
             verbose: int = 1,
             appname: str = None,
             hash_prefix: Union[None, str] = None,
             hasher: Union[str, Hasher] = 'sha512',
             expires: Union[str, int, datetime.datetime] = None,
             **download_kw) -> str | PathLike:
    ...
