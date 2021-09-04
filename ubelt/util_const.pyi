from typing import Any


class _NoParamType:
    def __new__(cls):
        ...

    def __reduce__(self):
        ...

    def __copy__(self):
        ...

    def __deepcopy__(self, memo):
        ...

    def __bool__(self):
        ...

    __nonzero__: Any


NoParam: _NoParamType
