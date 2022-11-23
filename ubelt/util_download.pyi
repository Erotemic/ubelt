from typing import Optional
import io
from typing import Union
from os import PathLike
from ubelt.util_const import NoParamType
from typing import Dict
import datetime
from typing import TypeVar

Hasher = TypeVar("Hasher")


def download(url: str,
             fpath: Optional[Union[str, PathLike, io.BytesIO]] = ...,
             dpath: Optional[PathLike] = ...,
             fname: Optional[str] = ...,
             appname: str = ...,
             hash_prefix: Union[None, str] = ...,
             hasher: Union[str, Hasher] = ...,
             chunksize: int = ...,
             verbose: Union[int, bool] = ...,
             timeout: Union[float, NoParamType] = ...,
             progkw: Union[Dict, NoParamType] = ...) -> str | PathLike:
    ...


def grabdata(url: str,
             fpath: Optional[Union[str, PathLike]] = ...,
             dpath: Optional[Union[str, PathLike]] = ...,
             fname: Optional[str] = ...,
             redo: bool = ...,
             verbose: int = ...,
             appname: str = ...,
             hash_prefix: Union[None, str] = ...,
             hasher: Union[str, Hasher] = ...,
             expires: Union[str, int, datetime.datetime] = ...,
             **download_kw) -> str | PathLike:
    ...
