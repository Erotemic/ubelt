from typing import List
from os import PathLike
from typing import Dict
from _typeshed import Incomplete

__pitch__: str
POSIX: Incomplete
WIN32: Incomplete


class CmdOutput(dict):

    @property
    def stdout(self):
        ...

    @property
    def stderr(self):
        ...

    @property
    def returncode(self):
        ...

    def check_returncode(self) -> None:
        ...


def cmd(command: str | List[str],
        shell: bool = False,
        detach: bool = False,
        verbose: int = 0,
        tee: bool | None = None,
        cwd: str | PathLike | None = None,
        env: Dict[str, str] | None = None,
        tee_backend: str = 'auto',
        check: bool = False,
        system: bool = False,
        timeout: float | None = None,
        capture: bool = True) -> dict | CmdOutput:
    ...
