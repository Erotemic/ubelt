from typing import List
from typing import Union
from os import PathLike
from typing import Dict
from _typeshed import Incomplete

__pitch__: str
POSIX: Incomplete
WIN32: Incomplete


def cmd(command: Union[str, List[str]],
        shell: bool = ...,
        detach: bool = ...,
        verbose: int = ...,
        tee: Union[bool, None] = ...,
        cwd: Union[str, PathLike, None] = ...,
        env: Union[Dict[str, str], None] = ...,
        tee_backend: str = ...,
        check: bool = ...,
        system: bool = ...,
        timeout: float = ...) -> dict:
    ...
