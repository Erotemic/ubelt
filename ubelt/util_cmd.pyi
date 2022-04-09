from typing import List
from typing import Union
from os import PathLike
from typing import Dict
from typing import Any

POSIX: Any


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
