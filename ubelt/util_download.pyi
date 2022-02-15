from typing import Optional
import io
from typing import Union
from os import PathLike
from typing import Dict
from typing import TypeVar

Hasher = TypeVar("Hasher")


def download(url: str,
             fpath: Optional[Union[str, PathLike, io.BytesIO]] = ...,
             dpath: Optional[PathLike] = ...,
             fname: Optional[str] = ...,
             hash_prefix: Union[None, str] = ...,
             hasher: Union[str, Hasher] = ...,
             chunksize: int = ...,
             verbose: int = ...,
             timeout: float = ...,
             progkw: Union[Dict, None] = ...) -> str | PathLike:
    ...


def grabdata(url: str,
             fpath: Optional[Union[str, PathLike]] = ...,
             dpath: Optional[Union[str, PathLike]] = ...,
             fname: Optional[str] = ...,
             redo: bool = ...,
             verbose: bool = ...,
             appname: str = ...,
             hash_prefix: Union[None, str] = ...,
             hasher: Union[str, Hasher] = ...,
             **download_kw) -> str | PathLike:
    ...
