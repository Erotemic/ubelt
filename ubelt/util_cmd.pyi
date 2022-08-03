from typing import Union
from typing import List
from os import PathLike
from typing import Dict
from _typeshed import Incomplete

POSIX: Incomplete
WIN32: Incomplete


def cmd(command: Union[str, List[str]],
        shell: bool = False,
        detach: bool = False,
        verbose: int = 0,
        tee: Union[bool, None] = None,
        cwd: Union[str, PathLike, None] = None,
        env: Union[Dict[str, str], None] = None,
        tee_backend: str = 'auto',
        check: bool = False,
        system: bool = False,
        timeout: float = None) -> dict:
    ...
