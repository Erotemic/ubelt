from typing import Tuple


class NoParamType:

    def __new__(cls) -> NoParamType:
        ...

    def __reduce__(self) -> Tuple[type, Tuple]:
        ...

    def __copy__(self) -> NoParamType:
        ...

    def __deepcopy__(self, memo) -> NoParamType:
        ...

    def __bool__(self) -> bool:
        ...


NoParam: NoParamType
